from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import asyncio
import json
from datetime import datetime

from crew.agricultural_crew import AgriculturalCrew
from models.database import create_tables, get_db
from config import Config

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

# Initialize agricultural crew
agricultural_crew = AgriculturalCrew()

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
        version="1.0.0"
    )

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process agricultural queries using AI agents"""
    try:
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
        ]
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