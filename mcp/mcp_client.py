import json
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from config import Config

class MCPClient:
    """Model Context Protocol client for external data integration"""
    
    def __init__(self, server_url: str = None):
        self.server_url = server_url or Config.MCP_SERVER_URL
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize MCP connection"""
        try:
            async with self.session.post(f"{self.server_url}/initialize") as response:
                return await response.json()
        except Exception as e:
            return {"error": f"Failed to initialize MCP: {str(e)}"}
    
    async def list_resources(self) -> List[Dict[str, Any]]:
        """List available resources"""
        try:
            async with self.session.get(f"{self.server_url}/resources") as response:
                return await response.json()
        except Exception as e:
            return [{"error": f"Failed to list resources: {str(e)}"}]
    
    async def read_resource(self, resource_id: str) -> Dict[str, Any]:
        """Read a specific resource"""
        try:
            async with self.session.get(f"{self.server_url}/resources/{resource_id}") as response:
                return await response.json()
        except Exception as e:
            return {"error": f"Failed to read resource: {str(e)}"}
    
    async def search_resources(self, query: str) -> List[Dict[str, Any]]:
        """Search for resources"""
        try:
            params = {"query": query}
            async with self.session.get(f"{self.server_url}/search", params=params) as response:
                return await response.json()
        except Exception as e:
            return [{"error": f"Failed to search resources: {str(e)}"}]
    
    async def get_weather_data(self, location: str) -> Dict[str, Any]:
        """Get weather data through MCP"""
        try:
            params = {"location": location, "type": "weather"}
            async with self.session.get(f"{self.server_url}/data", params=params) as response:
                return await response.json()
        except Exception as e:
            return {"error": f"Failed to get weather data: {str(e)}"}
    
    async def get_market_data(self, crop: str) -> Dict[str, Any]:
        """Get market data through MCP"""
        try:
            params = {"crop": crop, "type": "market"}
            async with self.session.get(f"{self.server_url}/data", params=params) as response:
                return await response.json()
        except Exception as e:
            return {"error": f"Failed to get market data: {str(e)}"}
    
    async def get_soil_data(self, location: str) -> Dict[str, Any]:
        """Get soil data through MCP"""
        try:
            params = {"location": location, "type": "soil"}
            async with self.session.get(f"{self.server_url}/data", params=params) as response:
                return await response.json()
        except Exception as e:
            return {"error": f"Failed to get soil data: {str(e)}"}
    
    async def get_policy_data(self, state: str) -> List[Dict[str, Any]]:
        """Get government policy data through MCP"""
        try:
            params = {"state": state, "type": "policy"}
            async with self.session.get(f"{self.server_url}/data", params=params) as response:
                return await response.json()
        except Exception as e:
            return [{"error": f"Failed to get policy data: {str(e)}"}]

class MCPDataProvider:
    """Data provider that uses MCP for external data sources"""
    
    def __init__(self):
        self.mcp_client = None
    
    async def initialize(self):
        """Initialize MCP client"""
        self.mcp_client = MCPClient()
        await self.mcp_client.__aenter__()
        await self.mcp_client.initialize()
    
    async def close(self):
        """Close MCP client"""
        if self.mcp_client:
            await self.mcp_client.__aexit__(None, None, None)
    
    async def get_comprehensive_data(self, location: str, crop: str = None, state: str = None) -> Dict[str, Any]:
        """Get comprehensive data from multiple sources"""
        if not self.mcp_client:
            await self.initialize()
        
        data = {}
        
        # Get weather data
        weather_data = await self.mcp_client.get_weather_data(location)
        data['weather'] = weather_data
        
        # Get soil data
        soil_data = await self.mcp_client.get_soil_data(location)
        data['soil'] = soil_data
        
        # Get market data if crop is specified
        if crop:
            market_data = await self.mcp_client.get_market_data(crop)
            data['market'] = market_data
        
        # Get policy data if state is specified
        if state:
            policy_data = await self.mcp_client.get_policy_data(state)
            data['policies'] = policy_data
        
        return data 