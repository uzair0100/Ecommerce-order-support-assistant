"""
Prompt builder for GadgetMart assistant.
Constructs system prompt and manages conversation history.
"""

from typing import List, Dict, Optional
from pathlib import Path
from backend.config import STORE_FACTS_FILE


class PromptBuilder:
    """Builds system prompts and manages conversation context."""
    
    def __init__(self, facts_file: str = STORE_FACTS_FILE):
        self.system_prompt = self._load_system_prompt(facts_file)
    
    def _load_system_prompt(self, facts_file: str) -> str:
        """Load GadgetMart facts from file."""
        facts_path = Path(facts_file)
        
        if not facts_path.exists():
            raise FileNotFoundError(
                f"Store facts file not found: {facts_file}"
            )
        
        with open(facts_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    
    def build_messages(
        self,
        history: List[Dict[str, str]],
        user_message: str,
        session_summary: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Build message list for Ollama /api/chat.
        
        Args:
            history: List of previous messages (role: user/assistant, content: text)
            user_message: Current user input
            session_summary: Optional compact summary of session state
        
        Returns:
            List of message dicts with 'role' and 'content'
        """
        messages = []
        
        # System message with GadgetMart facts
        system_content = self.system_prompt
        
        # Add session summary if available
        if session_summary:
            system_content += f"\n\nSession context: {session_summary}"
        
        messages.append({
            "role": "system",
            "content": system_content
        })
        
        # Add conversation history
        for msg in history:
            messages.append(msg)
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        return messages
    
    def estimate_token_count(self, text: str) -> int:
        """
        Rough token count estimation.
        Uses simple heuristic: ~4 chars per token for English text.
        
        This is approximate; actual tokenization may differ.
        """
        return len(text) // 4
    
    def should_trim_history(
        self,
        history: List[Dict[str, str]],
        max_turns: int
    ) -> bool:
        """
        Check if history should be trimmed.
        
        Args:
            history: Current conversation history
            max_turns: Maximum number of turn pairs to keep
        
        Returns:
            True if history exceeds max_turns
        """
        # Count user messages (each represents a turn)
        user_message_count = sum(
            1 for msg in history if msg["role"] == "user"
        )
        
        return user_message_count > max_turns
    
    def trim_history(
        self,
        history: List[Dict[str, str]],
        max_turns: int
    ) -> List[Dict[str, str]]:
        """
        Trim oldest turns from history while preserving recent context.
        
        Removes complete turn pairs (user + assistant) from the beginning.
        Always preserves the most recent turns up to max_turns.
        
        Args:
            history: Current conversation history
            max_turns: Maximum number of turn pairs to keep
        
        Returns:
            Trimmed history
        """
        if not self.should_trim_history(history, max_turns):
            return history
        
        # Find indices of user messages
        user_indices = [
            i for i, msg in enumerate(history)
            if msg["role"] == "user"
        ]
        
        if len(user_indices) <= max_turns:
            return history
        
        # Calculate how many turns to remove
        turns_to_remove = len(user_indices) - max_turns
        
        # Find the index after the last turn to remove
        # Each turn is: user message + assistant response
        if turns_to_remove > 0 and turns_to_remove < len(user_indices):
            cutoff_index = user_indices[turns_to_remove]
            return history[cutoff_index:]
        
        return history
    
    def create_session_summary(
        self,
        history: List[Dict[str, str]]
    ) -> str:
        """
        Create a compact summary of session state.
        
        Extracts:
        - Current product being discussed
        - User-provided tracking status (if any)
        - Whether discussing change-of-mind or faulty return
        
        Never claims to have verified order/tracking data.
        
        Args:
            history: Conversation history
        
        Returns:
            Compact summary string
        """
        summary_parts = []
        
        # Look for product mentions in recent history
        products = [
            "headphones", "laptop stand", "keyboard", 
            "webcam", "power bank"
        ]
        
        recent_product = None
        for msg in reversed(history[-6:]):  # Check last 3 turns
            content_lower = msg["content"].lower()
            for product in products:
                if product in content_lower:
                    recent_product = product
                    break
            if recent_product:
                break
        
        if recent_product:
            summary_parts.append(f"discussing {recent_product}")
        
        # Look for tracking status mentions
        tracking_statuses = [
            "in transit", "dispatched", "out for delivery",
            "delivered", "processing", "attempted delivery"
        ]
        
        for msg in reversed(history[-4:]):  # Check last 2 turns
            if msg["role"] == "user":
                content_lower = msg["content"].lower()
                for status in tracking_statuses:
                    if status in content_lower:
                        summary_parts.append(
                            f"user reported tracking status: '{status}'"
                        )
                        break
        
        # Look for return-related context
        # Check for faulty/damaged keywords first
        has_faulty = any(
            "faulty" in msg["content"].lower() or 
            "damaged" in msg["content"].lower() or
            "broken" in msg["content"].lower() or
            "defective" in msg["content"].lower()
            for msg in history[-4:]
        )
        
        has_return = any("return" in msg["content"].lower() 
                        for msg in history[-4:])
        
        if has_faulty:
            summary_parts.append("discussing faulty item return")
        elif has_return:
            summary_parts.append("discussing change-of-mind return")
        
        return "; ".join(summary_parts) if summary_parts else ""
