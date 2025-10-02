
# ============================================
# streamlit_app.py
# ============================================
"""
Streamlit web interface for the Real Estate Chatbot.
Run with: streamlit run streamlit_app.py
"""

import streamlit as st
import sys
from pathlib import Path
import tempfile
import os

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from graph.workflow import RealEstateChatbot
from models.inputs import UserQuery
from pydantic import ValidationError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="Real Estate Assistant",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .agent-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 0.25rem;
        font-size: 0.875rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .vision-badge {
        background-color: #d4edda;
        color: #155724;
    }
    .faq-badge {
        background-color: #cce5ff;
        color: #004085;
    }
    .clarification-badge {
        background-color: #fff3cd;
        color: #856404;
    }
    .error-badge {
        background-color: #f8d7da;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = RealEstateChatbot()
if 'history' not in st.session_state:
    st.session_state.history = []

# Header
st.markdown('<div class="main-header">🏠 Real Estate Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Property Issues & Tenancy Questions</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This AI assistant helps with:
    
    **🔧 Property Issues**
    - Upload images of property problems
    - Get expert troubleshooting advice
    - Learn when to call professionals
    
    **📋 Tenancy Law**
    - Ask about tenant/landlord rights
    - Understand lease agreements
    - Get location-specific guidance
    """)
    
    st.divider()
    
    st.header("⚙️ Settings")
    user_location = st.text_input(
        "Your Location (optional)",
        placeholder="e.g., New York, USA",
        help="Provide your location for location-specific tenancy advice"
    )
    
    st.divider()
    
    st.header("📊 Statistics")
    st.metric("Queries Processed", len(st.session_state.history))
    
    if st.button("Clear History"):
        st.session_state.history = []
        st.rerun()

def get_conversation_context(history, max_turns=3):
    """Get recent conversation context"""
    if not history:
        return ""
    
    recent = history[-max_turns:]
    context_parts = []
    for item in recent:
        context_parts.append(f"User: {item['query']}")
        context_parts.append(f"Assistant: {item['response'].response[:200]}...")
    
    return "\n".join(context_parts)

# Main interface
tab1, tab2 = st.tabs(["💬 Chat", "📚 Examples"])

with tab1:
    # Input section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        text_query = st.text_area(
            "Ask a question or describe a property issue:",
            placeholder="e.g., 'What's causing the water stains on my ceiling?' or 'Can my landlord increase rent?'",
            height=100
        )
    
    with col2:
        uploaded_file = st.file_uploader(
            "Upload property image (optional)",
            type=['jpg', 'jpeg', 'png', 'webp'],
            help="Upload an image of the property issue for visual analysis"
        )
        
        if uploaded_file:
            st.image(uploaded_file, caption="Uploaded Image", width='stretch')
    


    # Submit button
    if st.button("🚀 Get Help", type="primary", use_container_width=True):
        if not text_query and not uploaded_file:
            st.error("Please provide either a question or upload an image.")
        else:
            with st.spinner("Analyzing your query..."):
                try:
                    # Handle uploaded file
                    image_path = None
                    if uploaded_file:
                        # Save to temporary file
                        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            image_path = tmp_file.name
                    
                    # Create query
                    # Get conversation context
                    conversation_context = get_conversation_context(st.session_state.history)

                    # Create query with context
                    query_text = text_query if text_query else None
                    if conversation_context and query_text:
                        query_text = f"Previous conversation:\n{conversation_context}\n\nCurrent question: {query_text}"

                    query = UserQuery(
                        text_query=query_text,
                        image_path=image_path,
                        user_location=user_location if user_location else None
                    )
                    
                    # Get response
                    response = st.session_state.chatbot.process_query(query)
                    
                    # Add to history
                    st.session_state.history.append({
                        'query': text_query or "Image analysis",
                        'response': response,
                        'has_image': uploaded_file is not None
                    })
                    
                    # Clean up temp file
                    if image_path and os.path.exists(image_path):
                        try:
                            os.unlink(image_path)
                        except:
                            pass
                    
                    st.rerun()
                    
                except ValidationError as e:
                    st.error(f"❌ Validation Error: {str(e)}")
                except Exception as e:
                    logger.error(f"Error processing query: {e}", exc_info=True)
                    st.error(f"❌ Error: {str(e)}")
    
    # Display history
    st.divider()
    st.subheader("📜 Conversation History")
    
    if st.session_state.history:
        for i, item in enumerate(reversed(st.session_state.history)):
            response = item['response']
            
            # Agent badge
            badge_class = {
                'agent_1_vision': 'vision-badge',
                'agent_2_faq': 'faq-badge',
                'clarification': 'clarification-badge',
                'error': 'error-badge'
            }.get(response.agent_used, 'faq-badge')
            
            agent_name = {
                'agent_1_vision': '🔧 Property Inspector',
                'agent_2_faq': '📋 Tenancy Expert',
                'clarification': '❓ Clarification',
                'error': '❌ Error'
            }.get(response.agent_used, 'Assistant')
            
            with st.expander(f"Query {len(st.session_state.history) - i}: {item['query'][:60]}...", expanded=(i==0)):
                st.markdown(f'<span class="agent-badge {badge_class}">{agent_name}</span>', unsafe_allow_html=True)
                
                if item['has_image']:
                    st.info("🖼️ Image was provided with this query")
                
                st.markdown(f"**Your Query:** {item['query']}")
                st.markdown("**Response:**")
                st.write(response.response)
                
                if response.detected_issues:
                    st.markdown("**🔍 Detected Issues:**")
                    for issue in response.detected_issues:
                        st.markdown(f"- {issue}")
                
                if response.suggestions:
                    st.markdown("**💡 Suggestions:**")
                    for j, suggestion in enumerate(response.suggestions, 1):
                        st.markdown(f"{j}. {suggestion}")
                
                if response.confidence_score:
                    st.progress(response.confidence_score, text=f"Confidence: {response.confidence_score:.0%}")
                
                if response.needs_clarification:
                    st.warning("⚠️ More information may be helpful for a complete answer.")
    else:
        st.info("👋 No queries yet. Ask a question or upload an image to get started!")

with tab2:
    st.header("📚 Example Queries")
    st.markdown("Here are some example queries you can try:")
    
    st.subheader("🔧 Property Issues (with images)")
    examples_property = [
        "What's wrong with this wall?",
        "Is this mold on my ceiling?",
        "What's causing these cracks?",
        "I found water stains - what should I do?",
        "Is this electrical issue dangerous?"
    ]
    
    for ex in examples_property:
        st.markdown(f"- {ex}")
    
    st.divider()
    
    st.subheader("📋 Tenancy Questions")
    examples_tenancy = [
        "Can my landlord evict me without notice?",
        "How much notice do I need to give before vacating?",
        "Can my landlord increase rent during my lease?",
        "What if my landlord is not returning my deposit?",
        "Who is responsible for repairs - landlord or tenant?",
        "Can I sublet my apartment?",
        "What are my privacy rights as a tenant?",
        "Can I withhold rent for needed repairs?",
        "How do I break my lease early?",
        "What makes a rental unit uninhabitable?"
    ]
    
    for ex in examples_tenancy:
        st.markdown(f"- {ex}")
    
    st.divider()
    
    st.info("""
    **💡 Tips:**
    - For property issues, always try to include a clear image
    - For tenancy questions, include your location for specific advice
    - Be as detailed as possible in your description
    """)

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.875rem;">
    <p>🏠 Real Estate Multi-Agent Assistant | Built with LangGraph & Groq</p>
    <p>⚠️ Disclaimer: This is for informational purposes only. Consult professionals for specific legal or property advice.</p>
</div>
""", unsafe_allow_html=True)
