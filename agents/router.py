
# ============================================
# agents/router.py
# ============================================
from models.state import AgentState
from config.settings import settings
from utils.validators import extract_keywords, clean_text
from typing import Literal, Dict
import logging

logger = logging.getLogger(__name__)

def classify_input(state: AgentState) -> Dict:
    """
    Classify the type of input (text-only, image-only, text+image).
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with input_type
    """
    image_path = state.get('image_path')
    text_query = state.get('text_query')
    
    # Clean text query if present
    if text_query:
        text_query = clean_text(text_query)
        if not text_query:  # If cleaning resulted in empty string
            text_query = None
    
    # Determine input type
    if image_path and not text_query:
        input_type = 'image_only'
        logger.info("Input classified as: image_only")
    elif text_query and not image_path:
        input_type = 'text_only'
        logger.info("Input classified as: text_only")
    elif text_query and image_path:
        input_type = 'text_and_image'
        logger.info("Input classified as: text_and_image")
    else:
        input_type = 'error'
        logger.warning("Input classification failed: no valid input")
    
    return {
        'input_type': input_type,
        'text_query': text_query  # Return cleaned version
    }

def route_to_agent(state: AgentState) -> Literal["agent_1_vision", "agent_2_faq", "clarification", "error"]:
    """
    Route to appropriate agent based on input classification and content analysis.
    
    Args:
        state: Current agent state
        
    Returns:
        Name of the next node to execute
    """
    input_type = state.get('input_type', 'error')
    text_query = state.get('text_query', '').lower()
    
    logger.info(f"Routing with input_type: {input_type}")
    
    # Handle error cases
    if input_type == 'error':
        logger.warning("Routing to error node")
        return "error"
    
    # Image only -> Always route to vision agent
    if input_type == 'image_only':
        logger.info("Routing to vision agent (image only)")
        return "agent_1_vision"
    
    # Text + Image -> Route to vision agent (maintenance query with visual)
    if input_type == 'text_and_image':
        logger.info("Routing to vision agent (text + image)")
        return "agent_1_vision"
    
    # Text only -> Need to determine which agent
    if input_type == 'text_only':
        # Extract keywords
        maintenance_kw = extract_keywords(text_query, settings.MAINTENANCE_KEYWORDS)
        tenancy_kw = extract_keywords(text_query, settings.TENANCY_KEYWORDS)
        
        logger.info(f"Found maintenance keywords: {maintenance_kw}")
        logger.info(f"Found tenancy keywords: {tenancy_kw}")
        
        # If tenancy keywords found, route to FAQ agent
        if tenancy_kw:
            logger.info("Routing to FAQ agent (tenancy keywords detected)")
            return "agent_2_faq"
        
        # If maintenance keywords found but no image, ask for clarification
        if maintenance_kw:
            logger.info("Routing to clarification (maintenance keywords but no image)")
            return "clarification"
        
        # Check for question patterns
        question_indicators = ['how', 'what', 'when', 'where', 'why', 'can', 'should', 'is', 'are', 'do', 'does']
        is_question = any(text_query.strip().startswith(indicator) for indicator in question_indicators) or '?' in text_query
        
        if is_question:
            # Default questions to FAQ agent
            logger.info("Routing to FAQ agent (question pattern detected)")
            return "agent_2_faq"
        else:
            # Ambiguous, ask for clarification
            logger.info("Routing to clarification (ambiguous query)")
            return "clarification"
    
    # Fallback
    logger.warning("Routing to error (fallback)")
    return "error"
