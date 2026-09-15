"""
WebSocket handler for GadgetMart assistant.
Handles real-time streaming chat via WebSocket.
"""

import json
import uuid
import logging
from typing import Dict, Optional
from fastapi import WebSocket, WebSocketDisconnect

from backend.conversation_manager import ConversationManager
from backend.prompt_builder import PromptBuilder
from backend.ollama_client import OllamaClient

logger = logging.getLogger(__name__)


class WebSocketHandler:
    """Handles WebSocket connections and streaming responses."""
    
    def __init__(self, manager: ConversationManager):
        self.manager = manager
        self.prompt_builder = PromptBuilder()
        self.ollama_client = OllamaClient()
    
    async def handle_connection(self, websocket: WebSocket):
        """
        Handle a WebSocket connection.
        
        Args:
            websocket: FastAPI WebSocket instance
        """
        await websocket.accept()
        logger.info(f"WebSocket connection accepted")
        
        try:
            while True:
                # Receive message from client
                try:
                    raw_message = await websocket.receive_text()
                except WebSocketDisconnect:
                    logger.info("Client disconnected")
                    break
                
                # Parse and handle message
                try:
                    await self._handle_message(websocket, raw_message)
                except Exception as e:
                    logger.error(f"Error handling message: {e}", exc_info=True)
                    await self._send_error(
                        websocket,
                        session_id=None,
                        error="Internal server error",
                        code="SERVER_ERROR"
                    )
        
        except Exception as e:
            logger.error(f"WebSocket error: {e}", exc_info=True)
        finally:
            logger.info("WebSocket connection closed")
    
    async def _handle_message(self, websocket: WebSocket, raw_message: str):
        """Parse and route incoming message."""
        
        # Parse JSON
        try:
            message = json.loads(raw_message)
        except json.JSONDecodeError:
            await self._send_error(
                websocket,
                session_id=None,
                error="Invalid JSON format",
                code="INVALID_JSON"
            )
            return
        
        # Validate message type
        msg_type = message.get("type")
        if not msg_type:
            await self._send_error(
                websocket,
                session_id=None,
                error="Missing 'type' field",
                code="MISSING_FIELD"
            )
            return
        
        # Route by type
        if msg_type == "message":
            await self._handle_chat_message(websocket, message)
        elif msg_type == "reset":
            await self._handle_reset(websocket, message)
        else:
            await self._send_error(
                websocket,
                session_id=message.get("session_id"),
                error=f"Unknown message type: {msg_type}",
                code="INVALID_MESSAGE_TYPE"
            )
    
    async def _handle_chat_message(self, websocket: WebSocket, message: Dict):
        """Handle a chat message request."""
        
        # Extract fields
        session_id = message.get("session_id")
        content = message.get("content")
        
        # Validate content
        if content is None:
            await self._send_error(
                websocket,
                session_id=session_id,
                error="Missing 'content' field",
                code="MISSING_FIELD"
            )
            return
        
        # Check for empty/whitespace-only content
        if not content or not content.strip():
            await self._send_error(
                websocket,
                session_id=session_id,
                error="Content cannot be empty or whitespace-only",
                code="EMPTY_CONTENT"
            )
            return
        
        # Check content length
        if len(content) > 2000:
            await self._send_error(
                websocket,
                session_id=session_id,
                error="Content exceeds 2000 character limit",
                code="CONTENT_TOO_LONG"
            )
            return
        
        # Validate session_id if provided
        if session_id is not None:
            try:
                uuid.UUID(session_id)
            except ValueError:
                await self._send_error(
                    websocket,
                    session_id=session_id,
                    error="Invalid session_id format (must be UUID)",
                    code="INVALID_SESSION"
                )
                return
        
        # Create or get session
        if session_id is None or not self.manager.session_exists(session_id):
            session_id = self.manager.create_session()
        
        # Check if session is busy
        with self.manager.global_lock:
            session = self.manager.sessions.get(session_id)
            if session and session.in_progress:
                await self._send_error(
                    websocket,
                    session_id=session_id,
                    error="Session is busy processing another request",
                    code="SESSION_BUSY"
                )
                return
        
        # Generate turn ID
        turn_id = str(uuid.uuid4())
        
        # Send start event
        await websocket.send_json({
            "type": "start",
            "session_id": session_id,
            "turn_id": turn_id
        })
        
        # Stream response
        try:
            await self._stream_response(
                websocket,
                session_id,
                turn_id,
                content
            )
        except Exception as e:
            logger.error(f"Error streaming response: {e}", exc_info=True)
            await self._send_error(
                websocket,
                session_id=session_id,
                turn_id=turn_id,
                error="Model error occurred",
                code="MODEL_ERROR"
            )
    
    async def _stream_response(
        self,
        websocket: WebSocket,
        session_id: str,
        turn_id: str,
        user_message: str
    ):
        """Stream response from Ollama."""
        
        # Acquire session lock
        with self.manager.global_lock:
            session = self.manager.sessions[session_id]
        
        if not session.lock.acquire(blocking=False):
            await self._send_error(
                websocket,
                session_id=session_id,
                turn_id=turn_id,
                error="Session busy",
                code="SESSION_BUSY"
            )
            return
        
        try:
            session.in_progress = True
            
            # Trim history if needed
            current_turn_count = sum(
                1 for m in session.history if m["role"] == "user"
            )
            
            if current_turn_count >= self.manager.max_history_turns:
                session.history = self.prompt_builder.trim_history(
                    session.history,
                    self.manager.max_history_turns - 1
                )
            
            # Build messages
            session_summary = self.prompt_builder.create_session_summary(
                session.history
            )
            
            messages = self.prompt_builder.build_messages(
                history=session.history,
                user_message=user_message,
                session_summary=session_summary if session_summary else None
            )
            
            # Stream from Ollama
            full_response = ""
            token_count = None
            
            async for chunk in self.ollama_client.chat_stream(messages):
                # Extract content
                content = chunk.get("message", {}).get("content", "")
                
                if content:
                    full_response += content
                    
                    # Send chunk event
                    await websocket.send_json({
                        "type": "chunk",
                        "session_id": session_id,
                        "turn_id": turn_id,
                        "content": content
                    })
                
                # Check if done
                if chunk.get("done"):
                    token_count = chunk.get("eval_count")
                    break
            
            # Add to history only after successful completion
            session.add_message("user", user_message)
            session.add_message("assistant", full_response)
            
            # Send done event
            await websocket.send_json({
                "type": "done",
                "session_id": session_id,
                "turn_id": turn_id,
                "total_tokens": token_count
            })
        
        finally:
            session.in_progress = False
            session.lock.release()
    
    async def _handle_reset(self, websocket: WebSocket, message: Dict):
        """Handle a session reset request."""
        
        session_id = message.get("session_id")
        
        # Validate session_id
        if not session_id:
            await self._send_error(
                websocket,
                session_id=None,
                error="Missing 'session_id' field for reset",
                code="MISSING_FIELD"
            )
            return
        
        try:
            uuid.UUID(session_id)
        except ValueError:
            await self._send_error(
                websocket,
                session_id=session_id,
                error="Invalid session_id format (must be UUID)",
                code="INVALID_SESSION"
            )
            return
        
        # Check if session exists
        if not self.manager.session_exists(session_id):
            await self._send_error(
                websocket,
                session_id=session_id,
                error="Session not found",
                code="INVALID_SESSION"
            )
            return
        
        # Reset session
        self.manager.reset_session(session_id)
        
        # Send reset acknowledgment
        await websocket.send_json({
            "type": "reset",
            "session_id": session_id
        })
    
    async def _send_error(
        self,
        websocket: WebSocket,
        session_id: Optional[str],
        error: str,
        code: str,
        turn_id: Optional[str] = None
    ):
        """Send an error event to the client."""
        
        error_event = {
            "type": "error",
            "session_id": session_id,
            "error": error,
            "code": code
        }
        
        if turn_id:
            error_event["turn_id"] = turn_id
        
        await websocket.send_json(error_event)
