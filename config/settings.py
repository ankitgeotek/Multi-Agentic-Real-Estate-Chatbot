
# ============================================
# config/settings.py
# ============================================
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

class Settings:
    """Application settings and configuration"""
    
    # API Keys
    GROQ_API_KEY: str = os.getenv('GROQ_API_KEY', '')
    
    # Model configurations
    TEXT_MODEL: str = 'llama-3.3-70b-versatile'
    VISION_MODEL: str = 'meta-llama/llama-4-scout-17b-16e-instruct'
    
    # File constraints
    MAX_IMAGE_SIZE_MB: int = 10
    ALLOWED_IMAGE_FORMATS: list = ['.jpg', '.jpeg', '.png', '.webp']
    MAX_QUERY_LENGTH: int = 1000
    
    # Agent configurations
    MAINTENANCE_KEYWORDS: list = [
        'crack', 'leak', 'damage', 'broken', 'mold', 'mould',
        'wall', 'ceiling', 'paint', 'floor', 'window', 'door',
        'water', 'damp', 'stain', 'peeling', 'fixture', 'plumbing'
    ]
    
    TENANCY_KEYWORDS: list = [
        'landlord', 'tenant', 'rent', 'deposit', 'evict', 'eviction',
        'lease', 'contract', 'notice', 'agreement', 'rental',
        'tenancy', 'security deposit', 'vacate', 'termination'
    ]
    
    # Paths
    DATA_DIR: Path = BASE_DIR / 'data'
    TENANCY_FAQ_FILE: Path = DATA_DIR / 'tenancy_faqs.txt'
    
    @classmethod
    def validate(cls):
        """Validate that required settings are present"""
        if not cls.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        # Create data directory if it doesn't exist
        cls.DATA_DIR.mkdir(exist_ok=True)

settings = Settings()
settings.validate()
