
# ============================================
# agents/faq_agent.py
# ============================================
from langchain_groq import ChatGroq
from models.state import AgentState
from agents.prompts import FAQ_AGENT_SYSTEM_PROMPT, FAQ_AGENT_USER_TEMPLATE
from config.settings import settings
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class FAQAgent:
    """Tenancy FAQ Agent for rental and legal questions"""
    
    def __init__(self):
        self.model = ChatGroq(
            model=settings.TEXT_MODEL,
            api_key=settings.GROQ_API_KEY,
            temperature=0.2  # Lower temperature for factual, consistent answers
        )
    
    def process(self, state: AgentState) -> Dict:
        """
        Process tenancy-related questions.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state dict with response
        """
        try:
            # Get user query
            user_query = state.get('text_query', '')
            if not user_query:
                return self._error_response("No question provided")
            
            # Get user location if provided
            user_location = state.get('user_location', '')
            location_context = ""
            if user_location:
                location_context = f"User's location: {user_location}\nPlease provide location-specific guidance when applicable."
            else:
                location_context = "Note: User has not provided their location. If the answer varies by location, please ask for their location and provide general guidance."
            
            # Format the user message
            user_message = FAQ_AGENT_USER_TEMPLATE.format(
                query=user_query,
                location_context=location_context
            )
            
            # Create messages
            messages = [
                {"role": "system", "content": FAQ_AGENT_SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ]
            
            # Get response
            logger.info("Calling FAQ agent for tenancy question")
            response = self.model.invoke(messages)
            
            # Check if needs location clarification
            needs_clarification = self._check_needs_location(response.content, user_location)
            
            # Extract suggestions
            suggestions = self._extract_suggestions(response.content)
            
            return {
                'agent_response': response.content,
                'agent_used': 'agent_2_faq',
                'suggestions': suggestions,
                'confidence_score': 0.9,
                'needs_clarification': needs_clarification
            }
            
        except Exception as e:
            logger.error(f"FAQ agent error: {str(e)}", exc_info=True)
            return self._error_response(f"Error processing question: {str(e)}")
    
    def _check_needs_location(self, response: str, user_location: str) -> bool:
        """Check if response indicates need for location information"""
        if user_location:
            return False
        
        location_indicators = [
            'location', 'jurisdiction', 'state', 'country', 
            'where you live', 'your area', 'depends on'
        ]
        
        return any(indicator in response.lower() for indicator in location_indicators)
    
    def _extract_suggestions(self, response_text: str) -> list:
        """Extract actionable suggestions from response"""
        suggestions = []
        lines = response_text.split('\n')
        
        for line in lines:
            line = line.strip()
            # Look for actionable advice patterns
            if any(marker in line.lower() for marker in ['should', 'recommend', 'consider', 'contact', 'document', 'keep', 'file']):
                if len(line) > 20 and len(line) < 200:
                    suggestions.append(line)
        
        return suggestions[:5]
    
    def _error_response(self, error_message: str) -> Dict:
        """Create error response"""
        return {
            'agent_response': error_message,
            'agent_used': 'agent_2_faq',
            'error_message': error_message,
            'error_type': 'FAQAgentError',
            'needs_clarification': True
        }
