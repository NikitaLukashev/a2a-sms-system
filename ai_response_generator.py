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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIResponseGenerator:
    """Generates AI-powered responses to guest SMS messages using Mistral Large"""
    
    def __init__(self):
        self.client = MistralClient(api_key=os.getenv("MISTRAL_API_KEY"))
        self.model = os.getenv("MISTRAL_MODEL", "mistral-large-latest")
        self.property_context = property_parser.format_for_ai_context()
        
        logger.info(f"AI Response Generator initialized with model: {self.model}")
    
    def generate_response(self, guest_message: str, guest_name: str = "Guest") -> str:
        """
        Generate a casual and friendly response to a guest message
        
        Args:
            guest_message: The guest's SMS message
            guest_name: Name of the guest (if known)
            
        Returns:
            Generated response message
        """
        try:
            # Build the prompt for Mistral
            prompt = self._build_prompt(guest_message, guest_name)
            
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
            
            ai_response = response.choices[0].message.content.strip()
            
            # Clean up the response
            cleaned_response = self._clean_response(ai_response)
            
            logger.info(f"Generated response for '{guest_message}': {cleaned_response[:50]}...")
            
            return cleaned_response
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return self._generate_fallback_response(guest_message, guest_name)
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for Mistral"""
        return f"""You are a friendly and helpful property host assistant. You're responding to guest SMS messages about a property.

Your communication style should be:
- Casual and friendly (not formal)
- Warm and welcoming
- Helpful and informative
- Concise (SMS length)
- Use emojis occasionally to keep it friendly
- Be enthusiastic about the property

Property Information:
{self.property_context}

Always base your responses on the actual property information provided above. If you don't know something specific, say so and offer to help find out.

Keep responses under 160 characters when possible for SMS."""
    
    def _build_prompt(self, guest_message: str, guest_name: str) -> str:
        """Build the user prompt for Mistral"""
        return f"""Guest message: "{guest_message}"

Please respond to this guest message in a casual, friendly tone. Use the property information to provide accurate answers.

If the guest is asking about:
- WiFi: Confirm it's included and mention it's high-speed
- Check-in time: Provide the exact time and mention self check-in
- Amenities: List what's available
- House rules: Explain them kindly
- Nearby attractions: Give recommendations
- General questions: Be helpful and welcoming

Guest name: {guest_name}"""
    
    def _clean_response(self, response: str) -> str:
        """Clean and format the AI response"""
        # Remove quotes if the response is wrapped in them
        if response.startswith('"') and response.endswith('"'):
            response = response[1:-1]
        
        # Remove any markdown formatting
        response = response.replace('**', '').replace('*', '')
        
        # Ensure it's not too long for SMS
        if len(response) > 160:
            response = response[:157] + "..."
        
        return response.strip()
    
    def _generate_fallback_response(self, guest_message: str, guest_name: str) -> str:
        """Generate fallback response if AI generation fails"""
        message_lower = guest_message.lower()
        
        # Simple keyword-based responses as fallback
        if "wifi" in message_lower or "internet" in message_lower:
            return f"Hey {guest_name}! 😊 Yes, we have free high-speed WiFi included. You'll get the password when you check in!"
        
        elif "check" in message_lower and ("in" in message_lower or "time" in message_lower):
            return f"Hi {guest_name}! Check-in is at 3:00 PM and check-out is 11:00 AM. You'll get the keypad code 24 hours before arrival! 🏠"
        
        elif "parking" in message_lower:
            return f"Hey {guest_name}! Yes, we have free parking available right at the property. 🚗"
        
        elif "pet" in message_lower or "dog" in message_lower or "cat" in message_lower:
            return f"Hi {guest_name}! Unfortunately we don't allow pets at the property. Hope you understand! 🐾"
        
        elif "smoking" in message_lower:
            return f"Hey {guest_name}! The property is completely non-smoking. Thanks for asking! 🚭"
        
        elif "amenity" in message_lower or "what's included" in message_lower:
            return f"Hi {guest_name}! We include towels, linens, coffee, tea, and local guidebooks. The kitchen is fully equipped too! 🏠✨"
        
        elif "nearby" in message_lower or "restaurant" in message_lower:
            return f"Hey {guest_name}! We're close to restaurants, shopping centers, and attractions. I'll send you my local favorites! 🗺️"
        
        elif "cancel" in message_lower or "refund" in message_lower:
            return f"Hi {guest_name}! We have a flexible cancellation policy. Full refund if cancelled 7+ days before arrival, 50% within 7 days. Let me know if you need help! 📋"
        
        else:
            return f"Hey {guest_name}! Thanks for your message! I'd be happy to help with any questions about your stay. What would you like to know? 😊"
    
    def get_property_summary(self) -> str:
        """Get a summary of the property for quick reference"""
        return f"""🏠 {property_parser.get_property_name()}
📍 {property_parser.get_location()}
⏰ Check-in: 3:00 PM, Check-out: 11:00 AM
📶 WiFi included
🚗 Free parking
🐾 No pets
🚭 No smoking
👥 Guest limit applies"""
    
    def test_response_generation(self) -> Dict[str, str]:
        """Test response generation with common guest questions"""
        test_questions = [
            "Do you have WiFi?",
            "What time is check-in?",
            "Is parking included?"
        ]
        
        results = {}
        for question in test_questions:
            try:
                response = self.generate_response(question, "Test Guest")
                results[question] = response
            except Exception as e:
                results[question] = f"Error: {str(e)}"
        
        return results


# Global instance
ai_generator = AIResponseGenerator()
