#!/usr/bin/env python3
"""
Main Application for SMS Host Protocol
Entry point for the automated SMS host system using Mistral AI
"""

import asyncio
import os
import sys
import logging
import signal
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import HTMLResponse
import uvicorn

from a2a_protocol import sms_protocol
from ai_response_generator import ai_generator
from sms_handler import sms_handler

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('sms_host.log')
    ]
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="SMS Host Protocol",
    description="A2A Protocol for automated SMS host responses using Mistral AI",
    version="1.0.0"
)


class SMSHostApp:
    """Main application class for SMS Host Protocol"""
    
    def __init__(self):
        self.protocol = sms_protocol
        self.running = False
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("SMS Host Application initialized")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    async def initialize(self) -> bool:
        """Initialize the application"""
        logger.info("Initializing SMS Host Application...")
        
        # Check environment configuration
        if not self._validate_environment():
            return False
        
        # Start the protocol
        if not await self.protocol.start():
            logger.error("Failed to start protocol")
            return False
        
        logger.info("Application initialized successfully")
        return True
    
    def _validate_environment(self) -> bool:
        """Validate environment configuration"""
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
            logger.error("Missing required environment variables:")
            for var in missing_vars:
                logger.error(f"  - {var}")
            logger.error("\nPlease check your .env file and ensure all required variables are set.")
            return False
        
        return True
    
    async def run(self):
        """Run the main application loop"""
        self.running = True
        
        # Keep the application running
        while self.running:
            await asyncio.sleep(1)
        
        await self.cleanup()
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up application...")
        
        # Stop protocol
        if self.protocol:
            await self.protocol.stop()
        
        logger.info("Cleanup completed")


# Global app instance
app_instance = SMSHostApp()


# FastAPI startup event
@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup"""
    logger.info("Starting SMS Host Application...")
    if not await app_instance.initialize():
        logger.error("Failed to initialize application")
        raise Exception("Application initialization failed")
    logger.info("SMS Host Application started successfully")


# FastAPI shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down SMS Host Application...")
    await app_instance.cleanup()
    logger.info("Shutdown completed")


# FastAPI Routes

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with dashboard"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SMS Host Protocol Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; text-align: center; }
            .status { padding: 15px; margin: 20px 0; border-radius: 5px; }
            .status.running { background-color: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
            .status.stopped { background-color: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
            .button { background-color: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
            .button:hover { background-color: #0056b3; }
            .button.danger { background-color: #dc3545; }
            .button.danger:hover { background-color: #c82333; }
            .info-box { background-color: #e7f3ff; border: 1px solid #b3d9ff; padding: 15px; margin: 15px 0; border-radius: 5px; }
            .test-form { margin: 20px 0; padding: 20px; background-color: #f8f9fa; border-radius: 5px; }
            input[type="text"] { width: 100%; padding: 10px; margin: 5px 0; border: 1px solid #ddd; border-radius: 3px; }
            .ai-info { background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; margin: 15px 0; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏠 SMS Host Protocol Dashboard</h1>
            
                                    <div class="ai-info">
                            <h3>🤖 AI Assistant: Mistral Large + RAG Architecture</h3>
                            <p>This system uses Mistral AI's Large language model with RAG (Retrieval-Augmented Generation) for intelligent, context-aware responses to guest inquiries about your property.</p>
                        </div>
                        
                        <div class="rag-info" style="background-color: #e8f5e8; border: 1px solid #4caf50; padding: 15px; margin: 15px 0; border-radius: 5px;">
                            <h3>🧠 RAG System Status</h3>
                            <div id="rag-stats">Loading RAG stats...</div>
                        </div>
            
            <div class="info-box">
                <h3>System Status</h3>
                <div id="status">Loading...</div>
            </div>
            
                                    <div class="info-box">
                            <h3>Quick Actions</h3>
                            <button class="button" onclick="sendWelcome()">Send Welcome Message</button>
                            <button class="button" onclick="sendSummary()">Send Property Summary</button>
                            <button class="button" onclick="testProtocol()">Test Protocol</button>
                            <button class="button" onclick="testSMS()">Test SMS</button>
                            <button class="button" onclick="checkTwilioStatus()">Check Twilio Status</button>
                            <button class="button" onclick="refreshStatus()">Refresh Status</button>
                            <button class="button" onclick="refreshRAG()" style="background-color: #4caf50;">Refresh RAG Database</button>
                        </div>
            
            <div class="test-form">
                <h3>Test Message Processing</h3>
                <input type="text" id="testMessage" placeholder="Enter a test message (e.g., 'Do you have WiFi?')" />
                <button class="button" onclick="testMessage()">Test Message</button>
                <div id="testResult" style="margin-top: 10px;"></div>
            </div>
            
            <div class="info-box">
                <h3>Recent Conversations</h3>
                <div id="conversations">Loading...</div>
            </div>
        </div>
        
        <script>
            // Load initial status
            refreshStatus();
            
            async function refreshStatus() {
                try {
                    const response = await fetch('/status');
                    const status = await response.json();
                    
                    const statusDiv = document.getElementById('status');
                    const statusClass = status.status === 'Running' ? 'running' : 'stopped';
                    
                    statusDiv.innerHTML = `
                        <div class="status ${statusClass}">
                            <strong>Status:</strong> ${status.status}<br>
                            <strong>Property:</strong> ${status.property_name}<br>
                            <strong>Guest Phone:</strong> ${status.guest_phone}<br>
                            <strong>Total Messages:</strong> ${status.total_messages}<br>
                            <strong>Uptime:</strong> ${status.uptime_seconds ? Math.round(status.uptime_seconds / 60) + ' minutes' : 'N/A'}<br>
                            <strong>AI Model:</strong> ${status.ai_model}<br>
                            <strong>AI Provider:</strong> ${status.ai_provider}
                        </div>
                    `;
                    
                    // Load conversations
                    loadConversations();
                    // Load RAG stats
                    loadRAGStats();
                    
                } catch (error) {
                    console.error('Error loading status:', error);
                }
            }
            
            async function loadConversations() {
                try {
                    const response = await fetch('/conversations');
                    const conversations = await response.json();
                    
                    const conversationsDiv = document.getElementById('conversations');
                    if (conversations.length === 0) {
                        conversationsDiv.innerHTML = '<p>No conversations yet.</p>';
                        return;
                    }
                    
                    let html = '';
                    conversations.slice(-5).reverse().forEach(conv => {
                        html += `
                            <div style="border: 1px solid #ddd; margin: 10px 0; padding: 10px; border-radius: 5px;">
                                <strong>Guest:</strong> ${conv.guest_message}<br>
                                <strong>Host:</strong> ${conv.host_response}<br>
                                <small>${new Date(conv.timestamp).toLocaleString()}</small>
                            </div>
                        `;
                    });
                    
                    conversationsDiv.innerHTML = html;
                    
                } catch (error) {
                    console.error('Error loading conversations:', error);
                }
            }
            
            async function sendWelcome() {
                try {
                    const response = await fetch('/send-welcome', { method: 'POST' });
                    const result = await response.json();
                    alert(result.message);
                } catch (error) {
                    alert('Error sending welcome message');
                }
            }
            
            async function sendSummary() {
                try {
                    const response = await fetch('/send-summary', { method: 'POST' });
                    const result = await response.json();
                    alert(result.message);
                } catch (error) {
                    alert('Error sending summary');
                }
            }
            
            async function testProtocol() {
                try {
                    const response = await fetch('/test');
                    const result = await response.json();
                    alert('Protocol test completed. Check logs for details.');
                } catch (error) {
                    alert('Error testing protocol');
                }
            }
            
            async function testMessage() {
                const message = document.getElementById('testMessage').value;
                if (!message) {
                    alert('Please enter a test message');
                    return;
                }
                
                try {
                    const response = await fetch('/test-message', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                        body: `message=${encodeURIComponent(message)}`
                    });
                    
                    const result = await response.json();
                    document.getElementById('testResult').innerHTML = `
                        <div style="background-color: #d4edda; padding: 10px; border-radius: 3px; margin-top: 10px;">
                            <strong>Response:</strong> ${result.response}
                        </div>
                    `;
                    
                    // Refresh status to show new message
                    setTimeout(refreshStatus, 1000);
                    
                } catch (error) {
                    document.getElementById('testResult').innerHTML = `
                        <div style="background-color: #f8d7da; padding: 10px; border-radius: 3px; margin-top: 10px;">
                            Error testing message
                        </div>
                    `;
                }
            }
            
            async function refreshRAG() {
                try {
                    const response = await fetch('/refresh-rag', { method: 'POST' });
                    const result = await response.json();
                    alert(result.message);
                    loadRAGStats();
                } catch (error) {
                    alert('Error refreshing RAG database');
                }
            }

            async function testSMS() {
                try {
                    const response = await fetch('/test-sms', { method: 'POST' });
                    const result = await response.json();
                    alert(`SMS Test: ${result.message}\nPhone: ${result.phone}`);
                    refreshStatus();
                } catch (error) {
                    alert('Error testing SMS functionality');
                }
            }

            async function checkTwilioStatus() {
                try {
                    const response = await fetch('/twilio-status');
                    const result = await response.json();
                    
                    let statusMessage = `Twilio Status:\n`;
                    statusMessage += `✅ Configured: ${result.twilio_configured}\n`;
                    statusMessage += `📱 Phone Number: ${result.twilio_phone_number}\n`;
                    statusMessage += `👤 Guest Phone: ${result.guest_phone_number}\n`;
                    statusMessage += `🔧 Client Valid: ${result.twilio_client_valid}\n`;
                    
                    if (result.error_message) {
                        statusMessage += `❌ Error: ${result.error_message}\n`;
                    }
                    
                    if (result.recommendations) {
                        statusMessage += `\n💡 Recommendations:\n`;
                        result.recommendations.forEach(rec => {
                            statusMessage += `• ${rec}\n`;
                        });
                    }
                    
                    alert(statusMessage);
                } catch (error) {
                    alert('Error checking Twilio status');
                }
            }
            
            async function loadRAGStats() {
                try {
                    const response = await fetch('/rag-stats');
                    const stats = await response.json();
                    
                    const ragStatsDiv = document.getElementById('rag-stats');
                    if (stats.error) {
                        ragStatsDiv.innerHTML = `<p style="color: red;">Error: ${stats.error}</p>`;
                    } else {
                        ragStatsDiv.innerHTML = `
                            <p><strong>Total Documents:</strong> ${stats.total_documents || 'N/A'}</p>
                            <p><strong>Embedding Model:</strong> ${stats.embedding_model || 'N/A'}</p>
                            <p><strong>Embedding Provider:</strong> ${stats.embedding_provider || 'N/A'}</p>
                            <p><strong>Chunk Size:</strong> ${stats.chunk_size || 'N/A'}</p>
                            <p><strong>Data Directory:</strong> ${stats.data_directory || 'N/A'}</p>
                        `;
                    }
                } catch (error) {
                    document.getElementById('rag-stats').innerHTML = '<p style="color: red;">Error loading RAG stats</p>';
                }
            }
        </script>
    </body>
    </html>
    """
    return html_content


@app.get("/status")
async def get_status():
    """Get protocol status"""
    return sms_protocol.get_protocol_status()


@app.get("/conversations")
async def get_conversations(limit: int = 10):
    """Get recent conversation history"""
    return sms_protocol.get_conversation_history(limit)


@app.post("/send-welcome")
async def send_welcome():
    """Send welcome message to guest"""
    success = sms_protocol.send_welcome_message()
    if success:
        return {"message": "Welcome message sent successfully!"}
    else:
        return {"message": "Failed to send welcome message"}


@app.post("/send-summary")
async def send_summary():
    """Send property summary to guest"""
    success = sms_protocol.send_property_summary()
    if success:
        return {"message": "Property summary sent successfully!"}
    else:
        return {"message": "Failed to send property summary"}


@app.post("/test")
async def test_protocol():
    """Test the protocol functionality"""
    results = sms_protocol.test_protocol()
    return {"message": "Protocol test completed", "results": results}


@app.get("/twilio-status")
async def get_twilio_status():
    """Get Twilio configuration status"""
    # Get Twilio configuration
    twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
    twilio_phone = os.getenv("TWILIO_PHONE_NUMBER")
    guest_phone = os.getenv("GUEST_PHONE_NUMBER")
    
    # Check if credentials are set
    has_sid = bool(twilio_sid)
    has_phone = bool(twilio_phone)
    has_guest = bool(guest_phone)
    
    # Try to validate Twilio client
    twilio_valid = False
    error_message = None
    
    if has_sid and has_phone:
        try:
            # Test Twilio client initialization
            from twilio.rest import Client
            client = Client(twilio_sid, os.getenv("TWILIO_AUTH_TOKEN"))
            
            # Try to get account info
            account = client.api.accounts(twilio_sid).fetch()
            twilio_valid = True
            error_message = None
            
        except Exception as e:
            twilio_valid = False
            error_message = str(e)
    
    return {
        "twilio_configured": has_sid and has_phone,
        "account_sid_set": has_sid,
        "phone_number_set": has_phone,
        "guest_phone_set": has_guest,
        "twilio_client_valid": twilio_valid,
        "twilio_phone_number": twilio_phone,
        "guest_phone_number": guest_phone,
        "error_message": error_message,
        "recommendations": [
            "Ensure TWILIO_ACCOUNT_SID is set correctly",
            "Verify TWILIO_PHONE_NUMBER is a valid Twilio number",
            "Check if the phone number supports SMS",
            "Verify your Twilio account has SMS capabilities"
        ] if not twilio_valid else ["Twilio configuration looks good!"]
    }


@app.post("/test-sms")
async def test_sms():
    """Test SMS functionality by sending a test message"""
    guest_phone = os.getenv("GUEST_PHONE_NUMBER")
    if not guest_phone:
        raise HTTPException(status_code=500, detail="GUEST_PHONE_NUMBER not configured")
    
    # Send a test SMS message
    test_message = "🧪 This is a test SMS from your AI host assistant! The system is working perfectly! 🎉"
    sms_handler._send_sms_response(guest_phone, test_message)
    
    return {"message": "Test SMS sent successfully", "phone": guest_phone}


@app.post("/test-message")
async def test_message(message: str = Form(...)):
    """Test message processing and send SMS response"""
    # Get the guest phone number from environment
    guest_phone = os.getenv("GUEST_PHONE_NUMBER")
    if not guest_phone:
        raise HTTPException(status_code=500, detail="GUEST_PHONE_NUMBER not configured")
    
    # Process the message and send SMS response
    response = sms_protocol.process_guest_message(message, from_number=guest_phone)
    return {"message": "Message processed and SMS sent successfully", "response": response}


@app.get("/rag-stats")
async def get_rag_stats():
    """Get RAG system statistics"""
    return ai_generator.get_rag_stats()


@app.post("/refresh-rag")
async def refresh_rag_database():
    """Refresh the RAG vector database"""
    success = sms_protocol.refresh_rag_database()
    if success:
        return {"message": "RAG database refreshed successfully!"}
    else:
        return {"message": "Failed to refresh RAG database"}


@app.get("/rag-insights/{query}")
async def get_rag_insights(query: str):
    """Get RAG insights for a specific query"""
    insights = sms_protocol.get_rag_insights(query)
    return insights


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "protocol": "running" if sms_protocol.is_running else "stopped"}


async def main():
    """Main application entry point"""
    # Initialize the application
    if not await app_instance.initialize():
        logger.error("Failed to initialize application")
        return 1
    
    logger.info("SMS Host Protocol started successfully")
    logger.info("Access the dashboard at: http://localhost:8000")
    
    # Start the application loop
    await app_instance.run()
    
    return 0


if __name__ == "__main__":
    # Run the FastAPI app with uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=False
    )
