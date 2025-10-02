
# ============================================
# agents/vision_agent.py
# ============================================
from langchain_groq import ChatGroq
from models.state import AgentState
from utils.image_utils import encode_image, validate_image
from agents.prompts import VISION_AGENT_SYSTEM_PROMPT, VISION_AGENT_USER_TEMPLATE
from config.settings import settings
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class VisionAgent:
    """Property Issue Detection & Troubleshooting Agent"""
    
    def __init__(self):
        self.model = ChatGroq(
            model=settings.VISION_MODEL,
            api_key=settings.GROQ_API_KEY,
            temperature=0.3  # Lower temperature for more consistent technical analysis
        )
    
    def process(self, state: AgentState) -> Dict:
        """
        Process image and provide property issue analysis.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state dict with response
        """
        try:
            # Validate and encode image
            image_path = state.get('image_path')
            if not image_path:
                return self._error_response("No image provided")
            
            # Validate image
            is_valid, error_msg = validate_image(image_path)
            if not is_valid:
                return self._error_response(error_msg)
            
            # Encode image if not already encoded
            if not state.get('base64_image'):
                try:
                    base64_image = encode_image(image_path)
                except Exception as e:
                    logger.error(f"Image encoding failed: {str(e)}")
                    return self._error_response(f"Failed to process image: {str(e)}")
            else:
                base64_image = state['base64_image']
            
            # Prepare user query
            user_query = state.get('text_query', 'Please analyze this property image and identify any issues.')
            user_message = VISION_AGENT_USER_TEMPLATE.format(query=user_query)
            
            # Create messages for vision model
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"{VISION_AGENT_SYSTEM_PROMPT}\n\n{user_message}"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ]
            
            # Get response from vision model
            logger.info("Calling vision model for image analysis")
            response = self.model.invoke(messages)
            
            # Extract detected issues and suggestions (basic parsing)
            detected_issues = self._extract_issues(response.content)
            suggestions = self._extract_suggestions(response.content)
            
            return {
                'agent_response': response.content,
                'agent_used': 'agent_1_vision',
                'base64_image': base64_image,
                'detected_issues': detected_issues,
                'suggestions': suggestions,
                'confidence_score': 0.85,  # Could be calculated based on response quality
                'needs_clarification': False
            }
            
        except Exception as e:
            logger.error(f"Vision agent error: {str(e)}", exc_info=True)
            return self._error_response(f"Error analyzing image: {str(e)}")
    
    def _extract_issues(self, response_text: str) -> list:
        """Extract detected issues from response (basic keyword extraction)"""
        issues = []
        issue_keywords = ['crack', 'leak', 'damage', 'mold', 'mould', 'stain', 
                         'broken', 'deterioration', 'corrosion', 'damp']
        
        for keyword in issue_keywords:
            if keyword in response_text.lower():
                issues.append(keyword)
        
        return list(set(issues))[:5]  # Return up to 5 unique issues
    
    def _extract_suggestions(self, response_text: str) -> list:
        """Extract suggestions from response (basic extraction)"""
        suggestions = []
        lines = response_text.split('\n')
        
        for line in lines:
            line = line.strip()
            # Look for recommendation patterns
            if any(marker in line.lower() for marker in ['recommend', 'should', 'suggest', 'contact', 'call']):
                if len(line) > 20 and len(line) < 200:  # Reasonable suggestion length
                    suggestions.append(line)
        
        return suggestions[:5]  # Return up to 5 suggestions
    
    def _error_response(self, error_message: str) -> Dict:
        """Create error response"""
        return {
            'agent_response': error_message,
            'agent_used': 'agent_1_vision',
            'error_message': error_message,
            'error_type': 'VisionAgentError',
            'needs_clarification': True
        }