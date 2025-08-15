import requests
import json
from typing import Dict, Any, List
from datetime import datetime
from .base_agent import BaseAgent
from config import Config

class CropAgent(BaseAgent):
    """Agent specialized in crop selection and management recommendations"""
    
    def __init__(self):
        super().__init__(
            name="Crop Specialist",
            role="Agricultural Crop Expert",
            goal="Provide optimal crop selection and management advice based on local conditions"
        )
    
    def _get_backstory(self) -> str:
        return """You are a senior agricultural scientist with expertise in crop science, 
        soil management, and agricultural economics. You have worked across different 
        agro-climatic zones in India and understand the specific requirements of various 
        crops. You provide evidence-based recommendations for crop selection, timing, 
        and management practices that maximize yield and profitability."""
    
    def _get_tools(self) -> List:
        # Return empty list to avoid tool validation issues
        return []
    
    def _get_keywords(self) -> List[str]:
        return [
            "crop", "seed", "variety", "planting", "harvest", "yield", "pest",
            "disease", "fertilizer", "soil", "season", "market", "price",
            "फसल", "बीज", "किस्म", "रोपण", "फसल काटना", "उपज", "कीट",
            "रोग", "खाद", "मिट्टी", "मौसम", "बाजार", "कीमत"
        ]
    
    def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process crop-related queries"""
        try:
            # Extract parameters from context
            location = context.get('location', 'Mumbai') if context else 'Mumbai'
            soil_type = context.get('soil_type', 'Alluvial')
            season = context.get('season', 'Kharif')
            budget = context.get('budget', 'medium')
            
            # Get crop recommendations
            recommendations = self.get_crop_recommendations(location, soil_type, season)
            
            # Analyze suitability
            suitability_analysis = self.analyze_crop_suitability(recommendations, context)
            
            # Get market prices
            market_data = self.get_market_prices(recommendations)
            
            # Get crop calendar
            calendar = self.get_crop_calendar(season)
            
            response = {
                "recommendations": recommendations,
                "suitability_analysis": suitability_analysis,
                "market_data": market_data,
                "crop_calendar": calendar,
                "timestamp": datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "data": response,
                "confidence": self.get_confidence_score(query),
                "source": "Crop Agent"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "confidence": 0.0,
                "source": "Crop Agent"
            }
    
    def get_crop_recommendations(self, location: str, soil_type: str, season: str) -> List[Dict[str, Any]]:
        """Get crop recommendations based on location, soil, and season"""
        # This would typically integrate with agricultural databases
        # For now, using a simplified recommendation system
        
        crop_database = {
            "Kharif": {
                "Alluvial": [
                    {"name": "Rice", "varieties": ["IR64", "Swarna", "Pusa Basmati"], "duration": 120, "water_need": "High"},
                    {"name": "Maize", "varieties": ["Hybrid Maize", "Sweet Corn"], "duration": 90, "water_need": "Medium"},
                    {"name": "Cotton", "varieties": ["BT Cotton", "Desi Cotton"], "duration": 150, "water_need": "Medium"}
                ],
                "Black": [
                    {"name": "Soybean", "varieties": ["JS-335", "JS-9305"], "duration": 100, "water_need": "Medium"},
                    {"name": "Groundnut", "varieties": ["TMV-2", "JL-24"], "duration": 110, "water_need": "Low"}
                ]
            },
            "Rabi": {
                "Alluvial": [
                    {"name": "Wheat", "varieties": ["HD-2967", "PBW-343"], "duration": 140, "water_need": "Medium"},
                    {"name": "Mustard", "varieties": ["Pusa Bold", "RH-30"], "duration": 120, "water_need": "Low"}
                ],
                "Black": [
                    {"name": "Chickpea", "varieties": ["JG-11", "Pusa-372"], "duration": 130, "water_need": "Low"},
                    {"name": "Lentil", "varieties": ["PL-406", "PL-639"], "duration": 110, "water_need": "Low"}
                ]
            }
        }
        
        return crop_database.get(season, {}).get(soil_type, [])
    
    def analyze_crop_suitability(self, crops: List[Dict], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze crop suitability based on various factors"""
        analysis = {}
        
        for crop in crops:
            score = 0
            factors = []
            
            # Weather compatibility
            if context.get('temperature', 25) < 35:
                score += 20
                factors.append("Favorable temperature")
            
            # Water availability
            if context.get('water_availability', 'medium') == 'high':
                score += 25
                factors.append("Good water availability")
            elif crop['water_need'] == 'Low':
                score += 20
                factors.append("Low water requirement")
            
            # Market demand
            if context.get('market_demand', 'medium') == 'high':
                score += 25
                factors.append("High market demand")
            
            # Pest resistance
            if context.get('pest_pressure', 'low') == 'low':
                score += 15
                factors.append("Low pest pressure")
            
            # Profitability
            if context.get('budget', 'medium') == 'high':
                score += 15
                factors.append("High budget for inputs")
            
            analysis[crop['name']] = {
                "suitability_score": min(score, 100),
                "factors": factors,
                "recommendation": "Highly Recommended" if score >= 80 else "Recommended" if score >= 60 else "Moderate"
            }
        
        return analysis
    
    def get_market_prices(self, crops: List[Dict]) -> Dict[str, Any]:
        """Get current market prices for recommended crops"""
        # This would integrate with real-time market data APIs
        # For now, using sample data
        
        price_data = {
            "Rice": {"current_price": 1800, "unit": "per quintal", "trend": "Stable"},
            "Wheat": {"current_price": 2100, "unit": "per quintal", "trend": "Rising"},
            "Maize": {"current_price": 1500, "unit": "per quintal", "trend": "Stable"},
            "Cotton": {"current_price": 5500, "unit": "per quintal", "trend": "Falling"},
            "Soybean": {"current_price": 3200, "unit": "per quintal", "trend": "Rising"},
            "Groundnut": {"current_price": 4800, "unit": "per quintal", "trend": "Stable"},
            "Mustard": {"current_price": 4200, "unit": "per quintal", "trend": "Rising"},
            "Chickpea": {"current_price": 3800, "unit": "per quintal", "trend": "Stable"},
            "Lentil": {"current_price": 5200, "unit": "per quintal", "trend": "Rising"}
        }
        
        return {crop['name']: price_data.get(crop['name'], {"current_price": 0, "unit": "per quintal", "trend": "Unknown"}) 
                for crop in crops}
    
    def get_crop_calendar(self, season: str) -> Dict[str, Any]:
        """Get crop calendar for the season"""
        calendars = {
            "Kharif": {
                "planting_start": "June",
                "planting_end": "August",
                "harvest_start": "September",
                "harvest_end": "November",
                "key_activities": ["Land preparation", "Seed treatment", "Planting", "Weeding", "Pest control"]
            },
            "Rabi": {
                "planting_start": "October",
                "planting_end": "December",
                "harvest_start": "March",
                "harvest_end": "May",
                "key_activities": ["Land preparation", "Seed treatment", "Planting", "Irrigation", "Fertilization"]
            }
        }
        
        return calendars.get(season, {})
    
    def analyze_pest_risks(self, crop_name: str, location: str) -> Dict[str, Any]:
        """Analyze pest risks for specific crops"""
        # This would integrate with pest monitoring systems
        pest_data = {
            "Rice": ["Rice stem borer", "Rice leaf folder", "Brown plant hopper"],
            "Wheat": ["Aphids", "Termites", "Rust diseases"],
            "Cotton": ["Bollworm", "Aphids", "Whitefly"],
            "Maize": ["Fall armyworm", "Stem borer", "Ear rot"]
        }
        
        pests = pest_data.get(crop_name, [])
        risk_level = "High" if len(pests) > 2 else "Medium" if len(pests) > 1 else "Low"
        
        return {
            "pests": pests,
            "risk_level": risk_level,
            "recommendations": f"Monitor for {', '.join(pests)} and apply preventive measures"
        } 