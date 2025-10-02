
# ============================================
# README.md
# ============================================
"""
# 🏠 Multi-Agent Real Estate Chatbot

A sophisticated AI-powered chatbot system with specialized agents for property issue detection and tenancy law questions.

## 📋 Overview

This project implements a multi-agent chatbot system capable of:

1. **Property Issue Detection & Troubleshooting** (Agent 1)
   - Analyzes property images to detect issues
   - Provides troubleshooting advice
   - Recommends professional services when needed

2. **Tenancy Law FAQ** (Agent 2)
   - Answers rental and lease questions
   - Provides location-specific guidance
   - Covers landlord-tenant rights and responsibilities

## 🏗️ Architecture

### Multi-Agent System
- **Router/Manager**: Classifies inputs and routes to appropriate agent
- **Agent 1 (Vision)**: Handles image-based property analysis
- **Agent 2 (FAQ)**: Handles text-based tenancy questions
- **Clarification Handler**: Requests additional information when needed
- **Error Handler**: Manages edge cases and errors

### Technology Stack
- **Framework**: LangGraph for agent orchestration
- **LLM Provider**: Groq (Llama models)
- **Vision Model**: Llama 4 Scout 17B
- **Text Model**: Llama 3.3 70B
- **Validation**: Pydantic for type safety
- **UI**: Streamlit for web interface

## 📁 Project Structure

```
real_estate_chatbot/
├── config/
│   └── settings.py          # Configuration and environment variables
├── models/
│   ├── inputs.py            # Input validation schemas
│   ├── outputs.py           # Output response schemas
│   └── state.py             # LangGraph state definition
├── agents/
│   ├── vision_agent.py      # Property inspection agent
│   ├── faq_agent.py         # Tenancy FAQ agent
│   ├── router.py            # Input classification and routing
│   └── prompts.py           # System prompts for agents
├── graph/
│   └── workflow.py          # LangGraph workflow definition
├── utils/
│   ├── image_utils.py       # Image processing utilities
│   └── validators.py        # Text validation utilities
├── data/
│   └── tenancy_faqs.txt     # Knowledge base for FAQs
├── tests/
│   └── test_agents.py       # Unit tests
├── main.py                  # CLI interface
├── streamlit_app.py         # Web UI
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## 🚀 Installation

### Prerequisites
- Python 3.9+
- Groq API Key

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd real_estate_chatbot
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
Create a `.env` file in the project root:
```env
GROQ_API_KEY=your_groq_api_key_here
```

## 💻 Usage

### Method 1: Streamlit Web Interface (Recommended)

```bash
streamlit run streamlit_app.py
```

Then open http://localhost:8501 in your browser.

**Features:**
- Upload images for property analysis
- Ask tenancy questions
- View conversation history
- Get location-specific advice

### Method 2: Command Line Interface

**Run demo examples:**
```bash
python main.py --demo
```

**Interactive mode:**
```bash
python main.py --interactive
```

**Single query:**
```bash
# Text query
python main.py --query "Can my landlord evict me without notice?"

# With location
python main.py --query "Can rent be increased mid-lease?" --location "California, USA"

# With image
python main.py --query "What's wrong with this wall?" --image path/to/wall.jpg
```

### Method 3: Python API

```python
from graph.workflow import RealEstateChatbot
from models.inputs import UserQuery

# Initialize chatbot
chatbot = RealEstateChatbot()

# Example 1: Tenancy question
query = UserQuery(
    text_query="How much notice do I need before vacating?",
    user_location="New York, USA"
)
response = chatbot.process_query(query)
print(response.response)

# Example 2: Property issue with image
query = UserQuery(
    text_query="What's causing these stains?",
    image_path="path/to/ceiling.jpg"
)
response = chatbot.process_query(query)
print(response.response)
print(response.detected_issues)
print(response.suggestions)
```

## 🧪 Testing

Run the test suite:

```bash
# Install pytest if not already installed
pip install pytest

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_agents.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

## 🔄 How It Works

### 1. Input Classification
```
User Input → classify_input() → Determines input type:
- text_only
- image_only
- text_and_image
- error
```

### 2. Agent Routing
```
Input Type + Content Analysis → route_to_agent() → Routes to:
- agent_1_vision: Property issues (has image)
- agent_2_faq: Tenancy questions (keywords detected)
- clarification: Needs more info
- error: Invalid input
```

### 3. Agent Processing
```
Selected Agent → Processes query → Returns:
- Response text
- Detected issues (vision agent)
- Suggestions
- Confidence score
- Clarification needs
```

### 4. Response Formatting
```
Agent Output → Pydantic validation → AgentResponse:
- response: str
- agent_used: str
- needs_clarification: bool
- detected_issues: List[str]
- suggestions: List[str]
- confidence_score: float
```

## 🎯 Use Cases Covered

### Property Issues (Agent 1)
✅ Water damage detection  
✅ Crack analysis  
✅ Mold identification  
✅ Paint problems  
✅ Structural issues  
✅ Electrical hazards  
✅ Plumbing problems  
✅ General maintenance  

### Tenancy Questions (Agent 2)
✅ Eviction procedures  
✅ Notice periods  
✅ Rent increases  
✅ Security deposits  
✅ Lease termination  
✅ Repair responsibilities  
✅ Privacy rights  
✅ Subletting rules  
✅ Habitability standards  

## 🔍 Edge Cases Handled

1. **No input provided**: Returns error message
2. **Invalid image format**: Validation error with helpful message
3. **Image too large**: Size validation (max 10MB)
4. **Maintenance query without image**: Asks user to upload image
5. **Ambiguous query**: Routes to clarification
6. **Location-specific question without location**: Asks for location
7. **API errors**: Graceful error handling with retry suggestions
8. **Empty/whitespace-only text**: Cleaned and validated
9. **Mixed signals**: Prioritizes image presence for routing
10. **Non-property images**: Vision agent can identify and redirect

## 📊 Performance Considerations

- **Image size limit**: 10MB (configurable)
- **Text length limit**: 1000 characters
- **Response time**: 2-5 seconds typical
- **Supported formats**: JPG, PNG, WEBP
- **Temperature settings**:
  - Vision agent: 0.3 (more consistent)
  - FAQ agent: 0.2 (more factual)

## 🛠️ Configuration

Edit `config/settings.py` to customize:

```python
# Model selection
TEXT_MODEL = 'llama-3.3-70b-versatile'
VISION_MODEL = 'meta-llama/llama-4-scout-17b-16e-instruct'

# File constraints
MAX_IMAGE_SIZE_MB = 10
ALLOWED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.webp']
MAX_QUERY_LENGTH = 1000

# Keywords for routing
MAINTENANCE_KEYWORDS = ['crack', 'leak', 'damage', ...]
TENANCY_KEYWORDS = ['landlord', 'tenant', 'rent', ...]
```

## 🐛 Troubleshooting

### Common Issues

**1. "GROQ_API_KEY not found"**
- Ensure `.env` file exists with valid API key
- Check file is in project root directory

**2. "Image file not found"**
- Verify image path is correct and absolute
- Check file permissions

**3. "Module not found" errors**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

**4. Streamlit not starting**
- Check port 8501 is not in use
- Try `streamlit run streamlit_app.py --server.port 8502`

### Logging

Check `chatbot.log` for detailed error messages:
```bash
tail -f chatbot.log
```

## 📝 Deliverables Checklist

✅ Working chatbot with both agents  
✅ Image analysis capability  
✅ Text-based FAQ handling  
✅ Agent routing logic  
✅ Input validation  
✅ Error handling  
✅ Web interface (Streamlit)  
✅ CLI interface  
✅ Unit tests  
✅ Documentation  
✅ Example usage  
✅ Edge case handling  

## 🎥 Demo Video

For submission, record a video demonstrating:
1. Property image analysis (Agent 1)
2. Tenancy question answering (Agent 2)
3. Clarification flow
4. Error handling
5. Both text-only and image+text scenarios

Upload to Google Drive and ensure public access.

## 📄 License

This project is created as a POC for demonstration purposes.

## 👥 Contact

For questions or issues, please contact the development team.

---

**Built with ❤️ using LangGraph, Groq, and Streamlit**
"""            'needs_clarification': True
        
