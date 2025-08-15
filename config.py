import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Tavily API for web search
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    
    # Weather API
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
    
    # Database Configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./krishisetu.db")
    
    # Application Configuration
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    
    # MCP Configuration
    MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:3000")
    
    # Agricultural Data Sources
    WEATHER_BASE_URL = "http://api.openweathermap.org/data/2.5"
    CROP_CALENDAR_API = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
    SOIL_HEALTH_API = "https://api.data.gov.in/resource/3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69"
    
    # Supported Languages for Indian Agriculture
    SUPPORTED_LANGUAGES = ["en", "hi", "ta", "te", "bn", "mr", "gu", "kn", "ml", "pa"]
    
    # Crop Types for India
    MAJOR_CROPS = [
        "Rice", "Wheat", "Maize", "Cotton", "Sugarcane", "Pulses", 
        "Oilseeds", "Vegetables", "Fruits", "Spices"
    ]
    
    # Soil Types in India
    SOIL_TYPES = [
        "Alluvial", "Black", "Red", "Laterite", "Mountain", "Desert", "Saline"
    ] 