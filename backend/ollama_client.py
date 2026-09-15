"""
Ollama API client for GadgetMart assistant.
Uses /api/chat endpoint with structured role messages.
"""

import requests
from typing import List, Dict, Optional
from backend.config import (
    OLLAMA_CHAT_ENDPOINT,
    MODEL_NAME,
    TEMPERATURE,
    NUM_CTX
)


class OllamaClient:
    """Client for interacting with local Ollama API."""
    
    def __init__(
        self,
        base_url: str = OLLAMA_CHAT_ENDPOINT,
        model: str = MODEL_NAME,
        temperature: float = TEMPERATURE,
        num_ctx: int = NUM_CTX
    ):
        self.base_url = base_url
        self.model = model
        self.temperature = temperature
        self.num_ctx = num_ctx
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False
    ) -> Optional[str]:
        """
        Send a chat request to Ollama.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
                     Roles: 'system', 'user', 'assistant'
            stream: Whether to stream the response (False for Phase III)
        
        Returns:
            Generated response text, or None if error
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": self.temperature,
                "num_ctx": self.num_ctx
            }
        }
        
        try:
            response = requests.post(
                self.base_url,
                json=payload,
                timeout=(10, 180)  # 10s connect, 180s read (3 min for slow generations)
            )
            response.raise_for_status()
            
            if stream:
                # Phase IV will implement streaming
                raise NotImplementedError("Streaming not yet implemented")
            else:
                # Non-streaming response
                data = response.json()
                message_content = data.get("message", {}).get("content", "")
                
                # Fallback: check for 'response' field (some Ollama versions)
                if not message_content:
                    message_content = data.get("response", "")
                
                return message_content
        
        except requests.exceptions.Timeout:
            print(f"[OllamaClient] Timeout calling {self.base_url}")
            return None
        
        except requests.exceptions.RequestException as e:
            print(f"[OllamaClient] Request error: {type(e).__name__}: {e}")
            return None
        
        except Exception as e:
            print(f"[OllamaClient] Unexpected error: {type(e).__name__}: {e}")
            return None
    
    def health_check(self) -> bool:
        """
        Check if Ollama is available.
        
        Returns:
            True if Ollama responds, False otherwise
        """
        try:
            # Use /api/tags to check if Ollama is running
            tags_url = self.base_url.replace("/api/chat", "/api/tags")
            response = requests.get(tags_url, timeout=5)
            return response.status_code == 200
        except:
            return False
