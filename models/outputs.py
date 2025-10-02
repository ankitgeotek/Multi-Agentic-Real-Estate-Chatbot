
# ============================================
# models/outputs.py
# ============================================
from pydantic import BaseModel, Field
from typing import Optional, List, Literal

class AgentResponse(BaseModel):
    """Structured output from the chatbot"""
    
    response: str = Field(description="The agent's response to the user")
    agent_used: Literal['agent_1_vision', 'agent_2_faq', 'clarification', 'error'] = Field(
        description="Which agent handled the query"
    )
    needs_clarification: bool = Field(
        default=False,
        description="Whether the bot needs more information"
    )
    detected_issues: Optional[List[str]] = Field(
        default=None,
        description="List of property issues detected (for vision agent)"
    )
    confidence_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Confidence score of the response"
    )
    suggestions: Optional[List[str]] = Field(
        default=None,
        description="List of actionable suggestions"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "I can see water damage on the ceiling...",
                "agent_used": "agent_1_vision",
                "needs_clarification": False,
                "detected_issues": ["water damage", "paint peeling"],
                "confidence_score": 0.85,
                "suggestions": ["Check for roof leaks", "Contact a plumber"]
            }
        }

class ErrorResponse(BaseModel):
    """Error response model"""
    
    error: bool = True
    message: str
    error_type: str
    details: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": True,
                "message": "Invalid image format",
                "error_type": "ValidationError",
                "details": "Only JPG, PNG, and WEBP formats are supported"
            }
        }
