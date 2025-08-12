"""
A2A Protocol for SMS Host Automation
Main protocol that orchestrates the entire system using Mistral AI
"""

import os
import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

from config.listing_parser import property_parser
from ai_response_generator import ai_generator
from sms_handler import sms_handler

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SMSHostProtocol:
    """
    A2A Protocol for automated SMS host responses using Mistral AI
    
    This protocol:
    1. Reads property information from data/property_info.txt
    2. Processes incoming SMS messages from a fixed guest number
    3. Generates AI-powered responses using Mistral Large
    4. Sends responses back via SMS
    5. Maintains conversation context and history
    """
    
    def __init__(self):
        self.protocol_id = os.getenv("A2A_PROTOCOL_ID", "sms-host-protocol")
        self.agent_id = os.getenv("A2A_AGENT_ID", "sms-host-agent")
        self.is_running = False
        self.start_time = None
        self.message_count = 0
        self.conversation_history = []
        
        logger.info(f"SMS Host Protocol initialized: {self.protocol_id}")
    
    async def start(self) -> bool:
        """Start the A2A protocol"""
        try:
            logger.info("Starting SMS Host Protocol...")
            
            # Validate configuration
            if not self._validate_configuration():
                logger.error("Configuration validation failed")
                return False
            
            # Initialize components
            if not await self._initialize_components():
                logger.error("Component initialization failed")
                return False
            
            # Start the protocol
            self.is_running = True
            self.start_time = datetime.now()
            
            logger.info("SMS Host Protocol started successfully")
            logger.info(f"Protocol ID: {self.protocol_id}")
            logger.info(f"Agent ID: {self.agent_id}")
            logger.info(f"Guest Phone: {os.getenv('GUEST_PHONE_NUMBER')}")
            logger.info(f"Property: {property_parser.get_property_name()}")
            logger.info(f"AI Model: {os.getenv('MISTRAL_MODEL', 'mistral-large-latest')}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start protocol: {e}")
            return False
    
    async def stop(self):
        """Stop the A2A protocol"""
        try:
            logger.info("Stopping SMS Host Protocol...")
            
            self.is_running = False
            
            logger.info("SMS Host Protocol stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping protocol: {e}")
    
    def _validate_configuration(self) -> bool:
        """Validate that all required configuration is present"""
        required_vars = [
            "MISTRAL_API_KEY",
            "TWILIO_ACCOUNT_SID",
            "TWILIO_AUTH_TOKEN",
            "TWILIO_PHONE_NUMBER",
            "GUEST_PHONE_NUMBER"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {missing_vars}")
            return False
        
        return True
    
    async def _initialize_components(self) -> bool:
        """Initialize all protocol components"""
        try:
            # Test property parser
            property_name = property_parser.get_property_name()
            if not property_name:
                logger.error("Property parser failed to load property information")
                return False
            
            # Test AI generator
            test_response = ai_generator.generate_response("test", "Test")
            if not test_response:
                logger.error("AI generator failed to generate test response")
                return False
            
            # Test SMS handler
            sms_status = sms_handler.get_sms_status()
            if sms_status["status"] != "Active":
                logger.error("SMS handler is not active")
                return False
            
            logger.info("All components initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Component initialization failed: {e}")
            return False
    
    def process_guest_message(self, message: str, from_number: str = None) -> str:
        """
        Process a guest message and generate response
        
        Args:
            message: The guest's message
            from_number: Phone number (optional, uses configured guest number if not provided)
            
        Returns:
            Generated response message
        """
        try:
            if not self.is_running:
                logger.warning("Protocol not running, cannot process message")
                return "Sorry, the system is not available right now."
            
            # Use configured guest number if none provided
            if not from_number:
                from_number = os.getenv("GUEST_PHONE_NUMBER")
            
            # Validate sender
            if from_number != os.getenv("GUEST_PHONE_NUMBER"):
                logger.warning(f"Unauthorized message from {from_number}")
                return "Sorry, this number is not authorized to receive responses from this property."
            
            # Generate AI response
            ai_response = ai_generator.generate_response(message, "Guest")
            
            # Send SMS response
            sms_handler._send_sms_response(from_number, ai_response)
            
            # Update conversation history
            self._update_conversation_history(message, ai_response, from_number)
            
            # Increment message count
            self.message_count += 1
            
            logger.info(f"Message processed successfully. Total messages: {self.message_count}")
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Error processing guest message: {e}")
            error_response = "Sorry, I'm having trouble processing your message right now. Please try again later!"
            
            # Try to send error response
            try:
                if from_number:
                    sms_handler._send_sms_response(from_number, error_response)
            except:
                pass
            
            return error_response
    
    def _update_conversation_history(self, guest_message: str, host_response: str, phone_number: str):
        """Update conversation history"""
        conversation_entry = {
            "timestamp": datetime.now().isoformat(),
            "phone_number": phone_number,
            "guest_message": guest_message,
            "host_response": host_response,
            "message_number": self.message_count
        }
        
        self.conversation_history.append(conversation_entry)
        
        # Keep only last 100 conversations to prevent memory bloat
        if len(self.conversation_history) > 100:
            self.conversation_history = self.conversation_history[-100:]
    
    def send_welcome_message(self):
        """Send a welcome message to the guest"""
        try:
            if not self.is_running:
                logger.warning("Protocol not running, cannot send welcome message")
                return False
            
            sms_handler.send_welcome_message()
            logger.info("Welcome message sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error sending welcome message: {e}")
            return False
    
    def send_property_summary(self):
        """Send a property summary to the guest"""
        try:
            if not self.is_running:
                logger.warning("Protocol not running, cannot send property summary")
                return False
            
            sms_handler.send_property_summary()
            logger.info("Property summary sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error sending property summary: {e}")
            return False
    
    def test_protocol(self) -> Dict[str, Any]:
        """Test the protocol functionality"""
        test_results = {
            "timestamp": datetime.now().isoformat(),
            "protocol_status": "Running" if self.is_running else "Stopped",
            "components": {},
            "ai_test": {},
            "sms_test": {}
        }
        
        try:
            # Test property parser
            test_results["components"]["property_parser"] = {
                "property_name": property_parser.get_property_name(),
                "location": property_parser.get_location(),
                "checkin_info": property_parser.get_checkin_info(),
                "amenities": property_parser.get_amenities()
            }
            
            # Test AI generator
            test_questions = [
                "Do you have WiFi?",
                "What time is check-in?",
                "Is parking included?"
            ]
            
            ai_test_results = {}
            for question in test_questions:
                response = ai_generator.generate_response(question, "Test Guest")
                ai_test_results[question] = response
            
            test_results["ai_test"] = ai_test_results
            
            # Test SMS handler
            test_results["sms_test"] = sms_handler.get_sms_status()
            
            logger.info("Protocol test completed successfully")
            
        except Exception as e:
            logger.error(f"Protocol test failed: {e}")
            test_results["error"] = str(e)
        
        return test_results
    
    def get_protocol_status(self) -> Dict[str, Any]:
        """Get current protocol status"""
        uptime = None
        if self.start_time:
            uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            "protocol_id": self.protocol_id,
            "agent_id": self.agent_id,
            "status": "Running" if self.is_running else "Stopped",
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "uptime_seconds": uptime,
            "total_messages": self.message_count,
            "conversation_history_count": len(self.conversation_history),
            "property_name": property_parser.get_property_name(),
            "guest_phone": os.getenv("GUEST_PHONE_NUMBER"),
            "ai_model": os.getenv("MISTRAL_MODEL", "mistral-large-latest"),
            "ai_provider": "Mistral AI"
        }
    
    def get_conversation_history(self, limit: int = 10) -> list:
        """Get recent conversation history"""
        return self.conversation_history[-limit:] if self.conversation_history else []
    
    def export_conversation_data(self, format: str = "json") -> str:
        """Export conversation data"""
        try:
            if format.lower() == "json":
                import json
                data = {
                    "protocol_status": self.get_protocol_status(),
                    "conversation_history": self.conversation_history,
                    "export_timestamp": datetime.now().isoformat()
                }
                return json.dumps(data, indent=2, default=str)
            else:
                return f"Unsupported export format: {format}"
                
        except Exception as e:
            logger.error(f"Error exporting conversation data: {e}")
            return f"Error: {str(e)}"


# Global protocol instance
sms_protocol = SMSHostProtocol()
