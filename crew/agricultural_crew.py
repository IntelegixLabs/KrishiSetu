from crewai import Crew, Task
from typing import Dict, Any, List
from agents import WeatherAgent, CropAgent, FinanceAgent
from mcp.mcp_client import MCPDataProvider
import asyncio

class AgriculturalCrew:
    """Crew that orchestrates multiple agricultural agents"""
    
    def __init__(self):
        self.weather_agent = WeatherAgent()
        self.crop_agent = CropAgent()
        self.finance_agent = FinanceAgent()
        self.mcp_provider = MCPDataProvider()
        
    async def process_comprehensive_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a comprehensive agricultural query using multiple agents"""
        
        try:
            # Initialize MCP data provider
            await self.mcp_provider.initialize()
            
            # Check if LLM is available
            if self.weather_agent.llm is None:
                # Fallback to direct agent processing without CrewAI
                return await self._process_without_crew(query, context)
            
            # Create tasks for different aspects
            weather_task = Task(
                description=f"Analyze weather conditions and provide irrigation advice for: {query}",
                agent=self.weather_agent.agent,
                expected_output="Weather analysis and irrigation recommendations"
            )
            
            crop_task = Task(
                description=f"Provide crop selection and management advice for: {query}",
                agent=self.crop_agent.agent,
                expected_output="Crop recommendations and management strategies"
            )
            
            finance_task = Task(
                description=f"Provide financial advice and government scheme information for: {query}",
                agent=self.finance_agent.agent,
                expected_output="Financial options and government support information"
            )
            
            # Create the crew
            crew = Crew(
                agents=[self.weather_agent.agent, self.crop_agent.agent, self.finance_agent.agent],
                tasks=[weather_task, crop_task, finance_task],
                verbose=True
            )
            
            # Execute the crew
            result = crew.kickoff()
            
            # Get additional data from MCP
            location = context.get('location', 'Mumbai') if context else 'Mumbai'
            crop = context.get('crop_type', 'general') if context else 'general'
            state = context.get('state', 'Maharashtra') if context else 'Maharashtra'
            
            mcp_data = await self.mcp_provider.get_comprehensive_data(location, crop, state)
            
            # Combine results
            comprehensive_response = {
                "crew_result": result,
                "mcp_data": mcp_data,
                "agent_insights": {
                    "weather": await self._get_agent_insight(self.weather_agent, query, context),
                    "crop": await self._get_agent_insight(self.crop_agent, query, context),
                    "finance": await self._get_agent_insight(self.finance_agent, query, context)
                },
                "recommendations": self._synthesize_recommendations(result, mcp_data),
                "timestamp": asyncio.get_event_loop().time()
            }
            
            return {
                "success": True,
                "data": comprehensive_response,
                "confidence": self._calculate_overall_confidence(comprehensive_response),
                "source": "Agricultural Crew"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "confidence": 0.0,
                "source": "Agricultural Crew"
            }
        finally:
            await self.mcp_provider.close()
    
    async def _process_without_crew(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process query without CrewAI when LLM is not available"""
        try:
            # Get insights from individual agents
            weather_insight = self.weather_agent.process_query(query, context)
            crop_insight = self.crop_agent.process_query(query, context)
            finance_insight = self.finance_agent.process_query(query, context)
            
            # Get MCP data
            location = context.get('location', 'Mumbai') if context else 'Mumbai'
            crop = context.get('crop_type', 'general') if context else 'general'
            state = context.get('state', 'Maharashtra') if context else 'Maharashtra'
            
            mcp_data = await self.mcp_provider.get_comprehensive_data(location, crop, state)
            
            # Synthesize response
            comprehensive_response = {
                "crew_result": "Direct agent processing (no LLM available)",
                "mcp_data": mcp_data,
                "agent_insights": {
                    "weather": weather_insight,
                    "crop": crop_insight,
                    "finance": finance_insight
                },
                "recommendations": self._synthesize_recommendations("Direct processing", mcp_data),
                "timestamp": asyncio.get_event_loop().time()
            }
            
            return {
                "success": True,
                "data": comprehensive_response,
                "confidence": self._calculate_overall_confidence(comprehensive_response),
                "source": "Agricultural Crew (Direct Processing)"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "confidence": 0.0,
                "source": "Agricultural Crew"
            }
    
    async def _get_agent_insight(self, agent, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get specific insights from individual agents"""
        try:
            return agent.process_query(query, context)
        except Exception as e:
            return {"error": str(e)}
    
    def _synthesize_recommendations(self, crew_result: str, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize recommendations from crew results and MCP data"""
        recommendations = {
            "immediate_actions": [],
            "short_term_plan": [],
            "long_term_strategy": [],
            "risk_mitigation": [],
            "opportunities": []
        }
        
        # Extract immediate actions from weather data
        if 'weather' in mcp_data and 'error' not in mcp_data['weather']:
            weather = mcp_data['weather']
            if weather.get('temperature', 25) > 30:
                recommendations["immediate_actions"].append("Increase irrigation frequency due to high temperature")
            if weather.get('humidity', 60) < 50:
                recommendations["immediate_actions"].append("Monitor soil moisture levels")
        
        # Extract crop recommendations
        if 'market' in mcp_data and 'error' not in mcp_data['market']:
            market = mcp_data['market']
            if market.get('trend') == 'Rising':
                recommendations["opportunities"].append("Consider planting crops with rising market prices")
        
        # Extract policy opportunities
        if 'policies' in mcp_data and mcp_data['policies']:
            recommendations["opportunities"].append("Explore available government schemes and subsidies")
        
        return recommendations
    
    def _calculate_overall_confidence(self, response: Dict[str, Any]) -> float:
        """Calculate overall confidence score"""
        confidence_scores = []
        
        # Get confidence from individual agents
        for agent_type, insight in response.get('agent_insights', {}).items():
            if 'confidence' in insight:
                confidence_scores.append(insight['confidence'])
        
        # Get confidence from MCP data quality
        mcp_data = response.get('mcp_data', {})
        mcp_errors = sum(1 for data in mcp_data.values() if 'error' in data)
        mcp_confidence = max(0, 1 - (mcp_errors / len(mcp_data))) if mcp_data else 0.5
        confidence_scores.append(mcp_confidence)
        
        # Calculate average confidence
        return sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
    
    async def process_simple_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a simple query using the most relevant agent"""
        
        # Determine the most relevant agent based on keywords
        agent_scores = {
            'weather': self._calculate_relevance_score(query, self.weather_agent._get_keywords()),
            'crop': self._calculate_relevance_score(query, self.crop_agent._get_keywords()),
            'finance': self._calculate_relevance_score(query, self.finance_agent._get_keywords())
        }
        
        # Select the most relevant agent
        best_agent_type = max(agent_scores, key=agent_scores.get)
        
        if best_agent_type == 'weather':
            agent = self.weather_agent
        elif best_agent_type == 'crop':
            agent = self.crop_agent
        else:
            agent = self.finance_agent
        
        return agent.process_query(query, context)
    
    def _calculate_relevance_score(self, query: str, keywords: List[str]) -> float:
        """Calculate relevance score based on keyword matching"""
        query_lower = query.lower()
        matches = sum(1 for keyword in keywords if keyword.lower() in query_lower)
        return matches / len(keywords) if keywords else 0.0 