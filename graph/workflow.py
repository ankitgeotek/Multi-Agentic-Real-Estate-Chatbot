
# ============================================
# graph/workflow.py
# ============================================
from langgraph.graph import StateGraph, START, END
from models.state import AgentState
from models.inputs import UserQuery
from models.outputs import AgentResponse, ErrorResponse
from agents.vision_agent import VisionAgent
from agents.faq_agent import FAQAgent
from agents.router import classify_input, route_to_agent
from agents.prompts import CLARIFICATION_PROMPT, ERROR_MESSAGES
import logging
from typing import Dict

logger = logging.getLogger(__name__)

# Initialize agents
vision_agent = VisionAgent()
faq_agent = FAQAgent()

def agent_1_vision_node(state: AgentState) -> Dict:
    """Vision agent node wrapper"""
    logger.info("Executing vision agent node")
    return vision_agent.process(state)

def agent_2_faq_node(state: AgentState) -> Dict:
    """FAQ agent node wrapper"""
    logger.info("Executing FAQ agent node")
    return faq_agent.process(state)

def clarification_node(state: AgentState) -> Dict:
    """Clarification node - asks user for more information"""
    logger.info("Executing clarification node")
    return {
        'agent_response': CLARIFICATION_PROMPT,
        'agent_used': 'clarification',
        'needs_clarification': True,
        'confidence_score': 1.0
    }

def error_node(state: AgentState) -> Dict:
    """Error handling node"""
    logger.info("Executing error node")
    
    error_msg = state.get('error_message')
    if not error_msg:
        error_msg = ERROR_MESSAGES['no_input']
    
    return {
        'agent_response': error_msg,
        'agent_used': 'error',
        'error_message': error_msg,
        'error_type': state.get('error_type', 'UnknownError'),
        'needs_clarification': True
    }

def create_workflow() -> StateGraph:
    """
    Create and compile the LangGraph workflow.
    
    Returns:
        Compiled workflow
    """
    logger.info("Creating workflow graph")
    
    # Initialize graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("classify_input", classify_input)
    workflow.add_node("agent_1_vision", agent_1_vision_node)
    workflow.add_node("agent_2_faq", agent_2_faq_node)
    workflow.add_node("clarification", clarification_node)
    workflow.add_node("error", error_node)
    
    # Add edges
    workflow.add_edge(START, "classify_input")
    
    # Add conditional routing from classification
    workflow.add_conditional_edges(
        "classify_input",
        route_to_agent,
        {
            "agent_1_vision": "agent_1_vision",
            "agent_2_faq": "agent_2_faq",
            "clarification": "clarification",
            "error": "error"
        }
    )
    
    # All terminal nodes connect to END
    workflow.add_edge("agent_1_vision", END)
    workflow.add_edge("agent_2_faq", END)
    workflow.add_edge("clarification", END)
    workflow.add_edge("error", END)
    
    # Compile
    app = workflow.compile()
    logger.info("Workflow compiled successfully")
    
    return app

class RealEstateChatbot:
    """
    Main chatbot interface with input validation and error handling.
    """
    
    def __init__(self):
        self.workflow = create_workflow()
        logger.info("RealEstateChatbot initialized")
    
    def process_query(self, user_input: UserQuery) -> AgentResponse:
        """
        Process user query with full validation and error handling.
        
        Args:
            user_input: Validated user input (Pydantic model)
            
        Returns:
            AgentResponse with results
        """
        try:
            # Convert Pydantic model to dict
            input_dict = user_input.model_dump(exclude_none=True)
            
            # Add empty messages list for conversation tracking
            if 'messages' not in input_dict:
                input_dict['messages'] = []
            
            logger.info(f"Processing query: {input_dict.get('text_query', 'image-only')}")
            
            # Invoke workflow
            result = self.workflow.invoke(input_dict)
            
            # Create response
            response = AgentResponse(
                response=result.get('agent_response', 'No response generated'),
                agent_used=result.get('agent_used', 'error'),
                needs_clarification=result.get('needs_clarification', False),
                detected_issues=result.get('detected_issues'),
                confidence_score=result.get('confidence_score'),
                suggestions=result.get('suggestions')
            )
            
            logger.info(f"Query processed successfully by {response.agent_used}")
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}", exc_info=True)
            return AgentResponse(
                response=f"I encountered an error: {str(e)}. Please try again.",
                agent_used='error',
                needs_clarification=True,
                confidence_score=0.0
            )
    
    def process_query_dict(self, query_dict: dict) -> dict:
        """
        Process query from dictionary (for testing).
        
        Args:
            query_dict: Dictionary with query parameters
            
        Returns:
            Result dictionary
        """
        try:
            # Validate with Pydantic
            user_query = UserQuery(**query_dict)
            response = self.process_query(user_query)
            return response.model_dump()
        except Exception as e:
            logger.error(f"Error in process_query_dict: {str(e)}")
            return {
                'response': f"Validation error: {str(e)}",
                'agent_used': 'error',
                'needs_clarification': True
            }
