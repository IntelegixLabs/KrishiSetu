from abc import ABC, abstractmethod
from typing import Dict, Any, List
from crewai import Agent
from langchain_openai import ChatOpenAI
from config import Config

class BaseAgent(ABC):
    """Base class for all agricultural agents"""
    
    def __init__(self, name: str, role: str, goal: str):
        self.name = name
        self.role = role
        self.goal = goal
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            api_key=Config.OPENAI_API_KEY
        )
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """Create a CrewAI agent with the specified configuration"""
        return Agent(
            role=self.role,
            goal=self.goal,
            backstory=self._get_backstory(),
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=self._get_tools()
        )
    
    @abstractmethod
    def _get_backstory(self) -> str:
        """Return the backstory for the agent"""
        pass
    
    @abstractmethod
    def _get_tools(self) -> List:
        """Return the tools available to the agent"""
        pass
    
    @abstractmethod
    def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a query and return a response"""
        pass
    
    def validate_input(self, query: str) -> bool:
        """Validate if the query is relevant to this agent"""
        return True
    
    def get_confidence_score(self, response: str) -> float:
        """Calculate confidence score for the response"""
        # Simple heuristic - can be improved with more sophisticated methods
        keywords = self._get_keywords()
        query_lower = response.lower()
        matches = sum(1 for keyword in keywords if keyword.lower() in query_lower)
        return min(matches / len(keywords), 1.0) if keywords else 0.5
    
    @abstractmethod
    def _get_keywords(self) -> List[str]:
        """Return keywords that indicate this agent should handle the query"""
        pass 