"""
Conversation manager for GadgetMart assistant.
Handles session management, conversation history, and turn-taking.
"""

import uuid
import threading
from typing import Dict, List, Optional
from datetime import datetime

from backend.ollama_client import OllamaClient
from backend.prompt_builder import PromptBuilder
from backend.config import MAX_HISTORY_TURNS


class ConversationSession:
    """Represents a single conversation session."""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.history: List[Dict[str, str]] = []
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.lock = threading.Lock()  # Prevent concurrent turns
        self.in_progress = False  # Guard against overlapping requests
    
    def add_message(self, role: str, content: str):
        """Add a message to conversation history."""
        self.history.append({
            "role": role,
            "content": content
        })
        self.last_activity = datetime.now()
    
    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history."""
        return self.history.copy()
    
    def clear_history(self):
        """Clear conversation history (for reset)."""
        self.history = []
        self.last_activity = datetime.now()


class ConversationManager:
    """
    Manages multiple conversation sessions with isolated state.
    
    Features:
    - Per-session conversation history
    - Bounded context with automatic trimming
    - Turn-taking guard (no overlapping requests per session)
    - Session isolation
    - In-memory storage (sessions lost on restart)
    """
    
    def __init__(
        self,
        ollama_client: Optional[OllamaClient] = None,
        prompt_builder: Optional[PromptBuilder] = None,
        max_history_turns: int = MAX_HISTORY_TURNS
    ):
        self.sessions: Dict[str, ConversationSession] = {}
        self.ollama_client = ollama_client or OllamaClient()
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.max_history_turns = max_history_turns
        self.global_lock = threading.Lock()
    
    def create_session(self) -> str:
        """
        Create a new conversation session.
        
        Returns:
            session_id: Unique session identifier
        """
        session_id = str(uuid.uuid4())
        
        with self.global_lock:
            self.sessions[session_id] = ConversationSession(session_id)
        
        return session_id
    
    def session_exists(self, session_id: str) -> bool:
        """Check if a session exists."""
        with self.global_lock:
            return session_id in self.sessions
    
    def reset_session(self, session_id: str) -> bool:
        """
        Reset a session's conversation history.
        
        Args:
            session_id: Session to reset
        
        Returns:
            True if session was reset, False if session doesn't exist
        """
        with self.global_lock:
            if session_id not in self.sessions:
                return False
            
            self.sessions[session_id].clear_history()
            return True
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session completely.
        
        Args:
            session_id: Session to delete
        
        Returns:
            True if session was deleted, False if not found
        """
        with self.global_lock:
            if session_id in self.sessions:
                del self.sessions[session_id]
                return True
            return False
    
    def get_response(
        self,
        session_id: str,
        user_message: str
    ) -> Optional[str]:
        """
        Get a response from the assistant for the given user message.
        
        This is the main entry point for generating responses.
        
        Args:
            session_id: Session identifier
            user_message: User's input message
        
        Returns:
            Assistant response text, or None if error or session not found
        """
        # Check session exists
        with self.global_lock:
            if session_id not in self.sessions:
                return None
            session = self.sessions[session_id]
        
        # Acquire session lock to prevent overlapping requests
        if not session.lock.acquire(blocking=False):
            return "[ERROR: Another request is in progress for this session]"
        
        try:
            session.in_progress = True
            
            # Trim history BEFORE adding new message if needed
            # Check if adding this turn would exceed limit
            current_turn_count = sum(
                1 for m in session.history if m["role"] == "user"
            )
            
            if current_turn_count >= self.max_history_turns:
                session.history = self.prompt_builder.trim_history(
                    session.history,
                    self.max_history_turns - 1  # Leave room for new turn
                )
            
            # Create session summary
            session_summary = self.prompt_builder.create_session_summary(
                session.history
            )
            
            # Build messages for Ollama
            messages = self.prompt_builder.build_messages(
                history=session.history,
                user_message=user_message,
                session_summary=session_summary if session_summary else None
            )
            
            # Call Ollama
            response = self.ollama_client.chat(messages, stream=False)
            
            if response is None:
                return "[ERROR: Failed to get response from model]"
            
            # Add to history only after successful response
            session.add_message("user", user_message)
            session.add_message("assistant", response)
            
            return response
        
        finally:
            session.in_progress = False
            session.lock.release()
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """
        Get information about a session.
        
        Returns:
            Dict with session metadata, or None if not found
        """
        with self.global_lock:
            if session_id not in self.sessions:
                return None
            
            session = self.sessions[session_id]
            return {
                "session_id": session.session_id,
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "turn_count": len([
                    m for m in session.history if m["role"] == "user"
                ]),
                "in_progress": session.in_progress
            }
    
    def list_sessions(self) -> List[str]:
        """
        List all active session IDs.
        
        Returns:
            List of session IDs
        """
        with self.global_lock:
            return list(self.sessions.keys())
