"""
AI Image Generator for Meta Ads
Uses DALL-E 3 for generating ad creative images
"""
import os
import logging
import base64
from typing import Optional, Dict, Any
from io import BytesIO
import requests
from openai import OpenAI

logger = logging.getLogger(__name__)


class AIImageGenerator:
    """Generate ad creative images using DALL-E 3"""

    def __init__(self):
        """Initialize OpenAI API"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")

        self.client = OpenAI(api_key=api_key)
        logger.info("AI Image Generator initialized with DALL-E 3")

    def generate_meta_ad_image(
        self,
        product_name: str,
        product_description: str,
        image_style: str = "professional",
        brand_colors: Optional[list] = None,
        size: str = "1024x1024"  # Meta Feed ads: 1200x1200 or 1:1 ratio
    ) -> Dict[str, Any]:
        """
        Generate an image for Meta ad creative

        Args:
            product_name: Name of the product/service
            product_description: Description to visualize
            image_style: Style preference (minimalist, bold, colorful, professional)
            brand_colors: List of hex colors to incorporate
            size: Image dimensions (1024x1024 for Meta Feed)

        Returns:
            Dict with image_url, image_bytes, and prompt_used
        """

        # Build style guidance
        style_guidance = {
            "minimalist": "clean, simple, lots of white space, minimal elements",
            "bold": "vibrant, eye-catching, strong contrasts, dynamic composition",
            "colorful": "bright, cheerful, multiple colors, energetic mood",
            "professional": "polished, business-like, trustworthy, modern aesthetic",
            "luxurious": "elegant, premium, sophisticated, gold accents"
        }

        style_desc = style_guidance.get(image_style, "professional, modern")

        # Incorporate brand colors if provided
        color_guidance = ""
        if brand_colors and len(brand_colors) > 0:
            color_guidance = f" Using brand colors: {', '.join(brand_colors)}."

        # Construct DALL-E 3 prompt
        prompt = f"""Professional advertising image for {product_name}.
{product_description}

Style: {style_desc}{color_guidance}

Requirements:
- High-quality product photography style
- Suitable for Facebook/Instagram feed ads
- No text or words in the image (will be added separately)
- Central composition
- Engaging and scroll-stopping
- Clean background
- Focus on the product/concept
"""

        try:
            # Call DALL-E 3 API
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality="standard",  # or "hd" for higher quality
                n=1,
            )

            image_url = response.data[0].url
            revised_prompt = response.data[0].revised_prompt

            # Download image bytes
            image_response = requests.get(image_url)
            image_bytes = image_response.content

            logger.info(f"Generated image successfully for {product_name}")

            return {
                "image_url": image_url,
                "image_bytes": image_bytes,
                "prompt_used": prompt,
                "revised_prompt": revised_prompt,
                "size": size
            }

        except Exception as e:
            logger.error(f"Error generating image: {e}")
            raise

    def generate_meta_story_image(
        self,
        product_name: str,
        product_description: str,
        image_style: str = "professional",
        brand_colors: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Generate a vertical image for Meta Stories (9:16 ratio)

        Args:
            product_name: Name of the product/service
            product_description: Description to visualize
            image_style: Style preference
            brand_colors: List of hex colors

        Returns:
            Dict with image_url, image_bytes, and prompt_used
        """

        # Note: DALL-E 3 doesn't support 9:16 directly
        # We generate 1024x1792 (closest to 9:16)
        # OR generate 1024x1024 and the frontend can crop/scale

        style_guidance = {
            "minimalist": "clean, simple, vertical layout",
            "bold": "vibrant, eye-catching, vertical composition",
            "colorful": "bright, cheerful, vertical arrangement",
            "professional": "polished, vertical product showcase",
            "luxurious": "elegant, premium, vertical display"
        }

        style_desc = style_guidance.get(image_style, "professional, vertical")

        color_guidance = ""
        if brand_colors and len(brand_colors) > 0:
            color_guidance = f" Brand colors: {', '.join(brand_colors)}."

        prompt = f"""Vertical Instagram Story advertising image for {product_name}.
{product_description}

Style: {style_desc}{color_guidance}

Requirements:
- Vertical composition (optimized for mobile Stories)
- High-quality product photography
- No text or words in the image
- Mobile-first design
- Eye-catching and immersive
- Clean, uncluttered
"""

        try:
            # DALL-E 3 supports 1024x1792 for vertical
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1792",
                quality="standard",
                n=1,
            )

            image_url = response.data[0].url
            revised_prompt = response.data[0].revised_prompt

            image_response = requests.get(image_url)
            image_bytes = image_response.content

            logger.info(f"Generated Story image successfully for {product_name}")

            return {
                "image_url": image_url,
                "image_bytes": image_bytes,
                "prompt_used": prompt,
                "revised_prompt": revised_prompt,
                "size": "1024x1792"
            }

        except Exception as e:
            logger.error(f"Error generating Story image: {e}")
            raise

    def edit_image_with_prompt(
        self,
        original_image_url: str,
        edit_instruction: str
    ) -> Dict[str, Any]:
        """
        Edit an existing image based on text instructions (future feature)
        This would use DALL-E image editing capabilities

        Args:
            original_image_url: URL of the original image
            edit_instruction: What to change (e.g., "Make background white", "Add sunshine")

        Returns:
            Dict with edited image data
        """

        # Note: DALL-E 2 supports image editing, but DALL-E 3 does not yet
        # This is a placeholder for future implementation
        logger.warning("Image editing not yet implemented in DALL-E 3")
        raise NotImplementedError("Image editing will be available in a future version")
