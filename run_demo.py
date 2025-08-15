#!/usr/bin/env python3
"""
KrishiSetu Demo Runner
A simple demo to test the agricultural AI advisor system without requiring API keys.
"""

import asyncio
import json
from datetime import datetime

def run_offline_demo():
    """Run an offline demo showing the system structure"""
    print("🌾 KrishiSetu - Agricultural AI Advisor")
    print("=" * 50)
    print("Offline Demo Mode (No API Keys Required)")
    print()
    
    # Show system architecture
    print("🏗️ System Architecture:")
    print("• Multi-Agent System with CrewAI")
    print("• Weather Agent - Irrigation & Weather Analysis")
    print("• Crop Agent - Crop Selection & Management")
    print("• Finance Agent - Loans & Government Schemes")
    print("• MCP Integration - External Data Sources")
    print("• FastAPI - High-performance Web API")
    print()
    
    # Show supported features
    print("🚀 Key Features:")
    print("• Multilingual Support (10 Indian Languages)")
    print("• Real-time Weather Data Integration")
    print("• Government Scheme Information")
    print("• Market Price Analysis")
    print("• Crop Suitability Assessment")
    print("• Financial Advisory Services")
    print()
    
    # Show example queries
    print("💬 Example Queries:")
    queries = [
        "When should I irrigate my wheat crop?",
        "क्या आज बारिश होगी? (Will it rain today?)",
        "Which crop should I plant this season?",
        "What loans are available for farmers?",
        "Tell me about PM-KISAN scheme",
        "மழை எப்போது பெய்யும்? (When will it rain?)"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"{i}. {query}")
    print()
    
    # Show API endpoints
    print("🔌 Available API Endpoints:")
    endpoints = [
        "POST /query - Process agricultural queries",
        "POST /query/weather - Weather-specific queries",
        "POST /query/crop - Crop-specific queries", 
        "POST /query/finance - Finance-specific queries",
        "GET /agents - List available AI agents",
        "GET /examples - Get example queries",
        "GET /supported-languages - List supported languages"
    ]
    
    for endpoint in endpoints:
        print(f"• {endpoint}")
    print()
    
    # Show sample response
    print("📊 Sample Response Structure:")
    sample_response = {
        "success": True,
        "data": {
            "current_weather": {
                "temperature": 28.5,
                "humidity": 65,
                "description": "partly cloudy"
            },
            "irrigation_recommendation": {
                "recommendation": "Moderate irrigation recommended",
                "priority": "Medium",
                "next_irrigation": "Within 48 hours"
            },
            "crop_recommendations": [
                {
                    "name": "Rice",
                    "varieties": ["IR64", "Swarna"],
                    "suitability_score": 85
                }
            ],
            "financial_options": [
                {
                    "name": "Kisan Credit Card",
                    "interest_rate": "7.0%",
                    "max_amount": "₹3,00,000"
                }
            ]
        },
        "confidence": 0.85,
        "source": "Agricultural Crew",
        "timestamp": datetime.now().isoformat()
    }
    
    print(json.dumps(sample_response, indent=2))
    print()
    
    # Show setup instructions
    print("⚙️ Setup Instructions:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Set up environment variables in .env file")
    print("3. Get API keys for OpenAI, Tavily, and Weather APIs")
    print("4. Run: python main.py")
    print("5. Access API at: http://localhost:8000")
    print("6. View docs at: http://localhost:8000/docs")
    print()
    
    print("🎯 Ready to revolutionize Indian agriculture!")
    print("For full functionality, please set up API keys and run the complete system.")

def show_installation_guide():
    """Show detailed installation guide"""
    print("📦 Installation Guide")
    print("=" * 30)
    print()
    
    print("1. Clone the repository:")
    print("   git clone <repository-url>")
    print("   cd KrishiSetu")
    print()
    
    print("2. Create virtual environment:")
    print("   python -m venv venv")
    print("   source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
    print()
    
    print("3. Install dependencies:")
    print("   pip install -r requirements.txt")
    print()
    
    print("4. Set up environment variables:")
    print("   cp .env.example .env")
    print("   # Edit .env with your API keys")
    print()
    
    print("5. Required API Keys:")
    print("   • OpenAI API Key (for LLM agents)")
    print("   • Tavily API Key (for web search)")
    print("   • OpenWeatherMap API Key (for weather data)")
    print()
    
    print("6. Run the application:")
    print("   python main.py")
    print()
    
    print("7. Test the system:")
    print("   python examples/demo_queries.py")
    print()

def main():
    """Main function"""
    print("Choose an option:")
    print("1. View System Demo")
    print("2. Installation Guide")
    print("3. Exit")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        run_offline_demo()
    elif choice == "2":
        show_installation_guide()
    elif choice == "3":
        print("Goodbye! 🌾")
    else:
        print("Invalid choice. Running demo...")
        run_offline_demo()

if __name__ == "__main__":
    main() 