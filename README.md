# 🏠 SMS Host Protocol

An intelligent, automated SMS host assistant that responds to guest messages using **Mistral Large** LLM. This system reads your property information from a text file and automatically generates friendly, helpful responses to common guest questions.

## ✨ Features

- **🤖 AI-Powered Responses**: Uses **Mistral Large** for natural, helpful communication
- **📱 SMS Integration**: Handles guest messages via Twilio SMS
- **📋 Smart Property Parser**: Reads plain text property files and extracts key information
- **🎯 Context-Aware**: Generates responses based on your actual property details
- **🌐 Web Dashboard**: Beautiful interface for monitoring and testing
- **🐳 Docker Ready**: Easy deployment with Docker Compose
- **📊 Conversation History**: Tracks all guest interactions

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.11+
- Docker and Docker Compose
- **Mistral AI API key** (get one at [mistral.ai](https://mistral.ai))
- Twilio account (for SMS)

### 2. Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd sms-host-protocol

# Copy environment template
cp env.example .env

# Edit .env with your API keys
nano .env
```

### 3. Configure Environment

Edit your `.env` file with:

```bash
# Mistral AI Configuration
MISTRAL_API_KEY=your_mistral_api_key_here
MISTRAL_MODEL=mistral-large-latest

# Twilio SMS Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_PHONE_NUMBER=your_twilio_phone_number_here

# Guest Phone Number (fixed number to respond to)
GUEST_PHONE_NUMBER=+1234567890
```

### 4. Customize Your Property Information

Edit `data/airbnblisting.txt` with your property details:

```text
PROPERTY NAME: Your Property Name
LOCATION: Your City, State
ADDRESS: Your Full Address

CHECK-IN & CHECK-OUT:
Check-in time: 3:00 PM
Check-out time: 11:00 AM

AMENITIES:
WiFi: Free high-speed WiFi included
Kitchen: Fully equipped kitchen
Parking: Free parking available

HOUSE RULES:
No smoking
No pets allowed
Quiet hours: 10:00 PM to 8:00 AM
```

### 5. Run with Docker

```bash
# Build and start the system
docker-compose up -d

# View logs
docker-compose logs -f sms-host-protocol

# Access dashboard
open http://localhost:8000
```

## 🧪 Testing

### Test the System

```bash
# Run all tests (recommended)
python test/run_all_tests.py

# Run individual tests
python test/test_system.py      # System functionality tests
python test/test_rag.py         # RAG architecture tests

# Test specific questions via API
curl -X POST "http://localhost:8000/test-message" \
  -d "message=Do you have WiFi?"
```

### Test Folder Structure

```
test/
├── __init__.py              # Test package initialization
├── run_all_tests.py         # Test runner (runs all tests)
├── test_system.py           # System functionality tests
└── test_rag.py              # RAG architecture tests
```

### Test Message Processing

1. Open the web dashboard at `http://localhost:8000`
2. Use the "Test Message Processing" section
3. Try questions like:
   - "Do you have WiFi?"
   - "What time is check-in?"
   - "Is parking included?"

## 📱 How It Works

### 1. **Property Information**
- System reads your property details from `data/airbnblisting.txt`
- Parses information into structured sections (amenities, rules, etc.)
- Provides context for AI responses

### 2. **Guest Communication**
- Guest sends SMS to your Twilio number
- System validates the sender (only responds to authorized number)
- **Mistral Large** generates contextual response based on your property
- Response sent back via SMS

### 3. **AI Response Generation**
- Uses **Mistral Large** for natural language understanding
- Generates casual, friendly responses
- Incorporates your property details
- Maintains conversation context

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Guest SMS     │───▶│  Twilio SMS      │───▶│  SMS Handler    │
└─────────────────┘    │  Service         │    └─────────────────┘
                       └──────────────────┘             │
                                                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   AI Response   │◀───│  Mistral Large   │◀───│  Message        │
│   (SMS)        │    │  LLM API         │    │  Processor      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │  Property Parser │    │  Conversation   │
                       │  (data/*.txt)    │    │  History        │
                       └──────────────────┘    └─────────────────┘
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `MISTRAL_API_KEY` | Your Mistral AI API key | ✅ |
| `MISTRAL_MODEL` | Mistral model to use (default: mistral-large-latest) | ❌ |
| `TWILIO_ACCOUNT_SID` | Twilio account SID | ✅ |
| `TWILIO_AUTH_TOKEN` | Twilio auth token | ✅ |
| `TWILIO_PHONE_NUMBER` | Your Twilio phone number | ✅ |
| `GUEST_PHONE_NUMBER` | Guest phone number to respond to | ✅ |

### Property Information File Format

The system expects a plain text file with sections:

```text
SECTION NAME: Content here
ANOTHER SECTION: More content
  - Can include bullet points
  - And multiple lines
```

## 📊 Dashboard Features

- **System Status**: Monitor protocol health and uptime
- **AI Info**: Shows Mistral Large model status
- **Quick Actions**: Send welcome messages and property summaries
- **Message Testing**: Test AI responses without sending SMS
- **Conversation History**: View recent guest interactions
- **Real-time Updates**: Auto-refreshing status information

## 🐳 Docker Commands

```bash
# Start the system
docker-compose up -d

# Stop the system
docker-compose down

# View logs
docker-compose logs -f

# Restart a service
docker-compose restart sms-host-protocol

# Rebuild and restart
docker-compose up -d --build

# Check service status
docker-compose ps
```

## 🔍 Troubleshooting

### Common Issues

1. **"Missing required environment variables"**
   - Check your `.env` file exists and has all required variables
   - Ensure no extra spaces or quotes around values

2. **"Mistral AI API error"**
   - Verify your Mistral API key is correct
   - Check your Mistral account has credits
   - Ensure the API key has access to mistral-large-latest

3. **"Twilio configuration error"**
   - Verify Twilio credentials are correct
   - Check Twilio phone number format (+1XXXXXXXXXX)
   - Ensure Twilio account is active

4. **"Property file not found"**
   - Ensure `data/airbnblisting.txt` exists
   - Check file permissions
   - Verify file path in Docker volume mapping

### Logs

```bash
# View application logs
docker-compose logs sms-host-protocol

# View real-time logs
docker-compose logs -f sms-host-protocol

# Check specific time period
docker-compose logs --since="2024-01-01T00:00:00" sms-host-protocol
```

## 🔒 Security

- **Phone Number Validation**: Only responds to authorized guest number
- **Environment Variables**: Sensitive data stored in `.env` file
- **Docker Isolation**: Runs in isolated container environment
- **No Data Persistence**: Conversation history stored in memory only

## 📈 Monitoring

### Health Check

```bash
# Check system health
curl http://localhost:8000/health

# Get system status
curl http://localhost:8000/status

# View recent conversations
curl http://localhost:8000/conversations
```

### Metrics Available

- Total messages processed
- System uptime
- Conversation history count
- Component status
- Error counts
- AI model information

## 🚀 Production Deployment

### Environment Considerations

1. **SSL/TLS**: Use reverse proxy (nginx) with SSL certificates
2. **Load Balancing**: Consider multiple instances for high availability
3. **Monitoring**: Add Prometheus/Grafana for metrics
4. **Backup**: Regular backup of property data and configuration
5. **Updates**: Regular security updates and dependency management

### Scaling

```bash
# Scale to multiple instances
docker-compose up -d --scale sms-host-protocol=3

# Use external database for conversation history
# (modify code to use PostgreSQL/Redis)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Issues**: Create GitHub issue
- **Documentation**: Check this README
- **Testing**: Use `python test/run_all_tests.py` (recommended) or `python test/test_system.py`
- **Logs**: Check Docker logs for errors

---

**Happy hosting! 🏠✨**

Your AI assistant powered by **Mistral Large** is ready to help guests have an amazing stay at your property.
