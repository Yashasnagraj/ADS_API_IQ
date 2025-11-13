"""
AI Text Generator for Meta Ads
Uses Google Gemini 2.0 Flash for generating ad copy
"""
import os
import json
import logging
from typing import List, Dict, Any, Optional
import google.generativeai as genai

logger = logging.getLogger(__name__)


class AITextGenerator:
    """Generate ad copy using Google Gemini API"""

    def __init__(self):
        """Initialize Gemini API"""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        logger.info("AI Text Generator initialized with Gemini 2.0 Flash")

    def generate_meta_ad_copy(
        self,
        product_name: str,
        product_description: str,
        target_audience: str,
        brand_voice: str,
        unique_selling_points: List[str],
        preferred_ctas: List[str],
        prohibited_words: Optional[List[str]] = None,
        num_variations: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Generate Meta ad copy variations

        Args:
            product_name: Name of product/service being advertised
            product_description: Detailed description of the product
            target_audience: Description of target audience
            brand_voice: Tone/voice (professional, casual, friendly, urgent, luxurious)
            unique_selling_points: List of USPs to highlight
            preferred_ctas: List of preferred call-to-actions
            prohibited_words: Words to avoid in ad copy
            num_variations: Number of ad variations to generate

        Returns:
            List of ad variations with primary_text, headline, description, cta
        """

        prohibited_str = ""
        if prohibited_words and len(prohibited_words) > 0:
            prohibited_str = f"\nAVOID using these words: {', '.join(prohibited_words)}"

        prompt = f"""You are an expert Meta Ads copywriter. Generate {num_variations} high-converting ad variations for Facebook/Instagram Feed ads.

PRODUCT/SERVICE:
Name: {product_name}
Description: {product_description}

TARGET AUDIENCE:
{target_audience}

BRAND VOICE:
{brand_voice}

UNIQUE SELLING POINTS:
{chr(10).join(f'" {usp}' for usp in unique_selling_points)}

PREFERRED CALL-TO-ACTIONS:
{', '.join(preferred_ctas)}{prohibited_str}

META ADS FORMAT REQUIREMENTS:
- Primary Text: Max 125 characters, engaging hook that stops scrolling
- Headline: Max 27 characters, clear value proposition
- Description: Max 27 characters, supporting detail or urgency
- CTA: Choose from the preferred CTAs list

GUIDELINES:
1. Primary text should create curiosity or solve a pain point
2. Use numbers, questions, or bold statements when appropriate
3. Headline must be punchy and benefit-driven
4. Description adds urgency or trust signals
5. Each variation should feel unique, not just word swaps
6. Match the {brand_voice} tone perfectly
7. Emphasize different USPs across variations

Return ONLY valid JSON array (no markdown, no extra text):
[
  {{
    "primary_text": "engaging hook under 125 chars",
    "headline": "under 27 chars",
    "description": "under 27 chars",
    "cta": "chosen from preferred list",
    "focus_usp": "which USP this ad emphasizes",
    "confidence_score": 0-10 score
  }}
]"""

        try:
            # Generate content
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.9,  # Creative but controlled
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=2048,
                )
            )

            # Extract JSON from response
            response_text = response.text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            elif response_text.startswith("```"):
                response_text = response_text.replace("```", "").strip()

            # Parse JSON
            ad_variations = json.loads(response_text)

            # Validate and enforce character limits
            validated_variations = []
            for ad in ad_variations:
                validated_ad = {
                    "primary_text": ad["primary_text"][:125],
                    "headline": ad["headline"][:27],
                    "description": ad["description"][:27],
                    "cta": ad.get("cta", preferred_ctas[0] if preferred_ctas else "Learn More"),
                    "focus_usp": ad.get("focus_usp", unique_selling_points[0] if unique_selling_points else "Quality"),
                    "confidence_score": min(10, max(0, ad.get("confidence_score", 7)))
                }
                validated_variations.append(validated_ad)

            logger.info(f"Generated {len(validated_variations)} ad variations successfully")
            return validated_variations

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Gemini response: {e}")
            logger.error(f"Response was: {response_text}")
            # Return fallback ad
            return self._generate_fallback_ads(
                product_name,
                product_description,
                preferred_ctas[0] if preferred_ctas else "Learn More",
                num_variations
            )

        except Exception as e:
            logger.error(f"Error generating ad copy: {e}")
            raise

    def optimize_ad_copy(
        self,
        existing_primary_text: str,
        existing_headline: str,
        existing_description: str,
        performance_feedback: str,
        brand_voice: str
    ) -> Dict[str, str]:
        """
        Optimize existing ad copy based on performance feedback

        Args:
            existing_primary_text: Current primary text
            existing_headline: Current headline
            existing_description: Current description
            performance_feedback: What's not working (e.g., "Low CTR", "High CPC, low conversions")
            brand_voice: Brand voice to maintain

        Returns:
            Optimized ad copy
        """

        prompt = f"""You are an expert Meta Ads optimizer. Improve this ad based on performance feedback.

CURRENT AD:
Primary Text: {existing_primary_text}
Headline: {existing_headline}
Description: {existing_description}

PERFORMANCE ISSUE:
{performance_feedback}

BRAND VOICE:
{brand_voice}

OPTIMIZATION GUIDELINES:
- If low CTR: Make primary text more attention-grabbing, use questions or numbers
- If low conversions: Strengthen CTA, add urgency or social proof
- If high CPC: Improve relevance, be more specific about target audience
- Maintain the {brand_voice} tone
- Stay within Meta character limits (125, 27, 27)

Return ONLY valid JSON (no markdown):
{{
  "primary_text": "optimized version under 125 chars",
  "headline": "optimized version under 27 chars",
  "description": "optimized version under 27 chars",
  "changes_made": "brief explanation of key improvements",
  "confidence_score": 0-10 score
}}"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.7,
                    top_p=0.9,
                    max_output_tokens=1024,
                )
            )

            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()

            optimized_ad = json.loads(response_text)

            # Enforce limits
            optimized_ad["primary_text"] = optimized_ad["primary_text"][:125]
            optimized_ad["headline"] = optimized_ad["headline"][:27]
            optimized_ad["description"] = optimized_ad["description"][:27]

            logger.info("Ad copy optimized successfully")
            return optimized_ad

        except Exception as e:
            logger.error(f"Error optimizing ad copy: {e}")
            # Return original if optimization fails
            return {
                "primary_text": existing_primary_text,
                "headline": existing_headline,
                "description": existing_description,
                "changes_made": "Optimization failed, returned original",
                "confidence_score": 5
            }

    def _generate_fallback_ads(
        self,
        product_name: str,
        product_description: str,
        cta: str,
        num_variations: int
    ) -> List[Dict[str, Any]]:
        """Generate basic fallback ads if AI generation fails"""

        fallback_templates = [
            {
                "primary_text": f"Discover {product_name} - {product_description[:80]}",
                "headline": f"Shop {product_name} Now",
                "description": "Limited Time Offer",
                "cta": cta,
                "focus_usp": "Quality",
                "confidence_score": 6
            },
            {
                "primary_text": f"Looking for the best {product_name}? We've got you covered.",
                "headline": f"Premium {product_name}",
                "description": "Free Shipping",
                "cta": cta,
                "focus_usp": "Convenience",
                "confidence_score": 6
            },
            {
                "primary_text": f"Transform your life with {product_name}. {product_description[:60]}",
                "headline": "Get Started Today",
                "description": "100% Satisfaction",
                "cta": cta,
                "focus_usp": "Trust",
                "confidence_score": 5
            }
        ]

        # Return as many as requested, cycling through templates
        return [fallback_templates[i % len(fallback_templates)] for i in range(num_variations)]
