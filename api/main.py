from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, UploadFile, File, Form
from fastapi.responses import StreamingResponse
import io
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import re
import asyncio
import json
from datetime import datetime

from crew.agricultural_crew import AgriculturalCrew
from models.database import create_tables, get_db
from config import Config
from utils.reporting import (
    build_report_dict,
    build_csv_bytes,
    build_excel_bytes,
    build_pdf_bytes,
)
from utils.document_parser import extract_texts_from_uploads, detect_document_type, DocumentType, FileValidationResult
from openai import OpenAI
from schema import AgriculturalAnalysis

# Create FastAPI app
app = FastAPI(
    title="KrishiSetu - Agricultural AI Advisor",
    description="AI-powered agricultural advisory system using multi-agent architecture",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agricultural crew with error handling
try:
    agricultural_crew = AgriculturalCrew()
    crew_available = True
except Exception as e:
    print(f"Warning: Agricultural crew initialization failed: {e}")
    agricultural_crew = None
    crew_available = False

# Pydantic models for request/response
class QueryRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None
    comprehensive: bool = False
    language: str = "en"

class QueryResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    confidence: float
    source: str
    timestamp: str

class UserProfile(BaseModel):
    phone_number: str
    language: str = "en"
    location: Optional[str] = None
    farmer_type: Optional[str] = "small"
    land_area: Optional[float] = 2.0
    state: Optional[str] = "Maharashtra"

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    crew_status: str

class ReportRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None
    comprehensive: bool = True
    language: str = "en"
    format: str = "csv"  # csv | excel | pdf

class ChatResponse(BaseModel):
    success: bool
    analysis: AgriculturalAnalysis
    # raw_documents: Optional[List[Dict[str, Any]]] = None
    # timestamp: str

@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup"""
    create_tables()
    print("KrishiSetu Agricultural AI Advisor started successfully!")

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
        crew_status="available" if crew_available else "unavailable"
    )

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process agricultural queries using AI agents"""
    try:
        if not crew_available:
            raise HTTPException(status_code=503, detail="Agricultural crew is not available")
        
        if request.comprehensive:
            # Use full crew for comprehensive analysis
            result = await agricultural_crew.process_comprehensive_query(
                request.query, 
                request.context
            )
        else:
            # Use single most relevant agent
            result = await agricultural_crew.process_simple_query(
                request.query, 
                request.context
            )
        
        # Add timestamp
        result["timestamp"] = datetime.now().isoformat()
        
        return QueryResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/report")
async def generate_report(request: ReportRequest):
    """Generate an agriculture report in CSV, Excel, or PDF."""
    try:
        if not crew_available:
            raise HTTPException(status_code=503, detail="Agricultural crew is not available")

        # Get analysis result
        if request.comprehensive:
            result = await agricultural_crew.process_comprehensive_query(
                request.query,
                request.context,
            )
        else:
            result = await agricultural_crew.process_simple_query(
                request.query,
                request.context,
            )

        # Build normalized report data
        report_dict = build_report_dict(
            request.query,
            request.context or {},
            result,
            request.language,
        )

        fmt = (request.format or "csv").lower()
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")

        if fmt == "csv":
            data_bytes = build_csv_bytes(report_dict)
            media_type = "text/csv"
            filename = f"krishisetu_report_{ts}.csv"
        elif fmt in ("xlsx", "excel"):
            data_bytes = build_excel_bytes(report_dict)
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = f"krishisetu_report_{ts}.xlsx"
        elif fmt == "pdf":
            data_bytes = build_pdf_bytes(report_dict)
            media_type = "application/pdf"
            filename = f"krishisetu_report_{ts}.pdf"
        else:
            raise HTTPException(status_code=400, detail="Invalid format. Use csv, excel, or pdf.")

        return StreamingResponse(
            io.BytesIO(data_bytes),
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
async def chat_route(
    text: str = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    language: str = Form("en"),
):
    """Accept text and optional documents (pdf, csv, docx, xlsx, etc),
    detect document type, validate agricultural relevance, analyze with OpenAI, 
    and return a structured agricultural report with rainy season recommendations.
    """
    try:
        # Check if no files were uploaded
        if not files or len(files) == 0:
            # Provide analysis based on text only with appropriate message
            sys_prompt = (
                "You are an agricultural expert. The user has not attached any files. "
                "Analyze their text query and provide general agricultural advice. "
                "Include a note about 'no files attached' in your summary."
            )
            
            format_instructions = (
                "Output STRICT JSON only (no markdown, no code fences). The JSON MUST match this schema: "
                "{ soil: { type, ph:{average,range}, moisture_percentage:{average,range}, organic_carbon_percentage:{average,range}, "
                "nutrients:{ nitrogen_kg_per_ha:{average,range}, phosphorus_kg_per_ha:{average,range}, potassium_kg_per_ha:{average,range} } }, "
                "crop:{ types: string[], season: string, growth_stages: string[] }, "
                "weather:{ temperature_c:{average,range}, humidity_pct:{average,range}, rainfall_mm:{ last_24h:{average,range}, forecast_24h:{average,range} }, wind_speed_mps:{average,range} }, "
                "finance:{ market_price_inr_per_quintal:{average,range}, market_trend: string, applicable_schemes: string[] }, "
                "risks:{ pest_risk:{ average: string, notable_risks: string[] }, irrigation_need:{ average: string, specific_needs: string[] } }, "
                "recommendations:{ irrigation:{ general: string, specific: [{crop:string, action:string}] }, crop_management:{ general: string, specific: [{crop:string, action:string}] } }, "
                "summary: string }"
            )
            
            user_block = f"User Input: {text}\n\nNote: No files were attached. Please provide general agricultural advice and mention 'no files attached' in the summary."
            
            # Call OpenAI for text-only analysis
            client = OpenAI()
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "system", "content": format_instructions},
                    {"role": "user", "content": user_block},
                ],
                temperature=0.4,
            )
            
            content = completion.choices[0].message.content if completion.choices else "{}"
            
        else:
            # Extract documents and validate them
            extracted: List[Dict[str, Any]] = []
            validation_results: List[FileValidationResult] = []
            relevant_documents: List[Dict[str, Any]] = []
            
            # Process each uploaded file
            pairs = await extract_texts_from_uploads(files)
            for name, content in pairs:
                extracted.append({"filename": name, "content": content})
                
                # Validate document type and relevance
                validation = detect_document_type(name, content)
                validation_results.append(validation)
                
                if validation.is_relevant:
                    relevant_documents.append({
                        "filename": name, 
                        "content": content,
                        "document_type": validation.document_type.value,
                        "confidence": validation.confidence
                    })
            
            # Check if any relevant documents were found
            if not relevant_documents:
                # All uploaded files are irrelevant
                irrelevant_files = [v.filename for v in validation_results if not v.is_relevant]
                error_reasons = [v.reason for v in validation_results if not v.is_relevant]
                
                # Create a response indicating irrelevant files
                fallback_analysis = {
                    "soil": {
                        "type": "unknown",
                        "ph": {"average": 0.0, "range": "0.0-0.0"},
                        "moisture_percentage": {"average": 0.0, "range": "0.0-0.0"},
                        "organic_carbon_percentage": {"average": 0.0, "range": "0.0-0.0"},
                        "nutrients": {
                            "nitrogen_kg_per_ha": {"average": 0.0, "range": "0.0-0.0"},
                            "phosphorus_kg_per_ha": {"average": 0.0, "range": "0.0-0.0"},
                            "potassium_kg_per_ha": {"average": 0.0, "range": "0.0-0.0"}
                        }
                    },
                    "crop": {
                        "types": [],
                        "season": "unknown",
                        "growth_stages": []
                    },
                    "weather": {
                        "temperature_c": {"average": 0.0, "range": "0.0-0.0"},
                        "humidity_pct": {"average": 0.0, "range": "0.0-0.0"},
                        "rainfall_mm": {
                            "last_24h": {"average": 0.0, "range": "0.0-0.0"},
                            "forecast_24h": {"average": 0.0, "range": "0.0-0.0"}
                        },
                        "wind_speed_mps": {"average": 0.0, "range": "0.0-0.0"}
                    },
                    "finance": {
                        "market_price_inr_per_quintal": {"average": 0.0, "range": "0.0-0.0"},
                        "market_trend": "unknown",
                        "applicable_schemes": []
                    },
                    "risks": {
                        "pest_risk": {
                            "average": "unknown",
                            "notable_risks": []
                        },
                        "irrigation_need": {
                            "average": "unknown",
                            "specific_needs": []
                        }
                    },
                    "recommendations": {
                        "irrigation": {
                            "general": "Please upload relevant agricultural documents (soil reports, crop reports) for specific recommendations.",
                            "specific": []
                        },
                        "crop_management": {
                            "general": "Upload agricultural documents for detailed crop management advice.",
                            "specific": []
                        }
                    },
                    "summary": f"Unable to find relevant agricultural files. The uploaded files ({', '.join(irrelevant_files)}) appear to be non-agricultural documents. Please upload soil reports, crop reports, or other agricultural documents for analysis. Detected issues: {'; '.join(error_reasons)}"
                }
                
                try:
                    analysis_model = AgriculturalAnalysis.model_validate(fallback_analysis)
                    return ChatResponse(success=False, analysis=analysis_model)
                except Exception as e:
                    raise HTTPException(status_code=422, detail=f"Error creating irrelevant file response: {e}")
            
            # Compose enhanced prompt based on detected document types
            detected_types = [doc["document_type"] for doc in relevant_documents]
            type_summary = ", ".join(set(detected_types))
            
            sys_prompt = (
                f"You are an agricultural expert. The user has uploaded {type_summary} documents. "
                "Analyze the user's request and the attached agricultural documents to produce "
                "a structured, practical, and clinically accurate advisory report. "
                "Focus on rainy season recommendations based on the document type and content."
            )
            
            # Add specific instructions based on document types found
            rainy_season_context = ""
            if DocumentType.SOIL_REPORT.value in detected_types:
                rainy_season_context += "For soil reports: Focus on drainage, nutrient leaching prevention, and soil conservation during monsoon. "
            if DocumentType.CROP_REPORT.value in detected_types:
                rainy_season_context += "For crop reports: Emphasize water management, pest control during humidity, and harvest timing. "
            if DocumentType.WEATHER_REPORT.value in detected_types:
                rainy_season_context += "For weather data: Provide irrigation scheduling and flood/drought preparation advice. "
            if DocumentType.IRRIGATION_REPORT.value in detected_types:
                rainy_season_context += "For irrigation data: Optimize water usage during monsoon and suggest drainage improvements. "
            if DocumentType.FINANCIAL_REPORT.value in detected_types:
                rainy_season_context += "For financial data: Include monsoon insurance and weather-related scheme recommendations. "
            
            format_instructions = (
                "Output STRICT JSON only (no markdown, no code fences). The JSON MUST match this schema: "
                "{ soil: { type, ph:{average,range}, moisture_percentage:{average,range}, organic_carbon_percentage:{average,range}, "
                "nutrients:{ nitrogen_kg_per_ha:{average,range}, phosphorus_kg_per_ha:{average,range}, potassium_kg_per_ha:{average,range} } }, "
                "crop:{ types: string[], season: string, growth_stages: string[] }, "
                "weather:{ temperature_c:{average,range}, humidity_pct:{average,range}, rainfall_mm:{ last_24h:{average,range}, forecast_24h:{average,range} }, wind_speed_mps:{average,range} }, "
                "finance:{ market_price_inr_per_quintal:{average,range}, market_trend: string, applicable_schemes: string[] }, "
                "risks:{ pest_risk:{ average: string, notable_risks: string[] }, irrigation_need:{ average: string, specific_needs: string[] } }, "
                "recommendations:{ irrigation:{ general: string, specific: [{crop:string, action:string}] }, crop_management:{ general: string, specific: [{crop:string, action:string}] } }, "
                "summary: string }"
                f"\n\nRainy season focus: {rainy_season_context}"
            )

            doc_block = "\n\n".join([
                f"FILE: {d['filename']} (Type: {d['document_type']}, Confidence: {d['confidence']:.2f})\n"
                f"CONTENT:\n{d['content'][:8000]}" 
                for d in relevant_documents
            ])
            
            user_block = f"User Input:\n{text}\n\nAgricultural Documents:\n{doc_block}"

            # Call OpenAI with enhanced context
            client = OpenAI()
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "system", "content": format_instructions},
                    {"role": "user", "content": user_block},
                ],
                temperature=0.4,
            )

            content = completion.choices[0].message.content if completion.choices else "{}"

        # Extract pure JSON from model output (strip code fences if present)
        def extract_json(text: str) -> str:
            if not text:
                return "{}"
            fence_match = re.search(r"```(?:json)?\n([\s\S]*?)```", text, re.IGNORECASE)
            if fence_match:
                return fence_match.group(1).strip()
            # If looks like JSON already
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and end > start:
                return text[start:end + 1]
            return text

        json_text = extract_json(content)

        try:
            raw_obj = json.loads(json_text)
        except Exception:
            # As a final fallback, wrap in summary
            raw_obj = {"summary": content}

        # Validate and coerce using schema
        try:
            analysis_model = AgriculturalAnalysis.model_validate(raw_obj)
        except Exception as e:
            # If validation fails, raise a 422-like error with message for debugging
            raise HTTPException(status_code=422, detail=f"Response did not match schema: {e}")

        return ChatResponse(
            success=True,
            analysis=analysis_model,
            # raw_documents=extracted,
            # timestamp=datetime.now().isoformat(),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query/weather")
async def weather_query(request: QueryRequest):
    """Process weather-specific queries"""
    try:
        from agents import WeatherAgent
        weather_agent = WeatherAgent()
        result = weather_agent.process_query(request.query, request.context)
        result["timestamp"] = datetime.now().isoformat()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query/crop")
async def crop_query(request: QueryRequest):
    """Process crop-specific queries"""
    try:
        from agents import CropAgent
        crop_agent = CropAgent()
        result = crop_agent.process_query(request.query, request.context)
        result["timestamp"] = datetime.now().isoformat()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query/finance")
async def finance_query(request: QueryRequest):
    """Process finance-specific queries"""
    try:
        from agents import FinanceAgent
        finance_agent = FinanceAgent()
        result = finance_agent.process_query(request.query, request.context)
        result["timestamp"] = datetime.now().isoformat()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents")
async def list_agents():
    """List available AI agents"""
    return {
        "agents": [
            {
                "name": "Weather Agent",
                "description": "Provides weather analysis and irrigation recommendations",
                "capabilities": ["Weather forecasting", "Irrigation advice", "Soil moisture analysis"],
                "keywords": ["weather", "irrigation", "temperature", "rain", "humidity"]
            },
            {
                "name": "Crop Agent",
                "description": "Provides crop selection and management advice",
                "capabilities": ["Crop recommendations", "Market analysis", "Pest management"],
                "keywords": ["crop", "seed", "harvest", "pest", "fertilizer"]
            },
            {
                "name": "Finance Agent",
                "description": "Provides financial advice and government scheme information",
                "capabilities": ["Loan options", "Government schemes", "Market trends"],
                "keywords": ["loan", "credit", "scheme", "subsidy", "insurance"]
            }
        ],
        "crew_status": "available" if crew_available else "unavailable"
    }

@app.get("/supported-languages")
async def get_supported_languages():
    """Get list of supported languages"""
    return {
        "languages": Config.SUPPORTED_LANGUAGES,
        "default": "en"
    }

@app.get("/crops")
async def get_available_crops():
    """Get list of major crops supported"""
    return {
        "crops": Config.MAJOR_CROPS,
        "seasons": ["Kharif", "Rabi", "Zaid"]
    }

@app.get("/soil-types")
async def get_soil_types():
    """Get list of soil types in India"""
    return {
        "soil_types": Config.SOIL_TYPES
    }

@app.post("/user/profile")
async def create_user_profile(profile: UserProfile):
    """Create or update user profile"""
    try:
        db = next(get_db())
        # This would typically save to database
        # For now, return success response
        return {
            "success": True,
            "message": "User profile created successfully",
            "user_id": "user_123"  # This would be the actual user ID
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/examples")
async def get_example_queries():
    """Get example queries for different categories"""
    return {
        "weather_queries": [
            "When should I irrigate my wheat crop?",
            "What's the weather forecast for next week?",
            "Is it going to rain today?",
            "क्या आज बारिश होगी?",
            "मेरी गेहूं की फसल को कब सिंचाई करनी चाहिए?"
        ],
        "crop_queries": [
            "Which crop should I plant this season?",
            "What are the best rice varieties for my area?",
            "How to control pests in cotton?",
            "इस मौसम में कौन सी फसल लगानी चाहिए?",
            "मेरे क्षेत्र के लिए सबसे अच्छे चावल की किस्में कौन सी हैं?"
        ],
        "finance_queries": [
            "What loans are available for farmers?",
            "Tell me about PM-KISAN scheme",
            "How to get crop insurance?",
            "किसानों के लिए कौन से ऋण उपलब्ध हैं?",
            "PM-KISAN योजना के बारे में बताएं"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG
    ) 