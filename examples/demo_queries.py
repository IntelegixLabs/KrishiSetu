#!/usr/bin/env python3
"""
KrishiSetu Demo Queries
Example queries to demonstrate the agricultural AI advisor system capabilities.
"""

import asyncio
import json
from datetime import datetime
from crew.agricultural_crew import AgriculturalCrew
from utils.language_processor import LanguageProcessor

class KrishiSetuDemo:
    """Demo class to showcase KrishiSetu capabilities"""
    
    def __init__(self):
        self.crew = AgriculturalCrew()
        self.language_processor = LanguageProcessor()
    
    async def run_demo(self):
        """Run the complete demo"""
        print("🌾 KrishiSetu Agricultural AI Advisor - Demo")
        print("=" * 60)
        
        # Demo queries in different languages and categories
        demo_queries = [
            # Weather queries
            {
                "query": "When should I irrigate my wheat crop?",
                "context": {"location": "Mumbai", "crop_type": "Wheat"},
                "category": "Weather",
                "language": "English"
            },
            {
                "query": "क्या आज बारिश होगी?",
                "context": {"location": "Delhi"},
                "category": "Weather",
                "language": "Hindi"
            },
            {
                "query": "மழை எப்போது பெய்யும்?",
                "context": {"location": "Chennai"},
                "category": "Weather",
                "language": "Tamil"
            },
            
            # Crop queries
            {
                "query": "Which crop should I plant this season?",
                "context": {"location": "Punjab", "soil_type": "Alluvial", "season": "Kharif"},
                "category": "Crop",
                "language": "English"
            },
            {
                "query": "इस मौसम में कौन सी फसल लगानी चाहिए?",
                "context": {"location": "Maharashtra", "soil_type": "Black", "season": "Rabi"},
                "category": "Crop",
                "language": "Hindi"
            },
            {
                "query": "எந்த பயிர் நடவு செய்ய வேண்டும்?",
                "context": {"location": "Tamil Nadu", "soil_type": "Red", "season": "Kharif"},
                "category": "Crop",
                "language": "Tamil"
            },
            
            # Finance queries
            {
                "query": "What loans are available for farmers?",
                "context": {"farmer_type": "small", "land_area": 2.0, "state": "Maharashtra"},
                "category": "Finance",
                "language": "English"
            },
            {
                "query": "किसानों के लिए कौन से ऋण उपलब्ध हैं?",
                "context": {"farmer_type": "medium", "land_area": 5.0, "state": "Punjab"},
                "category": "Finance",
                "language": "Hindi"
            },
            {
                "query": "Tell me about PM-KISAN scheme",
                "context": {"farmer_type": "small", "state": "Karnataka"},
                "category": "Finance",
                "language": "English"
            }
        ]
        
        for i, demo in enumerate(demo_queries, 1):
            print(f"\n🔍 Demo {i}: {demo['category']} Query ({demo['language']})")
            print("-" * 50)
            print(f"Query: {demo['query']}")
            print(f"Context: {demo['context']}")
            
            # Process the query
            result = await self.process_demo_query(demo)
            
            # Display results
            self.display_results(result)
            
            # Wait between queries
            await asyncio.sleep(2)
    
    async def process_demo_query(self, demo):
        """Process a demo query"""
        try:
            # Language processing
            processed = self.language_processor.process_query(demo['query'])
            
            # Merge context
            context = {**demo['context'], **processed}
            
            # Process with crew
            result = await self.crew.process_comprehensive_query(
                demo['query'], 
                context
            )
            
            return {
                "success": True,
                "processed": processed,
                "result": result,
                "demo_info": demo
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "demo_info": demo
            }
    
    def display_results(self, result):
        """Display demo results in a formatted way"""
        if not result["success"]:
            print(f"❌ Error: {result['error']}")
            return
        
        demo = result["demo_info"]
        processed = result["processed"]
        crew_result = result["result"]
        
        print(f"\n📊 Language Detection: {processed['detected_language'].upper()}")
        print(f"🎯 Query Type: {processed['query_type'].title()}")
        print(f"📍 Location: {processed['location']}")
        print(f"🌱 Crop: {processed['crop']}")
        print(f"🔑 Keywords: {', '.join(processed['keywords'][:5])}")
        
        # Display agent insights
        if "agent_insights" in crew_result.get("data", {}):
            insights = crew_result["data"]["agent_insights"]
            print(f"\n🤖 Agent Insights:")
            
            for agent_type, insight in insights.items():
                if insight.get("success"):
                    confidence = insight.get("confidence", 0)
                    print(f"  • {agent_type.title()}: {confidence:.2f} confidence")
        
        # Display recommendations
        if "recommendations" in crew_result.get("data", {}):
            recommendations = crew_result["data"]["recommendations"]
            print(f"\n💡 Recommendations:")
            
            for category, items in recommendations.items():
                if items:
                    print(f"  • {category.replace('_', ' ').title()}:")
                    for item in items[:2]:  # Show first 2 items
                        print(f"    - {item}")
        
        # Overall confidence
        confidence = crew_result.get("confidence", 0)
        print(f"\n🎯 Overall Confidence: {confidence:.2f}")
    
    async def run_simple_demo(self):
        """Run a simple demo with basic queries"""
        print("🌾 KrishiSetu - Simple Demo")
        print("=" * 40)
        
        simple_queries = [
            "When should I irrigate?",
            "Which crop is best for my area?",
            "What government schemes are available?",
            "क्या आज बारिश होगी?",
            "कौन सी फसल लगानी चाहिए?"
        ]
        
        for query in simple_queries:
            print(f"\n❓ Query: {query}")
            
            # Language processing
            processed = self.language_processor.process_query(query)
            print(f"🔍 Detected: {processed['detected_language']} | Type: {processed['query_type']}")
            
            # Simple processing
            result = await self.crew.process_simple_query(query, processed)
            
            if result.get("success"):
                confidence = result.get("confidence", 0)
                source = result.get("source", "Unknown")
                print(f"✅ Response: {confidence:.2f} confidence from {source}")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
            
            await asyncio.sleep(1)

async def main():
    """Main demo function"""
    demo = KrishiSetuDemo()
    
    print("Choose demo type:")
    print("1. Simple Demo (quick overview)")
    print("2. Comprehensive Demo (full features)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        await demo.run_simple_demo()
    else:
        await demo.run_comprehensive_demo()

if __name__ == "__main__":
    asyncio.run(main()) 