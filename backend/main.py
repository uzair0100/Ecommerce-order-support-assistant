"""
FastAPI application for GadgetMart assistant.
Provides REST health endpoint and WebSocket chat endpoint.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.conversation_manager import ConversationManager
from backend.websocket_handler import WebSocketHandler
from backend.ollama_client import OllamaClient
from backend.config import MODEL_NAME

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize conversation manager
manager = ConversationManager()
websocket_handler = WebSocketHandler(manager)
ollama_client = OllamaClient()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("GadgetMart Assistant API starting...")
    logger.info(f"Model: {MODEL_NAME}")
    logger.info("WebSocket endpoint: /ws/chat")
    logger.info("Health check endpoint: /health")
    
    yield
    
    # Shutdown
    logger.info("GadgetMart Assistant API shutting down...")
    # Note: In-memory sessions will be lost (documented behavior)


# Create FastAPI app with lifespan
app = FastAPI(
    title="GadgetMart Assistant API",
    description="Local conversational AI assistant for GadgetMart e-commerce support",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - allow local frontend origins
# Update these origins to match your frontend URLs
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React default
        "http://localhost:5173",  # Vite default
        "http://localhost:8080",  # Python http.server / Vue / static
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
        "http://localhost:8000",  # Testing from same origin
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns server health and Ollama availability status separately.
    Does not hang waiting for Ollama.
    """
    # Server is healthy if we can respond
    server_healthy = True
    
    # Quick Ollama check (with timeout)
    try:
        ollama_available = ollama_client.health_check()
    except Exception as e:
        logger.error(f"Ollama health check failed: {e}")
        ollama_available = False
    
    # Get active session count
    active_sessions = len(manager.list_sessions())
    
    # Determine overall status
    # Server reports degraded if Ollama is unavailable
    if not ollama_available:
        status = "degraded"
    else:
        status = "healthy"
    
    return JSONResponse(
        status_code=200 if server_healthy else 503,
        content={
            "status": status,
            "server_healthy": server_healthy,
            "ollama_available": ollama_available,
            "model": MODEL_NAME,
            "active_sessions": active_sessions
        }
    )


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket endpoint for real-time chat.
    
    Protocol:
    
    Client → Server:
        {
            "type": "message",
            "session_id": "uuid-or-null",
            "content": "user message"
        }
        
        OR
        
        {
            "type": "reset",
            "session_id": "uuid"
        }
    
    Server → Client:
        {"type": "start", "session_id": "uuid", "turn_id": "uuid"}
        {"type": "chunk", "session_id": "uuid", "turn_id": "uuid", "content": "text"}
        {"type": "done", "session_id": "uuid", "turn_id": "uuid", "total_tokens": 123}
        {"type": "error", "session_id": "uuid", "error": "msg", "code": "ERROR_CODE"}
        {"type": "reset", "session_id": "uuid"}
    """
    # Check WebSocket origin for security
    origin = websocket.headers.get("origin")
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
    ]
    
    if origin and origin not in allowed_origins:
        logger.warning(f"Rejected WebSocket connection from origin: {origin}")
        await websocket.close(code=1008, reason="Origin not allowed")
        return
    
    await websocket_handler.handle_connection(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
