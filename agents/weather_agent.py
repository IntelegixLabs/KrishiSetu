import requests
import json
from typing import Dict, Any, List
from datetime import datetime, timedelta
from .base_agent import BaseAgent
from config import Config

class WeatherAgent(BaseAgent):
    """Agent specialized in weather analysis and irrigation recommendations"""
    
    def __init__(self):
        super().__init__(
            name="Weather Expert",
            role="Agricultural Weather Specialist",
            goal="Provide accurate weather forecasts and irrigation recommendations for optimal crop growth"
        )
    
    def _get_backstory(self) -> str:
        return """You are an expert agricultural meteorologist with 15 years of experience in 
        analyzing weather patterns for Indian agriculture. You understand the specific weather 
        needs of different crops, soil types, and regions across India. You provide practical 
        advice on irrigation timing, crop protection from weather extremes, and optimal farming 
        practices based on weather conditions."""
    
    def _get_tools(self) -> List:
        return [
            self.get_current_weather,
            self.get_weather_forecast,
            self.analyze_irrigation_needs,
            self.get_soil_moisture_analysis
        ]
    
    def _get_keywords(self) -> List[str]:
        return [
            "weather", "temperature", "rain", "irrigation", "humidity", "forecast",
            "drought", "flood", "monsoon", "season", "climate", "moisture",
            "पानी", "मौसम", "सिंचाई", "बारिश", "तापमान", "नमी"
        ]
    
    def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process weather-related queries"""
        try:
            # Extract location from context or query
            location = context.get('location', 'Mumbai') if context else 'Mumbai'
            
            # Get current weather
            current_weather = self.get_current_weather(location)
            
            # Get forecast
            forecast = self.get_weather_forecast(location)
            
            # Analyze irrigation needs
            irrigation_advice = self.analyze_irrigation_needs(current_weather, forecast)
            
            response = {
                "current_weather": current_weather,
                "forecast": forecast,
                "irrigation_recommendation": irrigation_advice,
                "timestamp": datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "data": response,
                "confidence": self.get_confidence_score(query),
                "source": "Weather Agent"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "confidence": 0.0,
                "source": "Weather Agent"
            }
    
    def get_current_weather(self, location: str) -> Dict[str, Any]:
        """Get current weather data for a location"""
        try:
            url = f"{Config.WEATHER_BASE_URL}/weather"
            params = {
                'q': location,
                'appid': Config.WEATHER_API_KEY,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return {
                "temperature": data['main']['temp'],
                "humidity": data['main']['humidity'],
                "description": data['weather'][0]['description'],
                "wind_speed": data['wind']['speed'],
                "pressure": data['main']['pressure']
            }
        except Exception as e:
            return {"error": f"Failed to fetch weather data: {str(e)}"}
    
    def get_weather_forecast(self, location: str) -> Dict[str, Any]:
        """Get 5-day weather forecast"""
        try:
            url = f"{Config.WEATHER_BASE_URL}/forecast"
            params = {
                'q': location,
                'appid': Config.WEATHER_API_KEY,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            forecast = []
            
            for item in data['list'][:8]:  # Next 24 hours (3-hour intervals)
                forecast.append({
                    "time": item['dt_txt'],
                    "temperature": item['main']['temp'],
                    "humidity": item['main']['humidity'],
                    "description": item['weather'][0]['description'],
                    "rainfall": item.get('rain', {}).get('3h', 0)
                })
            
            return {"forecast": forecast}
        except Exception as e:
            return {"error": f"Failed to fetch forecast: {str(e)}"}
    
    def analyze_irrigation_needs(self, current_weather: Dict, forecast: Dict) -> Dict[str, Any]:
        """Analyze irrigation needs based on weather data"""
        temp = current_weather.get('temperature', 25)
        humidity = current_weather.get('humidity', 60)
        
        # Simple irrigation logic (can be enhanced with crop-specific data)
        if temp > 30 and humidity < 50:
            recommendation = "High irrigation needed - high temperature and low humidity"
            priority = "High"
        elif temp > 25 and humidity < 60:
            recommendation = "Moderate irrigation recommended"
            priority = "Medium"
        else:
            recommendation = "Low irrigation needed - favorable conditions"
            priority = "Low"
        
        return {
            "recommendation": recommendation,
            "priority": priority,
            "reasoning": f"Temperature: {temp}°C, Humidity: {humidity}%",
            "next_irrigation": self._calculate_next_irrigation(current_weather, forecast)
        }
    
    def _calculate_next_irrigation(self, current_weather: Dict, forecast: Dict) -> str:
        """Calculate when next irrigation should be done"""
        # Simple logic - can be enhanced with soil moisture sensors
        temp = current_weather.get('temperature', 25)
        if temp > 30:
            return "Within 24 hours"
        elif temp > 25:
            return "Within 48 hours"
        else:
            return "Within 72 hours"
    
    def get_soil_moisture_analysis(self, location: str) -> Dict[str, Any]:
        """Analyze soil moisture based on weather patterns"""
        # This would integrate with soil moisture sensors in a real implementation
        return {
            "soil_moisture": "Moderate",
            "recommendation": "Monitor soil moisture levels",
            "next_check": "24 hours"
        } 