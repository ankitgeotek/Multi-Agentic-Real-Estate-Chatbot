
# ============================================
# models/inputs.py
# ============================================
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import os

class UserQuery(BaseModel):
    """Input model with comprehensive validation"""
    
    text_query: Optional[str] = Field(
        None,
        description="User's text question or description",
        examples=["What's wrong with this wall?", "Can my landlord evict me?"]
    )
    image_path: Optional[str] = Field(
        None,
        description="Path to the property image"
    )
    user_location: Optional[str] = Field(
        None,
        description="User's location for location-specific tenancy laws",
        examples=["New York, USA", "California", "London, UK"]
    )
    
    @field_validator('text_query')
    @classmethod
    def validate_text_query(cls, v: Optional[str]) -> Optional[str]:
        """Validate text query"""
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                return None
            if len(v) > 1000:
                raise ValueError("Text query must be less than 1000 characters")
        return v
    
    @field_validator('image_path')
    @classmethod
    def validate_image_path(cls, v: Optional[str]) -> Optional[str]:
        """Validate image path exists and is valid format"""
        if v is not None:
            if not os.path.exists(v):
                raise ValueError(f"Image file not found: {v}")
            
            ext = os.path.splitext(v)[1].lower()
            allowed_formats = ['.jpg', '.jpeg', '.png', '.webp']
            if ext not in allowed_formats:
                raise ValueError(f"Image format must be one of {allowed_formats}")
            
            # Check file size (max 10MB)
            file_size_mb = os.path.getsize(v) / (1024 * 1024)
            if file_size_mb > 10:
                raise ValueError(f"Image size must be less than 10MB (current: {file_size_mb:.2f}MB)")
        
        return v
    
    @field_validator('user_location')
    @classmethod
    def validate_location(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean location"""
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                return None
        return v
    
    def model_post_init(self, __context):
        """Ensure at least one input is provided"""
        if not self.text_query and not self.image_path:
            raise ValueError("Must provide either text_query or image_path")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text_query": "What's causing the water stains on my ceiling?",
                "image_path": "/path/to/ceiling.jpg",
                "user_location": "California, USA"
            }
        }
