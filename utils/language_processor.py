import re
from typing import Dict, Any, List, Tuple
from config import Config

class LanguageProcessor:
    """Process multilingual agricultural queries and responses"""
    
    def __init__(self):
        self.language_patterns = {
            "hi": {
                "weather_keywords": ["मौसम", "बारिश", "तापमान", "सिंचाई", "पानी", "नमी"],
                "crop_keywords": ["फसल", "बीज", "किस्म", "रोपण", "फसल काटना", "उपज"],
                "finance_keywords": ["ऋण", "क्रेडिट", "वित्त", "पैसा", "बैंक", "योजना"],
                "greetings": ["नमस्ते", "स्वागत है", "कैसे हैं"],
                "questions": ["क्या", "कब", "कहाँ", "कैसे", "क्यों"]
            },
            "ta": {
                "weather_keywords": ["வானிலை", "மழை", "வெப்பநிலை", "நீர்ப்பாசனம்", "தண்ணீர்", "ஈரப்பதம்"],
                "crop_keywords": ["பயிர்", "விதை", "வகை", "நடவு", "அறுவடை", "மகசூல்"],
                "finance_keywords": ["கடன்", "கடன்", "நிதி", "பணம்", "வங்கி", "திட்டம்"],
                "greetings": ["வணக்கம்", "வரவேற்கிறோம்", "எப்படி இருக்கிறீர்கள்"],
                "questions": ["என்ன", "எப்போது", "எங்கே", "எப்படி", "ஏன்"]
            },
            "te": {
                "weather_keywords": ["వాతావరణం", "వర్షం", "ఉష్ణోగ్రత", "నీటి తడుపుదల", "నీరు", "తేమ"],
                "crop_keywords": ["పంట", "విత్తనం", "రకం", "నాటడం", "పంట కోత", "పంట"],
                "finance_keywords": ["రుణం", "క్రెడిట్", "ఆర్థిక", "డబ్బు", "బ్యాంక్", "పథకం"],
                "greetings": ["నమస్కారం", "స్వాగతం", "ఎలా ఉన్నారు"],
                "questions": ["ఏమి", "ఎప్పుడు", "ఎక్కడ", "ఎలా", "ఎందుకు"]
            }
        }
    
    def detect_language(self, text: str) -> str:
        """Detect the language of the input text"""
        # Simple language detection based on character sets
        if re.search(r'[\u0900-\u097F]', text):  # Devanagari
            return "hi"
        elif re.search(r'[\u0B80-\u0BFF]', text):  # Tamil
            return "ta"
        elif re.search(r'[\u0C00-\u0C7F]', text):  # Telugu
            return "te"
        else:
            return "en"
    
    def extract_keywords(self, text: str, language: str = "en") -> List[str]:
        """Extract relevant keywords from the text"""
        text_lower = text.lower()
        keywords = []
        
        if language in self.language_patterns:
            patterns = self.language_patterns[language]
            for category, words in patterns.items():
                for word in words:
                    if word.lower() in text_lower:
                        keywords.append(word)
        
        # Add English keywords as fallback
        english_keywords = [
            "weather", "rain", "temperature", "irrigation", "water", "humidity",
            "crop", "seed", "variety", "plant", "harvest", "yield",
            "loan", "credit", "finance", "money", "bank", "scheme"
        ]
        
        for word in english_keywords:
            if word.lower() in text_lower:
                keywords.append(word)
        
        return list(set(keywords))
    
    def classify_query_type(self, text: str, language: str = "en") -> str:
        """Classify the type of agricultural query"""
        keywords = self.extract_keywords(text, language)
        
        weather_count = sum(1 for kw in keywords if kw in [
            "weather", "rain", "temperature", "irrigation", "water", "humidity",
            "मौसम", "बारिश", "तापमान", "सिंचाई", "पानी", "नमी",
            "வானிலை", "மழை", "வெப்பநிலை", "நீர்ப்பாசனம்", "தண்ணீர்", "ஈரப்பதம்",
            "వాతావరణం", "వర్షం", "ఉష్ణోగ్రత", "నీటి తడుపుదల", "నీరు", "తేమ"
        ])
        
        crop_count = sum(1 for kw in keywords if kw in [
            "crop", "seed", "variety", "plant", "harvest", "yield",
            "फसल", "बीज", "किस्म", "रोपण", "फसल काटना", "उपज",
            "பயிர்", "விதை", "வகை", "நடவு", "அறுவடை", "மகசூல்",
            "పంట", "విత్తనం", "రకం", "నాటడం", "పంట కోత", "పంట"
        ])
        
        finance_count = sum(1 for kw in keywords if kw in [
            "loan", "credit", "finance", "money", "bank", "scheme",
            "ऋण", "क्रेडिट", "वित्त", "पैसा", "बैंक", "योजना",
            "கடன்", "கடன்", "நிதி", "பணம்", "வங்கி", "திட்டம்",
            "రుణం", "క్రెడిట్", "ఆర్థిక", "డబ్బు", "బ్యాంక్", "పథకం"
        ])
        
        if weather_count > crop_count and weather_count > finance_count:
            return "weather"
        elif crop_count > weather_count and crop_count > finance_count:
            return "crop"
        elif finance_count > weather_count and finance_count > crop_count:
            return "finance"
        else:
            return "general"
    
    def extract_location(self, text: str) -> str:
        """Extract location information from text"""
        # Common Indian cities and states
        locations = {
            "mumbai": "Mumbai",
            "delhi": "Delhi",
            "bangalore": "Bangalore",
            "chennai": "Chennai",
            "kolkata": "Kolkata",
            "hyderabad": "Hyderabad",
            "pune": "Pune",
            "ahmedabad": "Ahmedabad",
            "jaipur": "Jaipur",
            "lucknow": "Lucknow",
            "patna": "Patna",
            "bhopal": "Bhopal",
            "chandigarh": "Chandigarh",
            "guwahati": "Guwahati",
            "shillong": "Shillong",
            "imphal": "Imphal",
            "aizawl": "Aizawl",
            "kohima": "Kohima",
            "itanagar": "Itanagar",
            "gangtok": "Gangtok",
            "agartala": "Agartala",
            "dispur": "Dispur",
            "shimla": "Shimla",
            "dehradun": "Dehradun",
            "srinagar": "Srinagar",
            "leh": "Leh",
            "port blair": "Port Blair",
            "kavaratti": "Kavaratti",
            "daman": "Daman",
            "diu": "Diu",
            "panaji": "Panaji",
            "silvassa": "Silvassa",
            "puducherry": "Puducherry",
            "karnataka": "Karnataka",
            "maharashtra": "Maharashtra",
            "tamil nadu": "Tamil Nadu",
            "andhra pradesh": "Andhra Pradesh",
            "telangana": "Telangana",
            "kerala": "Kerala",
            "gujarat": "Gujarat",
            "rajasthan": "Rajasthan",
            "madhya pradesh": "Madhya Pradesh",
            "uttar pradesh": "Uttar Pradesh",
            "bihar": "Bihar",
            "west bengal": "West Bengal",
            "odisha": "Odisha",
            "jharkhand": "Jharkhand",
            "chhattisgarh": "Chhattisgarh",
            "himachal pradesh": "Himachal Pradesh",
            "uttarakhand": "Uttarakhand",
            "punjab": "Punjab",
            "haryana": "Haryana",
            "assam": "Assam",
            "manipur": "Manipur",
            "meghalaya": "Meghalaya",
            "mizoram": "Mizoram",
            "nagaland": "Nagaland",
            "arunachal pradesh": "Arunachal Pradesh",
            "sikkim": "Sikkim",
            "tripura": "Tripura",
            "goa": "Goa",
            "jammu and kashmir": "Jammu and Kashmir",
            "ladakh": "Ladakh",
            "andaman and nicobar": "Andaman and Nicobar",
            "lakshadweep": "Lakshadweep",
            "dadra and nagar haveli": "Dadra and Nagar Haveli",
            "daman and diu": "Daman and Diu",
            "puducherry": "Puducherry"
        }
        
        text_lower = text.lower()
        for location_key, location_value in locations.items():
            if location_key in text_lower:
                return location_value
        
        return "Mumbai"  # Default location
    
    def extract_crop_info(self, text: str) -> str:
        """Extract crop information from text"""
        crops = {
            "rice": "Rice",
            "wheat": "Wheat",
            "maize": "Maize",
            "cotton": "Cotton",
            "sugarcane": "Sugarcane",
            "pulses": "Pulses",
            "oilseeds": "Oilseeds",
            "vegetables": "Vegetables",
            "fruits": "Fruits",
            "spices": "Spices",
            "चावल": "Rice",
            "गेहूं": "Wheat",
            "मक्का": "Maize",
            "कपास": "Cotton",
            "गन्ना": "Sugarcane",
            "दालें": "Pulses",
            "तिलहन": "Oilseeds",
            "सब्जियां": "Vegetables",
            "फल": "Fruits",
            "मसाले": "Spices"
        }
        
        text_lower = text.lower()
        for crop_key, crop_value in crops.items():
            if crop_key in text_lower:
                return crop_value
        
        return "general"
    
    def translate_response(self, response: str, target_language: str) -> str:
        """Translate response to target language (simplified)"""
        # This is a simplified translation - in production, use proper translation APIs
        if target_language == "en":
            return response
        
        # Simple keyword-based translation for common agricultural terms
        translations = {
            "hi": {
                "weather": "मौसम",
                "crop": "फसल",
                "irrigation": "सिंचाई",
                "loan": "ऋण",
                "scheme": "योजना",
                "recommendation": "सिफारिश",
                "temperature": "तापमान",
                "rainfall": "वर्षा",
                "humidity": "नमी"
            },
            "ta": {
                "weather": "வானிலை",
                "crop": "பயிர்",
                "irrigation": "நீர்ப்பாசனம்",
                "loan": "கடன்",
                "scheme": "திட்டம்",
                "recommendation": "பரிந்துரை",
                "temperature": "வெப்பநிலை",
                "rainfall": "மழை",
                "humidity": "ஈரப்பதம்"
            }
        }
        
        if target_language in translations:
            translated = response
            for eng, local in translations[target_language].items():
                translated = translated.replace(eng, local)
            return translated
        
        return response
    
    def process_query(self, text: str) -> Dict[str, Any]:
        """Process a query and extract relevant information"""
        language = self.detect_language(text)
        query_type = self.classify_query_type(text, language)
        location = self.extract_location(text)
        crop = self.extract_crop_info(text)
        keywords = self.extract_keywords(text, language)
        
        return {
            "original_text": text,
            "detected_language": language,
            "query_type": query_type,
            "location": location,
            "crop": crop,
            "keywords": keywords,
            "confidence": len(keywords) / 10.0  # Simple confidence based on keyword count
        } 