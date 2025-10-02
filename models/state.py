
# ============================================
# models/state.py
# ============================================
from typing_extensions import TypedDict
from typing import Optional, List, Dict, Annotated
import operator

class AgentState(TypedDict, total=False):
    """
    State schema for LangGraph workflow.
    All fields are optional to handle various input scenarios.
    """
    
    # Input fields
    text_query: Optional[str]
    image_path: Optional[str]
    user_location: Optional[str]
    
    # Processing fields
    base64_image: Optional[str]
    input_type: Optional[str]  # 'text_only', 'image_only', 'text_and_image', 'error'
    
    # Output fields
    agent_response: Optional[str]
    agent_used: Optional[str]
    detected_issues: Optional[List[str]]
    suggestions: Optional[List[str]]
    confidence_score: Optional[float]
    
    # Control fields
    needs_clarification: Optional[bool]
    error_message: Optional[str]
    error_type: Optional[str]
    
    # Conversation history (with reducer for appending)
    messages: Annotated[List[Dict], operator.add]

