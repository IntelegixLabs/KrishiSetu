import io
import os
import tempfile
import re
from typing import List, Tuple, Dict, Optional
from enum import Enum

from fastapi import UploadFile

try:
    from markitdown import MarkItDown  # type: ignore
except Exception as e:  # pragma: no cover
    MarkItDown = None  # type: ignore


SUPPORTED_SUFFIXES = {
    ".pdf",
    ".doc",
    ".docx",
    ".ppt",
    ".pptx",
    ".xls",
    ".xlsx",
    ".csv",
    ".txt",
    ".md",
}


class DocumentType(Enum):
    """Types of agricultural documents"""
    SOIL_REPORT = "soil_report"
    CROP_REPORT = "crop_report"
    WEATHER_REPORT = "weather_report"
    IRRIGATION_REPORT = "irrigation_report"
    FINANCIAL_REPORT = "financial_report"
    IRRELEVANT = "irrelevant"
    UNKNOWN = "unknown"


class FileValidationResult:
    """Result of file validation"""
    def __init__(self, is_relevant: bool, document_type: DocumentType, 
                 confidence: float, reason: str, filename: str):
        self.is_relevant = is_relevant
        self.document_type = document_type
        self.confidence = confidence
        self.reason = reason
        self.filename = filename


def detect_document_type(filename: str, content: str) -> FileValidationResult:
    """
    Detect if uploaded document is relevant to agriculture and determine its type.
    
    Args:
        filename: Name of the uploaded file
        content: Extracted text content from the file
        
    Returns:
        FileValidationResult with document type and relevance information
    """
    # Convert to lowercase for case-insensitive matching
    filename_lower = filename.lower() if filename else ""
    content_lower = content.lower() if content else ""
    
    # Check for extraction errors first
    if "[extraction error]" in content_lower:
        return FileValidationResult(
            is_relevant=False,
            document_type=DocumentType.UNKNOWN,
            confidence=0.0,
            reason="File extraction failed - unable to read content",
            filename=filename
        )
    
    # Keywords for different document types
    soil_keywords = [
        "soil", "ph", "nitrogen", "phosphorus", "potassium", "organic matter",
        "soil test", "soil analysis", "soil report", "nutrient", "fertility",
        "conductivity", "micronutrient", "macronutrient", "carbon", "humus",
        "soil health", "soil texture", "clay", "sand", "silt", "cation exchange",
        "मिट्टी", "पीएच", "नाइट्रोजन", "फास्फोरस", "पोटेशियम", "जैविक पदार्थ"
    ]
    
    crop_keywords = [
        "crop", "yield", "harvest", "seed", "variety", "cultivation", "planting",
        "farming", "agriculture", "rice", "wheat", "cotton", "sugarcane", "maize",
        "corn", "barley", "soybean", "tomato", "potato", "onion", "growth stage",
        "crop report", "production", "farm", "field", "plantation", "cultivation",
        "फसल", "उत्पादन", "बीज", "खेती", "चावल", "गेहूं", "कपास", "मकई"
    ]
    
    weather_keywords = [
        "weather", "temperature", "rainfall", "humidity", "wind", "forecast",
        "climate", "precipitation", "drought", "flood", "monsoon", "weather report",
        "meteorological", "atmospheric", "seasonal", "मौसम", "बारिश", "तापमान"
    ]
    
    irrigation_keywords = [
        "irrigation", "water", "watering", "drip", "sprinkler", "flood irrigation",
        "water management", "irrigation schedule", "moisture", "water requirement",
        "सिंचाई", "पानी", "जल प्रबंधन"
    ]
    
    financial_keywords = [
        "finance", "loan", "credit", "bank", "scheme", "subsidy", "insurance",
        "cost", "profit", "investment", "market price", "income", "expense",
        "budget", "financial report", "ऋण", "वित्त", "योजना", "सब्सिडी"
    ]
    
    # Irrelevant keywords that indicate non-agricultural documents
    irrelevant_keywords = [
        "marksheet", "mark sheet", "grade", "score", "percentage", "student",
        "school", "college", "university", "education", "degree", "certificate",
        "transcript", "academic", "examination", "test result", "semester",
        "birth certificate", "passport", "driver license", "id card", "aadhar",
        "pan card", "voter id", "medical report", "health checkup", "blood test",
        "x-ray", "prescription", "medicine", "hospital", "doctor", "patient",
        "invoice", "bill", "receipt", "shopping", "purchase", "order", "delivery",
        "अंकतालिका", "प्रमाण पत्र", "पासपोर्ट", "चिकित्सा रिपोर्ट"
    ]
    
    # Count keyword matches
    def count_keywords(text: str, keywords: List[str]) -> int:
        return sum(1 for keyword in keywords if keyword in text)
    
    # Count matches in both filename and content
    text_to_analyze = f"{filename_lower} {content_lower}"
    
    soil_count = count_keywords(text_to_analyze, soil_keywords)
    crop_count = count_keywords(text_to_analyze, crop_keywords)
    weather_count = count_keywords(text_to_analyze, weather_keywords)
    irrigation_count = count_keywords(text_to_analyze, irrigation_keywords)
    financial_count = count_keywords(text_to_analyze, financial_keywords)
    irrelevant_count = count_keywords(text_to_analyze, irrelevant_keywords)
    
    # Check for clearly irrelevant documents first
    if irrelevant_count > 2:
        return FileValidationResult(
            is_relevant=False,
            document_type=DocumentType.IRRELEVANT,
            confidence=0.8,
            reason="Document appears to be non-agricultural (contains educational, medical, or other irrelevant content)",
            filename=filename
        )
    
    # Determine document type based on keyword counts
    counts = {
        DocumentType.SOIL_REPORT: soil_count,
        DocumentType.CROP_REPORT: crop_count,
        DocumentType.WEATHER_REPORT: weather_count,
        DocumentType.IRRIGATION_REPORT: irrigation_count,
        DocumentType.FINANCIAL_REPORT: financial_count
    }
    
    # Find the type with highest count
    max_count = max(counts.values())
    
    # If no significant agricultural keywords found
    if max_count < 2:
        # Check if it has any minimal agricultural context
        basic_agri_keywords = ["farm", "farmer", "agriculture", "agricultural", "किसान", "खेत"]
        basic_count = count_keywords(text_to_analyze, basic_agri_keywords)
        
        if basic_count > 0:
            return FileValidationResult(
                is_relevant=True,
                document_type=DocumentType.UNKNOWN,
                confidence=0.3,
                reason="Document has minimal agricultural context but type unclear",
                filename=filename
            )
        else:
            return FileValidationResult(
                is_relevant=False,
                document_type=DocumentType.IRRELEVANT,
                confidence=0.7,
                reason="No significant agricultural content found in the document",
                filename=filename
            )
    
    # Find document type with highest score
    document_type = max(counts, key=counts.get)
    confidence = min(0.9, max_count / 10.0)  # Cap at 0.9, scale based on keyword count
    
    # Generate reason based on detected type
    type_reasons = {
        DocumentType.SOIL_REPORT: f"Soil-related content detected (found {soil_count} soil indicators)",
        DocumentType.CROP_REPORT: f"Crop-related content detected (found {crop_count} crop indicators)",
        DocumentType.WEATHER_REPORT: f"Weather-related content detected (found {weather_count} weather indicators)",
        DocumentType.IRRIGATION_REPORT: f"Irrigation-related content detected (found {irrigation_count} irrigation indicators)",
        DocumentType.FINANCIAL_REPORT: f"Financial/scheme-related content detected (found {financial_count} financial indicators)"
    }
    
    return FileValidationResult(
        is_relevant=True,
        document_type=document_type,
        confidence=confidence,
        reason=type_reasons[document_type],
        filename=filename
    )


def _guess_suffix(filename: str) -> str:
    filename_lower = (filename or "").lower()
    for ext in SUPPORTED_SUFFIXES:
        if filename_lower.endswith(ext):
            return ext
    return os.path.splitext(filename_lower)[1] or ".txt"


async def extract_texts_from_uploads(files: List[UploadFile]) -> List[Tuple[str, str]]:
    """Extract (filename, markdown_text) for each uploaded file using MarkItDown.

    Writes files to a temporary location to let MarkItDown handle various formats.
    Returns a list of (original_filename, extracted_markdown_text).
    """

    if not files:
        return []

    if MarkItDown is None:
        raise RuntimeError("markitdown is not installed. Please install markitdown[all].")

    md = MarkItDown()
    results: List[Tuple[str, str]] = []

    for f in files:
        try:
            suffix = _guess_suffix(f.filename or "")
            # Persist to a temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                content = await f.read()
                tmp.write(content)
                tmp_path = tmp.name

            converted = md.convert(tmp_path)
            text = getattr(converted, "text_content", "") or ""
            results.append((f.filename or os.path.basename(tmp_path), text))
        except Exception as e:  # Continue processing other files
            results.append((f.filename or "unknown", f"[Extraction error] {e}"))
        finally:
            try:
                if tmp_path and os.path.exists(tmp_path):
                    os.unlink(tmp_path)
            except Exception:
                pass

    return results


