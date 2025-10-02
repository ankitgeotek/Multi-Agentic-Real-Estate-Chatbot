
# ============================================
# utils/image_utils.py
# ============================================
import base64
import os
from PIL import Image
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

def encode_image(image_path: str) -> str:
    """
    Encode image to base64 string.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Base64 encoded string
        
    Raises:
        FileNotFoundError: If image doesn't exist
        ValueError: If image cannot be read
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    try:
        with open(image_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode('utf-8')
            logger.info(f"Successfully encoded image: {image_path}")
            return encoded
    except Exception as e:
        logger.error(f"Error encoding image {image_path}: {str(e)}")
        raise ValueError(f"Failed to encode image: {str(e)}")

def validate_image(image_path: str) -> Tuple[bool, Optional[str]]:
    """
    Validate if image is a valid property/real estate image.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            return False, f"Image file not found: {image_path}"
        
        # Try to open with PIL
        with Image.open(image_path) as img:
            # Check format
            if img.format not in ['JPEG', 'PNG', 'WEBP']:
                return False, f"Unsupported image format: {img.format}"
            
            # Check dimensions (minimum 100x100, maximum 4096x4096)
            width, height = img.size
            if width < 100 or height < 100:
                return False, f"Image too small: {width}x{height} (minimum 100x100)"
            if width > 4096 or height > 4096:
                return False, f"Image too large: {width}x{height} (maximum 4096x4096)"
            
            # Check file size
            file_size_mb = os.path.getsize(image_path) / (1024 * 1024)
            if file_size_mb > 10:
                return False, f"Image file too large: {file_size_mb:.2f}MB (maximum 10MB)"
        
        logger.info(f"Image validation passed: {image_path}")
        return True, None
        
    except Exception as e:
        logger.error(f"Error validating image {image_path}: {str(e)}")
        return False, f"Error validating image: {str(e)}"
