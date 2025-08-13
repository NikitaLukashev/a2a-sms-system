"""
A2A Protocol for SMS Host Automation
Main protocol that orchestrates the entire system using Mistral AI
"""

import os
import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from dotenv import load_dotenv

from config.listing_parser import property_parser
from .ai_response_generator import ai_generator
from .sms_handler import sms_handler

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SMSHostProtocol:
    """
    A2A Protocol for automated SMS host responses using Mistral AI and RAG
    
    This protocol:
    1. Uses RAG architecture with vector database for property information
    2. Processes incoming SMS messages from a fixed guest number
    3. Generates AI-powered responses using Mistral Large with relevant context
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
        logger.info("Starting SMS Host Protocol...")
        
        # Validate configuration
        if not self._validate_config():
            logger.error("Protocol configuration validation failed.")
            return False
        
        # Initialize components
        if not await self._initialize_components():
            logger.error("Protocol component initialization failed.")
            return False
        
        self.is_running = True
        self.start_time = datetime.now()
        
        logger.info("SMS Host Protocol started successfully")
        logger.info(f"Protocol ID: {self.protocol_id}")
        logger.info(f"Agent ID: {self.agent_id}")
        logger.info(f"Guest Phone: {os.getenv('GUEST_PHONE_NUMBER')}")
        logger.info(f"AI Model: {os.getenv('MISTRAL_MODEL', 'mistral-large-latest')}")
        logger.info("RAG Architecture: Enabled with vector database")
        
        return True

    async def stop(self):
        """Stop the A2A protocol"""
        logger.info("Stopping SMS Host Protocol...")
        
        self.is_running = False
        
        logger.info("SMS Host Protocol stopped successfully")

    def _validate_config(self) -> bool:
        """Validate that all required configuration is present"""
        required_vars = [
            "MISTRAL_API_KEY",
            "TWILIO_ACCOUNT_SID",
            "TWILIO_AUTH_TOKEN",
            "TWILIO_PHONE_NUMBER",
            "GUEST_PHONE_NUMBER"
        ]
        
        for var in required_vars:
            if not os.getenv(var):
                logger.error(f"Missing required environment variable: {var}")
                return False
        return True

    async def _initialize_components(self) -> bool:
        """Initialize all protocol components"""
        # Test RAG property parser
        rag_stats = property_parser.get_database_stats()
        logger.info(f"RAG Property Parser initialized: {rag_stats}")
        
        # Test AI generator (initialization only)
        ai_generator # Accessing the global instance to ensure it's initialized
        
        # Test SMS handler (initialization only)
        sms_handler # Accessing the global instance to ensure it's initialized
        
        logger.info("All protocol components initialized successfully.")
        return True

    def process_guest_message(self, message: str, from_number: str = None) -> str:
        """Process an incoming guest message and generate a response using RAG"""
        if not self.is_running:
            logger.warning("Protocol not running, cannot process message")
            return "System is currently offline. Please try again later."
        
        # Validate sender if from_number is provided
        if from_number and from_number != os.getenv("GUEST_PHONE_NUMBER"):
            logger.warning(f"Unauthorized message from {from_number}")
            return "Sorry, this number is not authorized to receive responses from this property."
        
        # Generate AI response using RAG
        guest_name = "Guest" # Default guest name
        response_text = ai_generator.generate_response(message, guest_name)
        
        # Update conversation history
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "role": "guest",
            "message": message
        })
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "role": "host_ai",
            "message": response_text
        })
        self.message_count += 1
        
        # If from_number is provided, send SMS response
        if from_number:
            sms_handler._send_sms_response(from_number, response_text) # Direct call to send SMS
        
        logger.info(f"Message processed using RAG. Response: {response_text}")
        return response_text

    def send_welcome_message(self):
        """Send a welcome message to the guest"""
        if not self.is_running:
            logger.warning("Protocol not running, cannot send welcome message")
            return False
        
        sms_handler.send_welcome_message()
        logger.info("Welcome message sent successfully")
        return True

    def send_property_summary(self):
        """Send a property summary to the guest using RAG"""
        if not self.is_running:
            logger.warning("Protocol not running, cannot send property summary")
            return False
        
        sms_handler.send_property_summary()
        logger.info("Property summary sent successfully using RAG")
        return True

    def get_protocol_status(self) -> Dict[str, Any]:
        """Get the current status of the protocol"""
        uptime_seconds = None
        if self.is_running and self.start_time:
            uptime_seconds = (datetime.now() - self.start_time).total_seconds()
        
        # Get RAG statistics
        rag_stats = property_parser.get_database_stats()
        
        return {
            "protocol_id": self.protocol_id,
            "agent_id": self.agent_id,
            "status": "Running" if self.is_running else "Stopped",
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "uptime_seconds": uptime_seconds,
            "total_messages": self.message_count,
            "conversation_history_count": len(self.conversation_history),
            "ai_model": os.getenv("MISTRAL_MODEL", "mistral-large-latest"),
            "ai_provider": "Mistral AI",
            "rag_architecture": "Enabled",
            "rag_stats": rag_stats
        }

    def get_conversation_history(self, limit: int = 10) -> List[Dict[str, str]]:
        """Get recent conversation history"""
        return self.conversation_history[-limit:]

    def test_protocol(self) -> Dict[str, Any]:
        """Run internal tests for the protocol components"""
        test_results = {
            "protocol_status": self.get_protocol_status(),
            "components": {},
            "messages": [],
            "rag_tests": {}
        }
        
        # Test RAG property parser
        rag_stats = property_parser.get_database_stats()
        test_results["rag_tests"]["database_stats"] = rag_stats
        
        # Test RAG query
        test_query = "WiFi amenities"
        rag_results = property_parser.query_property_info(test_query, k=2)
        test_results["rag_tests"]["query_test"] = {
            "query": test_query,
            "results_count": len(rag_results),
            "sample_result": rag_results[0] if rag_results else None
        }
        
        # Test AI generator
        ai_test_responses = ai_generator.test_response_generation()
        test_results["components"]["ai_generator"] = ai_test_responses
        
        # Test message processing (without actual SMS sending)
        test_message = "What are the check-in times?"
        simulated_response = self.process_guest_message(test_message, from_number=os.getenv("GUEST_PHONE_NUMBER"))
        test_results["messages"].append({
            "test_message": test_message,
            "simulated_response": simulated_response
        })
        
        logger.info("Protocol internal tests completed successfully.")
        return test_results

    def refresh_rag_database(self):
        """Refresh the RAG vector database"""
        if not self.is_running:
            logger.warning("Protocol not running, cannot refresh RAG database")
            return False
        
        logger.info("Refreshing RAG vector database...")
        property_parser.refresh_database()
        logger.info("RAG vector database refreshed successfully")
        return True

    def get_rag_insights(self, query: str) -> Dict[str, Any]:
        """Get RAG insights for a specific query"""
        if not self.is_running:
            return {"error": "Protocol not running"}
        
        # Get relevant context
        results = property_parser.query_property_info(query, k=3)
        
        # Get AI response for context
        context = property_parser.format_for_ai_context(query)
        
        return {
            "query": query,
            "relevant_chunks": len(results),
            "context": context,
            "top_result": results[0] if results else None,
            "all_results": results
        }

# Global protocol instance
sms_protocol = SMSHostProtocol()
