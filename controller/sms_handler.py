"""
SMS Handler for SMS Host Protocol
Handles incoming SMS messages and sends AI-generated responses
"""

import os
import logging
from typing import Dict, Any, Optional
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from .ai_response_generator import ai_generator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SMSHandler:
    """Handles SMS messaging for property guest communication"""
    
    def __init__(self):
        # Initialize Twilio client
        self.client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN")
        )
        
        # Configuration
        self.twilio_phone = os.getenv("TWILIO_PHONE_NUMBER")
        self.guest_phone = os.getenv("GUEST_PHONE_NUMBER")
        
        # Validate configuration
        if not all([self.twilio_phone, self.guest_phone]):
            raise ValueError("Missing Twilio configuration in environment variables")
        
        logger.info(f"SMS Handler initialized - Twilio: {self.twilio_phone}, Guest: {self.guest_phone}")
    
    def process_incoming_sms(self, from_number: str, message_body: str) -> str:
        """
        Process incoming SMS and generate response
        
        Args:
            from_number: Phone number the SMS came from
            message_body: Content of the SMS
            
        Returns:
            TwiML response string
        """
        # Check if message is from the authorized guest number
        if from_number != self.guest_phone:
            logger.warning(f"Unauthorized SMS from {from_number}")
            return self._generate_unauthorized_response()
        
        logger.info(f"Processing SMS from {from_number}: {message_body}")
        
        # Generate AI response
        ai_response = ai_generator.generate_response(message_body, "Guest")
        
        # Send SMS response
        self._send_sms_response(from_number, ai_response)
        
        # Return TwiML response for webhook
        return self._generate_twiml_response(ai_response)
    
    def _send_sms_response(self, to_number: str, message: str):
        """Send SMS response to guest"""
        message_obj = self.client.messages.create(
            body=message,
            from_=self.twilio_phone,
            to=to_number
        )
        
        logger.info(f"SMS response sent successfully: {message_obj.sid}")
    
    def _generate_twiml_response(self, message: str) -> str:
        """Generate TwiML response for webhook"""
        response = MessagingResponse()
        response.message(message)
        return str(response)
    
    def _generate_unauthorized_response(self) -> str:
        """Generate response for unauthorized numbers"""
        response = MessagingResponse()
        response.message("Sorry, this number is not authorized to receive responses from this property.")
        return str(response)
    
    def send_welcome_message(self, guest_name: str = "Guest"):
        """Send a welcome message to the guest"""
        welcome_message = f"Hey {guest_name}! 👋 Welcome to our property! I'm your AI host assistant. Feel free to ask me anything about your stay - WiFi, check-in times, amenities, nearby attractions, or house rules. I'm here to help make your stay perfect! 🏠✨"
        
        self._send_sms_response(self.guest_phone, welcome_message)
        logger.info("Welcome message sent successfully")
    
    def send_property_summary(self):
        """Send a summary of the property to the guest"""
        summary = ai_generator.get_property_summary()
        self._send_sms_response(self.guest_phone, summary)
        logger.info("Property summary sent successfully")
    
    def test_sms_functionality(self):
        """Test SMS functionality with a test message"""
        test_message = "This is a test message from your AI host assistant! 🏠✨"
        self._send_sms_response(self.guest_phone, test_message)
        logger.info("Test SMS sent successfully")
        return True
    
    def get_sms_status(self) -> Dict[str, Any]:
        """Get SMS handler status and configuration"""
        return {
            "twilio_phone": self.twilio_phone,
            "guest_phone": self.guest_phone,
            "twilio_account_sid": os.getenv("TWILIO_ACCOUNT_SID", "Not set"),
            "twilio_auth_token": "***" if os.getenv("TWILIO_AUTH_TOKEN") else "Not set",
            "status": "Active" if self.twilio_phone and self.guest_phone else "Inactive"
        }


# Global instance
sms_handler = SMSHandler()
