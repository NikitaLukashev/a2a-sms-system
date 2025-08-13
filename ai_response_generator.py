"""
AI Response Generator for SMS Host Protocol
Uses Mistral Large LLM to generate casual and friendly responses
"""

import os
import logging
from typing import Dict, Any, Optional
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from config.listing_parser import property_parser

# Configure logging
logger = logging.getLogger(__name__)

class AIResponseGenerator:
    """Generates AI-powered responses to guest SMS messages using Mistral Large with RAG"""
    
    def __init__(self):
        self.client = MistralClient(api_key=os.getenv("MISTRAL_API_KEY"))
        self.model = os.getenv("MISTRAL_MODEL", "mistral-large-latest")
        
        logger.info(f"AI Response Generator initialized with model: {self.model}")

    def generate_response(self, guest_message: str, guest_name: str = "Guest") -> str:
        """Generate an AI response based on guest message and RAG-retrieved property context"""
        logger.info(f"Generating AI response for message: '{guest_message}' from {guest_name}")
        
        # Get relevant property context using RAG
        property_context = self._get_relevant_context(guest_message)
        
        # Build the prompt for Mistral
        prompt = self._build_prompt(guest_message, guest_name, property_context)
        
        # Generate response using Mistral
        messages = [
            ChatMessage(role="system", content=self._get_system_prompt()),
            ChatMessage(role="user", content=prompt)
        ]
        
        response = self.client.chat(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=200
        )
        
        ai_text = response.choices[0].message.content
        cleaned_response = self._clean_response(ai_text)
        logger.info(f"AI generated response: '{cleaned_response}'")
        return cleaned_response

    def _get_relevant_context(self, guest_message: str) -> str:
        """Get relevant property context using RAG"""
        # Use RAG to get context specific to the guest's question
        results = property_parser.query_property_info(guest_message, k=3)
        
        if not results:
            logger.warning("No relevant context found for query, using general context")
            return property_parser.format_for_ai_context()
        
        # Format the most relevant results
        context_parts = ["Relevant Property Information:"]
        for i, result in enumerate(results[:2], 1):  # Use top 2 results
            context_parts.append(f"{i}. {result['content'].strip()}")
        
        return "\n\n".join(context_parts)

    def _get_system_prompt(self) -> str:
        """Get the system prompt for Mistral"""
        return """You are a friendly and helpful property host assistant. You're responding to guest SMS messages about a property.

Your communication style should be:
- Casual and friendly (not formal)
- Warm and welcoming
- Helpful and informative
- Concise (SMS length)
- Use emojis occasionally to keep it friendly
- Be enthusiastic about the property

Always base your responses on the actual property information provided in the context. If you don't know something specific, say so and offer to help find out.

Keep responses under 160 characters when possible for SMS."""

    def _build_prompt(self, guest_message: str, guest_name: str, property_context: str) -> str:
        """Build the user prompt for Mistral"""
        return f"""Guest message: "{guest_message}"

Property Context:
{property_context}

Based on the property information above, provide a casual and friendly response to {guest_name}.
"""

    def _clean_response(self, response: str) -> str:
        """Clean the AI response for SMS"""
        # Remove leading/trailing quotes or markdown code blocks
        response = response.strip()
        if response.startswith(('"', "'", "```")) and response.endswith(('"', "'", "```")):
            response = response[1:-1].strip()
            if response.startswith("python"): # Remove language tag from markdown
                response = response[6:].strip()
        
        # Truncate for SMS length if necessary (common SMS limit is 160 characters)
        if len(response) > 320: # Allow a bit more for multi-part SMS, but keep it concise
            response = response[:317] + "..."
        
        return response

    def _generate_fallback_response(self, guest_message: str, guest_name: str) -> str:
        """Generate fallback response if AI generation fails"""
        message_lower = guest_message.lower()
        
        if "checkin" in message_lower or "check-in" in message_lower:
            return f"Hey {guest_name}! Check-in is usually at 3:00 PM. I'll send you the exact details closer to your arrival! ⏰"
        
        elif "checkout" in message_lower or "check-out" in message_lower:
            return f"Hey {guest_name}! Check-out is usually at 11:00 AM. Let me know if you need anything else! 👋"
        
        elif "wifi" in message_lower:
            return f"Hey {guest_name}! Yes, we have free high-speed WiFi available! The network name and password will be provided upon check-in. 📶"
        
        elif "parking" in message_lower:
            return f"Hey {guest_name}! Yes, we have free parking available right at the property. 🚗"
        
        elif "pet" in message_lower or "dog" in message_lower or "cat" in message_lower:
            return f"Hey {guest_name}! Unfortunately, we have a strict no-pets policy at the property. Thanks for understanding! 🚫🐾"
        
        elif "rule" in message_lower:
            return f"Hey {guest_name}! Our main house rules are no smoking, no pets, and quiet hours from 10 PM to 8 AM. Full details are in the property guide! 🏡"
        
        elif "nearby" in message_lower or "restaurant" in message_lower:
            return f"Hey {guest_name}! We're close to restaurants, shopping centers, and attractions. I'll send you my local favorites! 🗺️"
        
        elif "cancel" in message_lower or "refund" in message_lower:
            return f"Hey {guest_name}! Our cancellation policy is flexible: full refund if cancelled 7+ days before arrival, 50% within 7 days. Please check your booking details for specifics. 🗓️"
        
        else:
            return f"Hey {guest_name}! Thanks for your message! I'd be happy to help with any questions about your stay. What would you like to know? 😊"

    def get_property_summary(self) -> str:
        """Get a summary of the property for quick reference"""
        return property_parser.get_property_summary()

    def test_response_generation(self) -> Dict[str, str]:
        """Test AI response generation with sample questions"""
        test_questions = [
            "Do you have WiFi?",
            "What time is check-in?",
            "Is parking included?"
        ]
        
        results = {}
        for q in test_questions:
            response = self.generate_response(q, "TestGuest")
            results[q] = response
        return results

    def get_rag_stats(self) -> Dict[str, Any]:
        """Get RAG system statistics"""
        return property_parser.get_database_stats()

# Global instance
ai_generator = AIResponseGenerator()
