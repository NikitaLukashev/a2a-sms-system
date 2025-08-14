# 🏗️ SMS Host Protocol - Project UML Architecture

## 📊 Class Diagram

```mermaid
classDiagram
    %% Main Application Layer
    class FastAPI {
        +app: FastAPI
        +startup_event()
        +shutdown_event()
    }
    
    class SMSHostApp {
        -protocol: SMSHostProtocol
        -running: bool
        +initialize() bool
        +run()
        +cleanup()
        -_signal_handler()
        -_validate_environment() bool
    }
    
    %% Controller Layer
    class SMSHostProtocol {
        -protocol_id: str
        -agent_id: str
        -is_running: bool
        -start_time: datetime
        -message_count: int
        -conversation_history: List
        +start() bool
        +stop()
        +process_guest_message() str
        +refresh_rag_database() bool
        +get_rag_insights() Dict
        -_validate_config() bool
        -_initialize_components() bool
    }
    
    class AIResponseGenerator {
        -client: MistralClient
        -model: str
        +generate_response() str
        +get_property_summary() str
        +get_rag_stats() Dict
        -_get_relevant_context() str
        -_build_prompt() str
        -_get_system_prompt() str
        -_clean_response() str
    }
    
    class SMSHandler {
        -client: Client
        -twilio_phone: str
        -guest_phone: str
        +process_incoming_sms() str
        +send_welcome_message()
        +send_property_summary()
        +test_sms_functionality()
        -_send_sms_response()
        -_generate_twiml_response() str
        -_generate_unauthorized_response() str
    }
    
    %% Configuration Layer
    class RAGPropertyParser {
        -data_directory: Path
        -persist_directory: Path
        -vector_store: Chroma
        -embeddings: MistralEmbeddings
        -text_splitter: RecursiveCharacterTextSplitter
        +query_property_info() List
        +get_property_summary() str
        +refresh_database()
        +get_database_stats() Dict
        -_initialize_components()
        -_setup_vector_database()
        -_create_vector_database()
        -_is_docker_environment() bool
        -_reset_chromadb_instances()
    }
    
    class MistralEmbeddings {
        -model: str
        -api_key: str
        -client: MistralClient
        +embed_documents() List
        +embed_query() List
    }
    
    %% External Dependencies
    class MistralClient {
        +chat()
        +embeddings()
    }
    
    class TwilioClient {
        +messages.create()
    }
    
    class Chroma {
        +from_documents()
        +similarity_search_with_score()
    }
    
    class LangChain {
        +RecursiveCharacterTextSplitter
        +Document
    }
    
    %% Relationships
    FastAPI --> SMSHostApp : uses
    SMSHostApp --> SMSHostProtocol : manages
    
    SMSHostProtocol --> RAGPropertyParser : uses
    SMSHostProtocol --> AIResponseGenerator : uses
    SMSHostProtocol --> SMSHandler : uses
    
    AIResponseGenerator --> RAGPropertyParser : queries
    AIResponseGenerator --> MistralClient : uses
    
    SMSHandler --> AIResponseGenerator : uses
    SMSHandler --> TwilioClient : uses
    
    RAGPropertyParser --> MistralEmbeddings : uses
    RAGPropertyParser --> Chroma : uses
    RAGPropertyParser --> LangChain : uses
    
    MistralEmbeddings --> MistralClient : uses
```

## 🏛️ Architecture Overview

### **📱 Application Layers:**

#### **1. Presentation Layer (FastAPI)**
- **FastAPI App**: Main web application with REST endpoints
- **SMSHostApp**: Application lifecycle management

#### **2. Controller Layer**
- **SMSHostProtocol**: Main orchestrator and business logic
- **AIResponseGenerator**: AI-powered response generation
- **SMSHandler**: SMS messaging and Twilio integration

#### **3. Configuration Layer**
- **RAGPropertyParser**: RAG architecture and vector database
- **MistralEmbeddings**: Custom embeddings for LangChain

### **🔗 Key Dependencies:**

#### **Core Dependencies:**
- **SMSHostProtocol** → **RAGPropertyParser** (RAG queries)
- **SMSHostProtocol** → **AIResponseGenerator** (AI responses)
- **SMSHostProtocol** → **SMSHandler** (SMS operations)

#### **AI Chain:**
- **AIResponseGenerator** → **RAGPropertyParser** (context retrieval)
- **AIResponseGenerator** → **MistralClient** (LLM generation)

#### **Data Flow:**
- **RAGPropertyParser** → **MistralEmbeddings** → **MistralClient**
- **RAGPropertyParser** → **Chroma** → **LangChain**

### **🚀 Design Patterns:**

#### **1. Orchestrator Pattern**
- **SMSHostProtocol** coordinates all components

#### **2. Strategy Pattern**
- **MistralEmbeddings** provides embedding strategy
- **RAGPropertyParser** provides retrieval strategy

#### **3. Factory Pattern**
- **Chroma.from_documents()** creates vector stores

#### **4. Observer Pattern**
- **SMSHostApp** observes protocol state changes

### **📊 Data Flow:**

```
Guest SMS → SMSHandler → AIResponseGenerator → RAGPropertyParser
    ↓
RAGPropertyParser → MistralEmbeddings → MistralClient
    ↓
AIResponseGenerator → MistralClient → Response
    ↓
SMSHandler → TwilioClient → Guest SMS
```

### **🔧 Key Features:**

- **Modular Architecture**: Clear separation of concerns
- **Dependency Injection**: Components are loosely coupled
- **Error Handling**: Graceful fallbacks and error recovery
- **Configuration Management**: Environment-based configuration
- **Docker Support**: Environment-aware database strategies

This architecture provides a robust, scalable foundation for the SMS Host Protocol system! 🎯
