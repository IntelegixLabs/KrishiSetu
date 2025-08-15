import unittest
from unittest.mock import Mock, patch
import asyncio
from agents import WeatherAgent, CropAgent, FinanceAgent
from utils.language_processor import LanguageProcessor

class TestWeatherAgent(unittest.TestCase):
    """Test cases for WeatherAgent"""
    
    def setUp(self):
        self.weather_agent = WeatherAgent()
    
    def test_weather_agent_initialization(self):
        """Test that WeatherAgent initializes correctly"""
        self.assertEqual(self.weather_agent.name, "Weather Expert")
        self.assertEqual(self.weather_agent.role, "Agricultural Weather Specialist")
    
    def test_weather_keywords(self):
        """Test that weather keywords are correctly identified"""
        keywords = self.weather_agent._get_keywords()
        self.assertIn("weather", keywords)
        self.assertIn("irrigation", keywords)
        self.assertIn("temperature", keywords)
    
    def test_weather_query_processing(self):
        """Test weather query processing"""
        query = "When should I irrigate my wheat crop?"
        context = {"location": "Mumbai"}
        
        result = self.weather_agent.process_query(query, context)
        
        self.assertIn("success", result)
        self.assertIn("data", result)
        self.assertIn("confidence", result)
    
    @patch('requests.get')
    def test_get_current_weather(self, mock_get):
        """Test current weather data retrieval"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "main": {"temp": 25, "humidity": 60, "pressure": 1013},
            "weather": [{"description": "clear sky"}],
            "wind": {"speed": 5}
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        weather_data = self.weather_agent.get_current_weather("Mumbai")
        
        self.assertIn("temperature", weather_data)
        self.assertIn("humidity", weather_data)
        self.assertEqual(weather_data["temperature"], 25)

class TestCropAgent(unittest.TestCase):
    """Test cases for CropAgent"""
    
    def setUp(self):
        self.crop_agent = CropAgent()
    
    def test_crop_agent_initialization(self):
        """Test that CropAgent initializes correctly"""
        self.assertEqual(self.crop_agent.name, "Crop Specialist")
        self.assertEqual(self.crop_agent.role, "Agricultural Crop Expert")
    
    def test_crop_keywords(self):
        """Test that crop keywords are correctly identified"""
        keywords = self.crop_agent._get_keywords()
        self.assertIn("crop", keywords)
        self.assertIn("seed", keywords)
        self.assertIn("harvest", keywords)
    
    def test_crop_recommendations(self):
        """Test crop recommendations"""
        recommendations = self.crop_agent.get_crop_recommendations(
            "Mumbai", "Alluvial", "Kharif"
        )
        
        self.assertIsInstance(recommendations, list)
        if recommendations:
            self.assertIn("name", recommendations[0])
            self.assertIn("varieties", recommendations[0])
    
    def test_crop_suitability_analysis(self):
        """Test crop suitability analysis"""
        crops = [
            {"name": "Rice", "water_need": "High"},
            {"name": "Wheat", "water_need": "Medium"}
        ]
        context = {"temperature": 25, "water_availability": "high"}
        
        analysis = self.crop_agent.analyze_crop_suitability(crops, context)
        
        self.assertIn("Rice", analysis)
        self.assertIn("Wheat", analysis)
        self.assertIn("suitability_score", analysis["Rice"])

class TestFinanceAgent(unittest.TestCase):
    """Test cases for FinanceAgent"""
    
    def setUp(self):
        self.finance_agent = FinanceAgent()
    
    def test_finance_agent_initialization(self):
        """Test that FinanceAgent initializes correctly"""
        self.assertEqual(self.finance_agent.name, "Finance Advisor")
        self.assertEqual(self.finance_agent.role, "Agricultural Finance Specialist")
    
    def test_finance_keywords(self):
        """Test that finance keywords are correctly identified"""
        keywords = self.finance_agent._get_keywords()
        self.assertIn("loan", keywords)
        self.assertIn("credit", keywords)
        self.assertIn("scheme", keywords)
    
    def test_loan_options(self):
        """Test loan options retrieval"""
        loans = self.finance_agent.get_loan_options("small", 1.5, "Rice")
        
        self.assertIsInstance(loans, list)
        if loans:
            self.assertIn("name", loans[0])
            self.assertIn("interest_rate", loans[0])
    
    def test_government_schemes(self):
        """Test government schemes retrieval"""
        schemes = self.finance_agent.get_government_schemes("Maharashtra", "small")
        
        self.assertIsInstance(schemes, list)
        if schemes:
            self.assertIn("name", schemes[0])
            self.assertIn("description", schemes[0])

class TestLanguageProcessor(unittest.TestCase):
    """Test cases for LanguageProcessor"""
    
    def setUp(self):
        self.language_processor = LanguageProcessor()
    
    def test_language_detection(self):
        """Test language detection"""
        # Test Hindi
        hindi_text = "मौसम कैसा है?"
        detected_lang = self.language_processor.detect_language(hindi_text)
        self.assertEqual(detected_lang, "hi")
        
        # Test English
        english_text = "How is the weather?"
        detected_lang = self.language_processor.detect_language(english_text)
        self.assertEqual(detected_lang, "en")
    
    def test_query_classification(self):
        """Test query type classification"""
        # Weather query
        weather_query = "When should I irrigate?"
        query_type = self.language_processor.classify_query_type(weather_query)
        self.assertEqual(query_type, "weather")
        
        # Crop query
        crop_query = "Which crop should I plant?"
        query_type = self.language_processor.classify_query_type(crop_query)
        self.assertEqual(query_type, "crop")
        
        # Finance query
        finance_query = "What loans are available?"
        query_type = self.language_processor.classify_query_type(finance_query)
        self.assertEqual(query_type, "finance")
    
    def test_location_extraction(self):
        """Test location extraction"""
        text = "I am in Mumbai and need advice"
        location = self.language_processor.extract_location(text)
        self.assertEqual(location, "Mumbai")
    
    def test_crop_extraction(self):
        """Test crop information extraction"""
        text = "I want to grow rice"
        crop = self.language_processor.extract_crop_info(text)
        self.assertEqual(crop, "Rice")

class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def setUp(self):
        self.weather_agent = WeatherAgent()
        self.crop_agent = CropAgent()
        self.finance_agent = FinanceAgent()
        self.language_processor = LanguageProcessor()
    
    def test_end_to_end_query_processing(self):
        """Test end-to-end query processing"""
        query = "When should I irrigate my wheat crop in Mumbai?"
        
        # Process query
        processed = self.language_processor.process_query(query)
        
        # Verify processing
        self.assertEqual(processed["query_type"], "weather")
        self.assertEqual(processed["location"], "Mumbai")
        self.assertEqual(processed["crop"], "Wheat")
        
        # Test agent response
        context = {
            "location": processed["location"],
            "crop_type": processed["crop"]
        }
        
        result = self.weather_agent.process_query(query, context)
        self.assertIn("success", result)
        self.assertIn("data", result)

if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2) 