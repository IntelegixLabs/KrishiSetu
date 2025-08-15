# 🌾 KrishiSetu - Agricultural AI Advisor

A comprehensive AI-powered agricultural advisory system designed specifically for Indian farmers. This system uses multi-agent architecture with CrewAI, MCP (Model Context Protocol), and FastAPI to provide intelligent, contextual advice for agricultural decisions.

## 🎯 Problem Statement

KrishiSetu addresses the critical challenges faced by Indian farmers by providing AI-driven solutions to answer questions like:

- **"When should I irrigate?"** - Weather-based irrigation recommendations
- **"What seed variety suits this unpredictable weather?"** - Climate-adaptive crop selection
- **"Will next week's temperature drop kill my yield?"** - Weather risk assessment
- **"Can I afford to wait for the market to improve?"** - Market trend analysis
- **"Where can I get affordable credit, and will any state/central government policy help me with finances?"** - Financial guidance and policy information

## 🏗️ Architecture

### Multi-Agent System
The system uses three specialized AI agents working together:

1. **🌤️ Weather Agent** - Provides weather analysis and irrigation recommendations
2. **🌱 Crop Agent** - Offers crop selection and management advice
3. **💰 Finance Agent** - Delivers financial guidance and government scheme information

### Technology Stack
- **CrewAI** - Multi-agent orchestration and task management
- **MCP (Model Context Protocol)** - External data integration
- **FastAPI** - High-performance web API
- **LangChain** - LLM integration and tool management
- **SQLAlchemy** - Database management
- **Pydantic** - Data validation and serialization

## 🚀 Features

### 🌍 Multilingual Support
- **English, Hindi, Tamil, Telugu, Bengali, Marathi, Gujarati, Kannada, Malayalam, Punjabi**
- Automatic language detection
- Localized responses for Indian farmers

### 📊 Real-time Data Integration
- Weather data from OpenWeatherMap API
- Government agricultural data
- Market price information
- Soil health data

### 🎯 Intelligent Query Processing
- Natural language understanding
- Context-aware responses
- Confidence scoring
- Multi-domain synthesis

### 🔧 Extensible Architecture
- Modular agent system
- Plugin-based data sources
- Configurable workflows
- Easy integration with external systems

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd KrishiSetu
   ```

2. **Install dependencies**
   ```bash
   uv pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Initialize the database**
   ```bash
   python -c "from models.database import create_tables; create_tables()"
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

## 🔑 Configuration

### Required API Keys
- **OpenAI API Key** - For LLM-powered agents
- **Tavily API Key** - For web search capabilities
- **Weather API Key** - For weather data (OpenWeatherMap)

### Environment Variables
```env
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
WEATHER_API_KEY=your_weather_api_key_here
DATABASE_URL=sqlite:///./krishisetu.db
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

## 🎮 Usage

### **API Endpoints**

#### 1. Process Agricultural Query
```http
POST /query
Content-Type: application/json

{
  "query": "When should I irrigate my wheat crop?",
  "context": {
    "location": "Mumbai",
    "crop_type": "Wheat",
    "farmer_type": "small"
  },
  "comprehensive": true,
  "language": "en"
}
```

#### 2. Weather-Specific Query
```http
POST /query/weather
Content-Type: application/json

{
  "query": "क्या आज बारिश होगी?",
  "context": {"location": "Delhi"}
}
```

#### 3. Crop-Specific Query
```http
POST /query/crop
Content-Type: application/json

{
  "query": "Which crop should I plant this season?",
  "context": {
    "location": "Punjab",
    "soil_type": "Alluvial",
    "season": "Kharif"
  }
}
```

#### 4. Finance-Specific Query
```http
POST /query/finance
Content-Type: application/json

{
  "query": "What loans are available for farmers?",
  "context": {
    "farmer_type": "small",
    "land_area": 2.0,
    "state": "Maharashtra"
  }
}
```

### Example Responses

#### Weather Query Response
```json
{
  "success": true,
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
    }
  },
  "confidence": 0.85,
  "source": "Weather Agent"
}
```

#### Crop Query Response
```json
{
  "success": true,
  "data": {
    "recommendations": [
      {
        "name": "Rice",
        "varieties": ["IR64", "Swarna"],
        "suitability_score": 85,
        "market_price": 1800
      }
    ],
    "crop_calendar": {
      "planting_start": "June",
      "harvest_start": "September"
    }
  },
  "confidence": 0.78,
  "source": "Crop Agent"
}
```

## 🧪 Testing

Run the test suite to ensure all components work correctly:

```bash
python -m pytest tests/
```

Or run specific test categories:

```bash
# Test agents
python tests/test_agents.py

# Test language processing
python -c "from tests.test_agents import TestLanguageProcessor; unittest.main()"
```

## 📁 Project Structure

```
KrishiSetu/
├── agents/                 # AI agent implementations
│   ├── base_agent.py      # Base agent class
│   ├── weather_agent.py   # Weather analysis agent
│   ├── crop_agent.py      # Crop management agent
│   └── finance_agent.py   # Financial advisory agent
├── api/                   # FastAPI application
│   └── main.py           # Main API endpoints
├── crew/                  # CrewAI orchestration
│   └── agricultural_crew.py
├── mcp/                   # Model Context Protocol
│   └── mcp_client.py     # MCP client implementation
├── models/                # Database models
│   └── database.py       # SQLAlchemy models
├── utils/                 # Utility functions
│   └── language_processor.py
├── tests/                 # Test suite
│   └── test_agents.py
├── config.py             # Configuration management
├── main.py               # Application entry point
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🔧 Development

### Adding New Agents

1. Create a new agent class inheriting from `BaseAgent`
2. Implement required methods:
   - `_get_backstory()`
   - `_get_tools()`
   - `process_query()`
   - `_get_keywords()`

3. Register the agent in the crew:

```python
from crew.agricultural_crew import AgriculturalCrew

class NewAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="New Expert",
            role="New Specialist",
            goal="Provide new type of advice"
        )
    
    # Implement required methods...
```

### Adding New Data Sources

1. Extend the MCP client in `mcp/mcp_client.py`
2. Add new data retrieval methods
3. Update the data provider in `crew/agricultural_crew.py`

### Customizing Language Support

1. Add new language patterns in `utils/language_processor.py`
2. Update the `language_patterns` dictionary
3. Add translation mappings

## 🌟 Key Innovations

### 1. Multi-Agent Collaboration
- Agents work together using CrewAI for comprehensive analysis
- Each agent specializes in specific domains
- Coordinated responses provide holistic advice

### 2. Context-Aware Processing
- Extracts location, crop type, and farmer context
- Provides personalized recommendations
- Considers local conditions and constraints

### 3. Multilingual Intelligence
- Automatic language detection
- Localized agricultural terminology
- Cultural context awareness

### 4. Real-time Data Integration
- Weather data integration
- Market price monitoring
- Government scheme updates

### 5. Explainable AI
- Confidence scoring for responses
- Source attribution
- Reasoning transparency

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **CrewAI** - For multi-agent orchestration
- **LangChain** - For LLM integration
- **FastAPI** - For high-performance API framework
- **Indian Agricultural Research Institute** - For agricultural data
- **OpenWeatherMap** - For weather data
- **Government of India** - For agricultural policies and schemes

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Contact the development team
- Check the documentation

---

**KrishiSetu** - Bridging the gap between technology and agriculture for a sustainable future! 🌾🤖
