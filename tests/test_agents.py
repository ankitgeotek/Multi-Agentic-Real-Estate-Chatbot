
# ============================================
# tests/test_agents.py
# ============================================
"""
Unit tests for the Real Estate Chatbot agents.
Run with: pytest tests/test_agents.py -v
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.inputs import UserQuery
from models.state import AgentState
from graph.workflow import RealEstateChatbot
from agents.router import classify_input, route_to_agent
from pydantic import ValidationError

class TestInputValidation:
    """Test input validation"""
    
    def test_valid_text_only_query(self):
        """Test valid text-only query"""
        query = UserQuery(text_query="Can my landlord evict me?")
        assert query.text_query == "Can my landlord evict me?"
        assert query.image_path is None
    
    def test_valid_image_path_validation(self):
        """Test that image path must exist"""
        with pytest.raises(ValidationError):
            UserQuery(image_path="/nonexistent/path/image.jpg")
    
    def test_empty_query_rejected(self):
        """Test that empty query is rejected"""
        with pytest.raises(ValidationError):
            UserQuery()
    
    def test_text_too_long(self):
        """Test that overly long text is rejected"""
        long_text = "a" * 1001
        with pytest.raises(ValidationError):
            UserQuery(text_query=long_text)
    
    def test_location_optional(self):
        """Test that location is optional"""
        query = UserQuery(
            text_query="Test query",
            user_location="New York"
        )
        assert query.user_location == "New York"

class TestClassification:
    """Test input classification logic"""
    
    def test_classify_text_only(self):
        """Test text-only classification"""
        state = {'text_query': 'Can my landlord evict me?'}
        result = classify_input(state)
        assert result['input_type'] == 'text_only'
    
    def test_classify_image_only(self):
        """Test image-only classification"""
        state = {'image_path': '/some/path.jpg'}
        result = classify_input(state)
        assert result['input_type'] == 'image_only'
    
    def test_classify_text_and_image(self):
        """Test text+image classification"""
        state = {
            'text_query': 'What is this?',
            'image_path': '/some/path.jpg'
        }
        result = classify_input(state)
        assert result['input_type'] == 'text_and_image'
    
    def test_classify_empty(self):
        """Test empty input classification"""
        state = {}
        result = classify_input(state)
        assert result['input_type'] == 'error'

class TestRouting:
    """Test agent routing logic"""
    
    def test_route_image_only_to_vision(self):
        """Test that image-only routes to vision agent"""
        state = {'input_type': 'image_only'}
        result = route_to_agent(state)
        assert result == 'agent_1_vision'
    
    def test_route_text_image_to_vision(self):
        """Test that text+image routes to vision agent"""
        state = {
            'input_type': 'text_and_image',
            'text_query': 'what is this crack?'
        }
        result = route_to_agent(state)
        assert result == 'agent_1_vision'
    
    def test_route_tenancy_keywords_to_faq(self):
        """Test that tenancy keywords route to FAQ agent"""
        state = {
            'input_type': 'text_only',
            'text_query': 'can my landlord evict me?'
        }
        result = route_to_agent(state)
        assert result == 'agent_2_faq'
    
    def test_route_maintenance_keywords_to_clarification(self):
        """Test that maintenance keywords without image route to clarification"""
        state = {
            'input_type': 'text_only',
            'text_query': 'i have a crack in my wall'
        }
        result = route_to_agent(state)
        assert result == 'clarification'
    
    def test_route_error(self):
        """Test error routing"""
        state = {'input_type': 'error'}
        result = route_to_agent(state)
        assert result == 'error'

class TestChatbotIntegration:
    """Integration tests for full chatbot workflow"""
    
    def test_chatbot_initialization(self):
        """Test that chatbot initializes correctly"""
        chatbot = RealEstateChatbot()
        assert chatbot.workflow is not None
    
    def test_tenancy_query_processing(self):
        """Test processing a tenancy question"""
        chatbot = RealEstateChatbot()
        query = UserQuery(
            text_query="Can my landlord increase rent during my lease?"
        )
        response = chatbot.process_query(query)
        
        assert response is not None
        assert response.agent_used in ['agent_2_faq', 'clarification']
        assert len(response.response) > 0
    
    def test_maintenance_query_without_image(self):
        """Test maintenance query without image triggers clarification"""
        chatbot = RealEstateChatbot()
        query = UserQuery(text_query="I have a leak")
        response = chatbot.process_query(query)
        
        assert response.agent_used == 'clarification'
        assert response.needs_clarification == True
    
    def test_error_handling(self):
        """Test that errors are handled gracefully"""
        chatbot = RealEstateChatbot()
        # This should handle the error gracefully
        result = chatbot.process_query_dict({})
        
        assert 'error' in result.get('agent_used', '')

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
