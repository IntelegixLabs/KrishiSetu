#!/usr/bin/env python3
"""
KrishiSetu - Agricultural AI Advisor
A comprehensive AI-powered agricultural advisory system using multi-agent architecture.

This system provides:
- Weather analysis and irrigation recommendations
- Crop selection and management advice
- Financial guidance and government scheme information
- Multilingual support for Indian farmers
- Real-time data integration through MCP
"""

import asyncio
import uvicorn
from fastapi import FastAPI
from api.main import app
from config import Config
from models.database import create_tables

def main():
    """Main entry point for the KrishiSetu application"""
    print("🌾 KrishiSetu - Agricultural AI Advisor")
    print("=" * 50)
    print("Starting up the agricultural advisory system...")
    
    # Initialize database
    create_tables()
    print("✅ Database initialized")
    
    # Start the FastAPI server
    print(f"🚀 Starting server on {Config.HOST}:{Config.PORT}")
    uvicorn.run(
        "api.main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG,
        log_level="info"
    )

if __name__ == "__main__":
    main() 