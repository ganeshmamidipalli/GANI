import os
import yaml
import json
import requests
from typing import Dict, Any
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import our RAG components
import sys
sys.path.append('..')

from rag.intent_router import IntentRouter
from rag.retriever import Retriever
from rag.context_packer import ContextPacker
from rag.verifier import Verifier

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
def load_config():
    """Load configuration from config.yaml"""
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return {}

config = load_config()

# Initialize components (will be done in startup event)
intent_router = None
retriever = None
context_packer = None
verifier = None

# Load system prompt
def load_system_prompt():
    """Load system prompt from prompts/system.txt"""
    try:
        with open('prompts/system.txt', 'r') as f:
            return f.read().strip()
    except Exception as e:
        logger.error(f"Error loading system prompt: {e}")
        return "You are GANI, an AI assistant that mimics Ganesh's personality."

system_prompt = load_system_prompt()

# FastAPI app
app = FastAPI(title="GANI Chatbot", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    global intent_router, retriever, context_packer, verifier
    
    try:
        # Debug: Check environment variables
        pinecone_key = os.getenv('PINECONE_API_KEY')
        openrouter_key = os.getenv('OPENROUTER_API_KEY')
        logger.info(f"PINECONE_API_KEY: {'✅ Set' if pinecone_key else '❌ Missing'}")
        logger.info(f"OPENROUTER_API_KEY: {'✅ Set' if openrouter_key else '❌ Missing'}")
        
        intent_router = IntentRouter()
        retriever = Retriever(
            api_key=pinecone_key,
            index_name=os.getenv('PINECONE_INDEX', config.get('pinecone', {}).get('index', 'gani')),
            region=os.getenv('PINECONE_REGION', config.get('pinecone', {}).get('region', 'us-east-1'))
        )
        context_packer = ContextPacker(
            char_limit=config.get('retrieval', {}).get('chunk_char_limit', 1200)
        )
        verifier = Verifier()
        logger.info("✅ All components initialized successfully")
    except Exception as e:
        logger.error(f"❌ Error initializing components: {e}")
        raise e

# Request/Response models
class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer_short: str
    answer_expanded: str
    citations: list
    confidence: float
    intent: str
    session_id: str

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "GANI Chatbot API",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # Check Pinecone connection
        pinecone_stats = retriever.get_namespace_info()
        
        return {
            "status": "healthy",
            "pinecone": pinecone_stats,
            "config_loaded": bool(config)
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, http_request: Request):
    """Main chat endpoint"""
    try:
        # Generate simple session ID (without memory store)
        client_ip = http_request.client.host
        user_agent = http_request.headers.get("user-agent", "")
        session_id = f"session_{hash(client_ip + user_agent) % 10000:04d}"
        
        logger.info(f"Chat request from session {session_id}: {request.question}")
        
        # Route intent
        intent = intent_router.route_intent(request.question)
        logger.info(f"Routed to intent: {intent}")
        
        # Retrieve relevant snippets
        snippets = retriever.retrieve(
            query=request.question,
            intent=intent,
            k_context=config.get('app', {}).get('k_context', 6)
        )
        
        if not snippets:
            logger.warning("No relevant snippets found")
            return ChatResponse(
                answer_short="I don't have enough information to answer that question.",
                answer_expanded="I don't have enough information about that specific topic. Could you provide more details or share a link/document so I can give you a better answer?",
                citations=[],
                confidence=0.0,
                intent=intent,
                session_id=session_id
            )
        
        # Pack context
        packed_context = context_packer.pack(snippets)
        logger.info(f"Packed context: {len(snippets)} snippets, {len(packed_context)} chars")
        
        # Prepare LLM request
        llm_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{packed_context}\n\nQuestion: {request.question}"}
        ]
        
        # Call OpenRouter API
        openrouter_response = await call_openrouter(llm_messages)
        
        if not openrouter_response:
            raise HTTPException(status_code=500, detail="Failed to get response from OpenRouter")
        
        # Parse and validate response
        parsed_response = verifier.validate_json_response(openrouter_response)
        
        if not parsed_response['is_valid']:
            logger.warning(f"Invalid JSON response: {parsed_response['error']}")
            # Create fallback response
            response_data = {
                "answer_short": "I'm having trouble formatting my response properly.",
                "answer_expanded": openrouter_response,
                "citations": verifier.extract_citations_from_snippets(snippets),
                "confidence": 0.5,
                "intent": intent,
                "session_id": session_id
            }
        else:
            response_data = parsed_response['parsed']
            response_data['intent'] = intent
            response_data['session_id'] = session_id
            
            # Fill citations if missing
            if not response_data.get('citations'):
                response_data['citations'] = verifier.extract_citations_from_snippets(snippets)
        
        # Calculate confidence
        groundedness = verifier.groundedness_score(
            response_data['answer_expanded'], 
            packed_context
        )
        response_data['confidence'] = verifier.build_confidence(groundedness)
        
        logger.info(f"Chat response generated with confidence: {response_data['confidence']:.2f}")
        
        return ChatResponse(**response_data)
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def call_openrouter(messages: list) -> str:
    """Call OpenRouter API for chat completion"""
    try:
        api_key = os.getenv('OPENROUTER_API_KEY')
        model = os.getenv('OPENROUTER_MODEL', config.get('app', {}).get('model', 'openai/gpt-oss-20b'))
        
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not found")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": config.get('app', {}).get('temperature', 0.2),
            "top_p": config.get('app', {}).get('top_p', 0.9),
            "max_tokens": 1000
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        result = response.json()
        
        return result['choices'][0]['message']['content']
        
    except Exception as e:
        logger.error(f"OpenRouter API call failed: {e}")
        return None

@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    try:
        return {
            "pinecone": retriever.get_namespace_info(),
            "config": {
                "model": config.get('app', {}).get('model'),
                "k_context": config.get('app', {}).get('k_context'),
                "namespaces": config.get('pinecone', {}).get('namespaces')
            }
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
