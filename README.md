# 🤖 GANI - Chat with Ganesh

GANI is an intelligent RAG-powered chatbot that mimics Ganesh's personality, knowledge, and communication style. It provides accurate, contextual responses based on embedded knowledge from personal, website, and Medium content.

## ✨ Features

- **Intent-Aware Routing**: Automatically categorizes questions into intro, technical, HR, or manager modes
- **Hybrid Retrieval**: Uses BGE embeddings to query Pinecone vector database across multiple namespaces
- **Context-Aware Responses**: Generates answers with inline citations and source links
- **Confidence Scoring**: Provides groundedness verification and confidence metrics
- **Session Memory**: Remembers conversation context using IP+UA hashing
- **Modern Web UI**: Clean, responsive chat interface with real-time interactions

## 🏗️ Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Web UI    │───▶│  FastAPI    │───▶│ Intent     │───▶│ Pinecone    │
│             │    │   Backend   │    │ Router     │    │ Vector DB   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                           │                   │
                           ▼                   ▼
                    ┌─────────────┐    ┌─────────────┐
                    │ Context     │    │ OpenRouter  │
                    │ Packer      │    │ LLM API     │
                    └─────────────┘    └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ Verifier    │
                    │ & Memory    │
                    └─────────────┘
```

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env
```

**Required Environment Variables:**
- `OPENROUTER_API_KEY`: Your OpenRouter API key
- `PINECONE_API_KEY`: Your Pinecone API key
- `PINECONE_INDEX`: Pinecone index name (default: gani)
- `PINECONE_REGION`: Pinecone region (default: us-east-1)

### 3. Start the Backend

```bash
# Start FastAPI server
uvicorn api.chat:app --reload --port 8000
```

### 4. Start the Frontend

```bash
# In a new terminal, serve the web UI
cd web
python -m http.server 3000
```

### 5. Access the Application

- **Backend API**: http://localhost:8000
- **Web UI**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

## 🧪 Testing

### Health Check

```bash
curl http://localhost:8000/health
```

### Chat Endpoint

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"Give me a 3-line intro about Ganesh."}'
```

### Expected Response Format

```json
{
  "answer_short": "Brief 1-2 sentence answer",
  "answer_expanded": "Detailed answer with inline citations [1], [2], etc.",
  "citations": [
    {"url": "source_url", "section": "section_name"}
  ],
  "confidence": 0.85,
  "intent": "intro",
  "session_id": "abc123..."
}
```

## 🔧 Configuration

### config.yaml

```yaml
app:
  model: openai/gpt-oss-20b
  temperature: 0.2
  top_p: 0.9
  k_context: 6

pinecone:
  index: gani
  cloud: aws
  region: us-east-1
  namespaces: [personal, website, medium]

retrieval:
  chunk_char_limit: 1200
  embedding_model: BAAI/bge-large-en-v1.5
```

## 📁 Project Structure

```
GANI/
├── api/
│   └── chat.py              # FastAPI application & chat endpoint
├── rag/
│   ├── intent_router.py     # Question intent classification
│   ├── retriever.py         # BGE embeddings & Pinecone queries
│   ├── context_packer.py    # Context formatting & chunking
│   └── verifier.py          # Response validation & confidence
├── memory/
│   └── store.py             # Session memory (Redis + fallback)
├── prompts/
│   └── system.txt           # LLM system prompt
├── web/
│   ├── index.html           # Chat UI
│   └── script.js            # Frontend logic
├── config.yaml              # Application configuration
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
└── README.md                # This file
```

## 🎯 Intent Categories

### Intro Mode
- Personal background, elevator pitch
- Keywords: intro, about, background, who are you

### Technical Mode
- Project details, technical explanations
- Keywords: WSDM, machine learning, code, algorithm

### HR Mode
- Behavioral questions, conflict resolution
- Keywords: conflict, teamwork, challenge, STAR format

### Manager Mode
- Leadership, prioritization, strategy
- Keywords: lead, manage, roadmap, tradeoff

## 🔍 Retrieval Strategy

- **Namespace Weighting**: Different weights per intent for optimal relevance
- **Hybrid Search**: Combines multiple Pinecone namespaces
- **Deduplication**: Removes duplicate content by URL and text similarity
- **Context Packing**: Formats snippets into numbered blocks with source attribution

## 🧠 Memory System

- **Session ID**: Generated from IP address + User Agent hash
- **Storage Options**: Redis (persistent) or in-memory (fallback)
- **TTL**: Configurable expiration (default: 7 days)
- **Context**: Remembers last question and intent for continuity

## 🚨 Troubleshooting

### Common Issues

1. **Pinecone Connection Error**
   - Verify API key and region
   - Ensure index exists and is accessible

2. **OpenRouter API Error**
   - Check API key validity
   - Verify model name and quota

3. **Import Errors**
   - Ensure virtual environment is activated
   - Check Python path and module structure

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
uvicorn api.chat:app --reload --port 8000 --log-level debug
```

## 📊 Performance

- **Response Time**: Typically 2-5 seconds
- **Context Window**: 1200 characters max
- **Retrieval**: Top 6 most relevant snippets
- **Memory**: Session-based with configurable TTL

## 🔒 Security

- **API Keys**: Stored in environment variables only
- **CORS**: Configurable for production deployment
- **Input Validation**: Pydantic models for request validation
- **Error Handling**: Graceful fallbacks without exposing internals

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is for personal use and demonstration purposes.

## 🙏 Acknowledgments

- **BGE Embeddings**: BAAI for the embedding model
- **Pinecone**: Vector database infrastructure
- **OpenRouter**: LLM API access
- **FastAPI**: Modern Python web framework

---

**Ready to chat with GANI?** 🚀 Start the backend and open the web UI to begin your conversation!
