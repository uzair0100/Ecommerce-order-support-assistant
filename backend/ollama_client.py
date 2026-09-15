"""
Ollama API client for GadgetMart assistant.
Uses /api/chat endpoint with structured role messages.
Supports both streaming and non-streaming modes.
"""

import json
import httpx
from typing import List, Dict, Optional, AsyncIterator
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
    
    async def chat_stream(
        self,
        messages: List[Dict[str, str]]
    ) -> AsyncIterator[Dict[str, any]]:
        """
        Send a streaming chat request to Ollama.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
        
        Yields:
            Dict chunks from Ollama with 'content', 'done', etc.
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": self.temperature,
                "num_ctx": self.num_ctx
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(10.0, read=180.0)) as client:
                async with client.stream(
                    "POST",
                    self.base_url,
                    json=payload
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if not line.strip():
                            continue
                        
                        try:
                            chunk = json.loads(line)
                            yield chunk
                        except json.JSONDecodeError:
                            continue
        
        except httpx.TimeoutException:
            raise Exception("Ollama request timed out")
        except httpx.RequestError as e:
            raise Exception(f"Ollama request failed: {str(e)}")
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False
    ) -> Optional[str]:
        """
        Send a non-streaming chat request to Ollama (Phase III compatibility).
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            stream: Must be False for this method
        
        Returns:
            Generated response text, or None if error
        """
        if stream:
            raise NotImplementedError("Use chat_stream() for streaming")
        
        import requests
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_ctx": self.num_ctx
            }
        }
        
        try:
            response = requests.post(
                self.base_url,
                json=payload,
                timeout=(10, 180)
            )
            response.raise_for_status()
            
            data = response.json()
            message_content = data.get("message", {}).get("content", "")
            
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
            import requests
            tags_url = self.base_url.replace("/api/chat", "/api/tags")
            response = requests.get(tags_url, timeout=5)
            return response.status_code == 200
        except:
            return False
