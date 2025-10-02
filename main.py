
# ============================================
# main.py
# ============================================
"""
Main entry point for the Real Estate Chatbot.
Demonstrates usage and provides CLI interface.
"""

import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from graph.workflow import RealEstateChatbot
from models.inputs import UserQuery
from pydantic import ValidationError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chatbot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def print_response(response):
    """Pretty print the response"""
    print("\n" + "="*80)
    print(f"AGENT: {response.agent_used.upper()}")
    print("="*80)
    print(f"\n{response.response}\n")
    
    if response.detected_issues:
        print("DETECTED ISSUES:")
        for issue in response.detected_issues:
            print(f"  - {issue}")
        print()
    
    if response.suggestions:
        print("SUGGESTIONS:")
        for i, suggestion in enumerate(response.suggestions, 1):
            print(f"  {i}. {suggestion}")
        print()
    
    if response.confidence_score:
        print(f"Confidence: {response.confidence_score:.2%}")
    
    if response.needs_clarification:
        print("\n⚠️  More information may be needed for a complete answer.")
    
    print("="*80 + "\n")

def run_examples():
    """Run example queries to demonstrate the chatbot"""
    
    print("\n🏠 MULTI-AGENT REAL ESTATE CHATBOT DEMO")
    print("="*80 + "\n")
    
    # Initialize chatbot
    chatbot = RealEstateChatbot()
    
    # Example 1: Image only (property issue)
    print("\n📷 EXAMPLE 1: Image-only property analysis")
    print("-" * 80)
    
    # Note: Replace with actual image path for testing
    try:
        query1 = UserQuery(
            image_path="/path/to/test/wall_damage.jpg"
        )
        response1 = chatbot.process_query(query1)
        print_response(response1)
    except ValidationError as e:
        print(f"⚠️  Skipping Example 1: {e}")
        print("   (Please provide a valid image path for testing)\n")
    
    # Example 2: Text only (tenancy FAQ)
    print("\n💬 EXAMPLE 2: Tenancy law question")
    print("-" * 80)
    
    query2 = UserQuery(
        text_query="Can my landlord evict me without giving notice?",
        user_location="California, USA"
    )
    response2 = chatbot.process_query(query2)
    print_response(response2)
    
    # Example 3: Text + Image (maintenance with context)
    print("\n🖼️ EXAMPLE 3: Property issue with description")
    print("-" * 80)
    
    try:
        query3 = UserQuery(
            text_query="I found these dark spots on my bathroom ceiling. What could be causing this?",
            image_path="/path/to/test/ceiling_stains.jpg"
        )
        response3 = chatbot.process_query(query3)
        print_response(response3)
    except ValidationError as e:
        print(f"⚠️  Skipping Example 3: {e}")
        print("   (Please provide a valid image path for testing)\n")
    
    # Example 4: Text only (tenancy question)
    print("\n📋 EXAMPLE 4: Security deposit question")
    print("-" * 80)
    
    query4 = UserQuery(
        text_query="How long does my landlord have to return my security deposit after I move out?"
    )
    response4 = chatbot.process_query(query4)
    print_response(response4)
    
    # Example 5: Maintenance keyword without image (triggers clarification)
    print("\n❓ EXAMPLE 5: Maintenance question without image")
    print("-" * 80)
    
    query5 = UserQuery(
        text_query="I have a crack in my wall"
    )
    response5 = chatbot.process_query(query5)
    print_response(response5)
    
    # Example 6: Rent increase question with location
    print("\n🏘️ EXAMPLE 6: Location-specific tenancy question")
    print("-" * 80)
    
    query6 = UserQuery(
        text_query="Can my landlord increase rent in the middle of my lease?",
        user_location="New York City, USA"
    )
    response6 = chatbot.process_query(query6)
    print_response(response6)

def interactive_mode():
    """Run chatbot in interactive CLI mode"""
    
    print("\n🏠 REAL ESTATE CHATBOT - Interactive Mode")
    print("="*80)
    print("Ask questions about property issues or tenancy laws!")
    print("Commands:")
    print("  - Type your question")
    print("  - Type 'image:path/to/image.jpg' to upload an image")
    print("  - Type 'quit' or 'exit' to stop")
    print("="*80 + "\n")
    
    chatbot = RealEstateChatbot()
    
    while True:
        try:
            user_input = input("\n💬 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye! Thanks for using Real Estate Chatbot.\n")
                break
            
            if not user_input:
                continue
            
            # Parse input
            image_path = None
            text_query = user_input
            
            if user_input.startswith('image:'):
                parts = user_input.split('image:', 1)
                if len(parts) > 1:
                    image_path = parts[1].strip()
                    text_query = input("   Describe the issue (optional): ").strip() or None
            
            # Create query
            query = UserQuery(
                text_query=text_query if text_query else None,
                image_path=image_path
            )
            
            # Get response
            response = chatbot.process_query(query)
            
            # Print response
            print(f"\n🤖 Bot ({response.agent_used}):")
            print(f"{response.response}")
            
            if response.detected_issues:
                print(f"\n📋 Detected Issues: {', '.join(response.detected_issues)}")
            
            if response.suggestions:
                print(f"\n💡 Suggestions:")
                for i, sug in enumerate(response.suggestions, 1):
                    print(f"   {i}. {sug}")
            
        except ValidationError as e:
            print(f"\n❌ Error: {e}")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            logger.error(f"Error in interactive mode: {e}", exc_info=True)
            print(f"\n❌ An error occurred: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Real Estate Multi-Agent Chatbot")
    parser.add_argument('--demo', action='store_true', help='Run demo examples')
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    parser.add_argument('--query', type=str, help='Single query to process')
    parser.add_argument('--image', type=str, help='Image path for query')
    parser.add_argument('--location', type=str, help='User location for tenancy questions')
    
    args = parser.parse_args()
    
    try:
        if args.demo:
            run_examples()
        elif args.interactive:
            interactive_mode()
        elif args.query or args.image:
            # Single query mode
            chatbot = RealEstateChatbot()
            query = UserQuery(
                text_query=args.query,
                image_path=args.image,
                user_location=args.location
            )
            response = chatbot.process_query(query)
            print_response(response)
        else:
            # Default: show help
            parser.print_help()
            print("\n💡 Try:")
            print("  python main.py --demo           # Run example queries")
            print("  python main.py --interactive    # Interactive chat mode")
            print("  python main.py --query 'Can my landlord evict me?'")
            
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!\n")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n❌ Fatal error: {e}\n")# Multi-Agent Real Estate Chatbot
