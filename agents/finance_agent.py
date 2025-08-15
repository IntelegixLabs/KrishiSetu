import requests
import json
from typing import Dict, Any, List
from datetime import datetime
from .base_agent import BaseAgent
from config import Config

class FinanceAgent(BaseAgent):
    """Agent specialized in agricultural finance and government schemes"""
    
    def __init__(self):
        super().__init__(
            name="Finance Advisor",
            role="Agricultural Finance Specialist",
            goal="Provide comprehensive financial advice including loans, government schemes, and market insights"
        )
    
    def _get_backstory(self) -> str:
        return """You are a senior agricultural finance expert with extensive experience in 
        rural banking, government schemes, and agricultural economics. You understand the 
        financial challenges faced by Indian farmers and provide practical advice on loans, 
        subsidies, insurance, and market opportunities. You have deep knowledge of both 
        government and private sector financial products for agriculture."""
    
    def _get_tools(self) -> List:
        return [
            self.get_loan_options,
            self.get_government_schemes,
            self.analyze_market_trends,
            self.get_insurance_options,
            self.calculate_loan_eligibility
        ]
    
    def _get_keywords(self) -> List[str]:
        return [
            "loan", "credit", "finance", "money", "bank", "scheme", "subsidy",
            "insurance", "market", "price", "profit", "investment", "budget",
            "ऋण", "क्रेडिट", "वित्त", "पैसा", "बैंक", "योजना", "सब्सिडी",
            "बीमा", "बाजार", "कीमत", "लाभ", "निवेश", "बजट"
        ]
    
    def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process finance-related queries"""
        try:
            # Extract parameters from context
            farmer_type = context.get('farmer_type', 'small') if context else 'small'
            land_area = context.get('land_area', 2)  # in hectares
            crop_type = context.get('crop_type', 'general')
            state = context.get('state', 'Maharashtra')
            
            # Get loan options
            loans = self.get_loan_options(farmer_type, land_area, crop_type)
            
            # Get government schemes
            schemes = self.get_government_schemes(state, farmer_type)
            
            # Analyze market trends
            market_analysis = self.analyze_market_trends(crop_type)
            
            # Get insurance options
            insurance = self.get_insurance_options(crop_type, land_area)
            
            # Calculate loan eligibility
            eligibility = self.calculate_loan_eligibility(farmer_type, land_area, context)
            
            response = {
                "loan_options": loans,
                "government_schemes": schemes,
                "market_analysis": market_analysis,
                "insurance_options": insurance,
                "loan_eligibility": eligibility,
                "timestamp": datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "data": response,
                "confidence": self.get_confidence_score(query),
                "source": "Finance Agent"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "confidence": 0.0,
                "source": "Finance Agent"
            }
    
    def get_loan_options(self, farmer_type: str, land_area: float, crop_type: str) -> List[Dict[str, Any]]:
        """Get available loan options for farmers"""
        loan_options = [
            {
                "name": "Kisan Credit Card (KCC)",
                "institution": "All Banks",
                "interest_rate": "7.0%",
                "max_amount": "₹3,00,000",
                "tenure": "5 years",
                "eligibility": "All farmers",
                "features": ["No collateral for loans up to ₹1.6 lakh", "Flexible repayment", "Crop insurance included"]
            },
            {
                "name": "PM-KISAN",
                "institution": "Government of India",
                "interest_rate": "0%",
                "max_amount": "₹6,000/year",
                "tenure": "Annual",
                "eligibility": "Small and marginal farmers",
                "features": ["Direct benefit transfer", "No repayment required", "Three installments per year"]
            },
            {
                "name": "Agricultural Term Loan",
                "institution": "NABARD",
                "interest_rate": "8.5%",
                "max_amount": "₹10,00,000",
                "tenure": "3-7 years",
                "eligibility": "Farmers with land documents",
                "features": ["For farm mechanization", "Infrastructure development", "Collateral required"]
            },
            {
                "name": "Microfinance Loan",
                "institution": "MFIs",
                "interest_rate": "18-24%",
                "max_amount": "₹50,000",
                "tenure": "1-2 years",
                "eligibility": "Small farmers, women farmers",
                "features": ["Group lending", "Weekly/monthly repayment", "No collateral"]
            }
        ]
        
        # Filter based on farmer type and land area
        if farmer_type == 'small' and land_area < 2:
            return [loan for loan in loan_options if loan['name'] in ['Kisan Credit Card (KCC)', 'PM-KISAN', 'Microfinance Loan']]
        elif farmer_type == 'medium' and 2 <= land_area <= 10:
            return [loan for loan in loan_options if loan['name'] in ['Kisan Credit Card (KCC)', 'Agricultural Term Loan']]
        else:
            return loan_options
    
    def get_government_schemes(self, state: str, farmer_type: str) -> List[Dict[str, Any]]:
        """Get relevant government schemes"""
        schemes = [
            {
                "name": "PM Fasal Bima Yojana",
                "description": "Crop insurance scheme covering yield and weather risks",
                "coverage": "All food crops, oilseeds, and commercial crops",
                "premium": "2% for Kharif, 1.5% for Rabi, 5% for commercial crops",
                "benefits": ["Yield loss coverage", "Weather risk coverage", "Post-harvest losses"]
            },
            {
                "name": "PM-KISAN",
                "description": "Direct income support of ₹6,000 per year to farmers",
                "coverage": "Small and marginal farmers",
                "premium": "Free",
                "benefits": ["Direct bank transfer", "No repayment", "Three installments"]
            },
            {
                "name": "Kisan Samman Nidhi",
                "description": "Pension scheme for small and marginal farmers",
                "coverage": "Farmers aged 60-80 years",
                "premium": "₹55-200 per month",
                "benefits": ["Monthly pension", "Life insurance", "Accident coverage"]
            },
            {
                "name": "Soil Health Card Scheme",
                "description": "Free soil testing and recommendations",
                "coverage": "All farmers",
                "premium": "Free",
                "benefits": ["Soil testing", "Fertilizer recommendations", "Crop-specific advice"]
            }
        ]
        
        # Add state-specific schemes
        state_schemes = {
            "Maharashtra": [
                {
                    "name": "Maharashtra Krishi Sanjivani Yojana",
                    "description": "Weather-based crop insurance",
                    "coverage": "All crops in Maharashtra",
                    "premium": "Subsidized rates",
                    "benefits": ["Weather risk coverage", "Quick claim settlement"]
                }
            ],
            "Punjab": [
                {
                    "name": "Punjab Kisan Vikas Yojana",
                    "description": "Support for crop diversification",
                    "coverage": "Farmers switching from paddy",
                    "premium": "Free",
                    "benefits": ["Financial assistance", "Technical support", "Market linkage"]
                }
            ]
        }
        
        schemes.extend(state_schemes.get(state, []))
        return schemes
    
    def analyze_market_trends(self, crop_type: str) -> Dict[str, Any]:
        """Analyze market trends for agricultural products"""
        # This would integrate with real-time market data
        market_data = {
            "Rice": {
                "current_price": 1800,
                "trend": "Stable",
                "forecast": "Expected to remain stable",
                "factors": ["Good monsoon", "Government procurement", "Export demand"]
            },
            "Wheat": {
                "current_price": 2100,
                "trend": "Rising",
                "forecast": "Expected to increase by 5-10%",
                "factors": ["Reduced production", "Increased demand", "Export opportunities"]
            },
            "Cotton": {
                "current_price": 5500,
                "trend": "Falling",
                "forecast": "Expected to stabilize",
                "factors": ["Global price pressure", "Textile industry slowdown"]
            }
        }
        
        return market_data.get(crop_type, {
            "current_price": 0,
            "trend": "Unknown",
            "forecast": "Data not available",
            "factors": []
        })
    
    def get_insurance_options(self, crop_type: str, land_area: float) -> List[Dict[str, Any]]:
        """Get crop insurance options"""
        insurance_options = [
            {
                "name": "PM Fasal Bima Yojana",
                "coverage": "Yield loss, weather risk, post-harvest losses",
                "premium_rate": "2% for Kharif, 1.5% for Rabi",
                "sum_insured": f"₹{land_area * 50000}",
                "features": ["Government subsidy", "Quick settlement", "Comprehensive coverage"]
            },
            {
                "name": "Weather-Based Crop Insurance",
                "coverage": "Weather-related losses",
                "premium_rate": "3-5%",
                "sum_insured": f"₹{land_area * 40000}",
                "features": ["Weather station data", "Automatic settlement", "No crop cutting experiments"]
            },
            {
                "name": "Crop Insurance for Horticulture",
                "coverage": "Fruits and vegetables",
                "premium_rate": "5-8%",
                "sum_insured": f"₹{land_area * 60000}",
                "features": ["Specialized coverage", "Market price protection", "Quality loss coverage"]
            }
        ]
        
        return insurance_options
    
    def calculate_loan_eligibility(self, farmer_type: str, land_area: float, context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate loan eligibility for farmers"""
        base_amount = land_area * 50000  # ₹50,000 per hectare
        
        # Adjust based on farmer type
        if farmer_type == 'small':
            multiplier = 0.8
        elif farmer_type == 'medium':
            multiplier = 1.0
        else:  # large
            multiplier = 1.2
        
        # Adjust based on credit history
        credit_score = context.get('credit_score', 'good')
        if credit_score == 'excellent':
            credit_multiplier = 1.2
        elif credit_score == 'good':
            credit_multiplier = 1.0
        else:
            credit_multiplier = 0.7
        
        eligible_amount = base_amount * multiplier * credit_multiplier
        
        return {
            "eligible_amount": f"₹{eligible_amount:,.0f}",
            "factors": [
                f"Land area: {land_area} hectares",
                f"Farmer type: {farmer_type}",
                f"Credit score: {credit_score}"
            ],
            "recommendations": [
                "Maintain good credit history",
                "Keep land documents updated",
                "Consider crop insurance for better terms"
            ]
        } 