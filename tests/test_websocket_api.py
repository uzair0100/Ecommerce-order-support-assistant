"""
Tests for WebSocket API protocol and behavior.
"""

import pytest
import json
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test /health endpoint returns proper structure."""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "server_healthy" in data
    assert "ollama_available" in data
    assert "model" in data
    assert "active_sessions" in data
    
    # Server should be healthy even if Ollama is down
    assert data["server_healthy"] is True


def test_websocket_connection():
    """Test WebSocket connection can be established."""
    with client.websocket_connect("/ws/chat") as websocket:
        # Connection successful if no exception
        assert websocket is not None


def test_websocket_invalid_json():
    """Test WebSocket rejects invalid JSON."""
    with client.websocket_connect("/ws/chat") as websocket:
        # Send invalid JSON
        websocket.send_text("not valid json{")
        
        # Should receive error
        response = websocket.receive_json()
        assert response["type"] == "error"
        assert response["code"] == "INVALID_JSON"


def test_websocket_missing_type():
    """Test WebSocket rejects message without 'type' field."""
    with client.websocket_connect("/ws/chat") as websocket:
        message = {"content": "hello"}
        websocket.send_json(message)
        
        response = websocket.receive_json()
        assert response["type"] == "error"
        assert response["code"] == "MISSING_FIELD"


def test_websocket_unknown_type():
    """Test WebSocket rejects unknown message type."""
    with client.websocket_connect("/ws/chat") as websocket:
        message = {"type": "unknown_type"}
        websocket.send_json(message)
        
        response = websocket.receive_json()
        assert response["type"] == "error"
        assert response["code"] == "INVALID_MESSAGE_TYPE"


def test_websocket_empty_content():
    """Test WebSocket rejects empty content."""
    with client.websocket_connect("/ws/chat") as websocket:
        message = {
            "type": "message",
            "session_id": None,
            "content": ""
        }
        websocket.send_json(message)
        
        response = websocket.receive_json()
        assert response["type"] == "error"
        assert response["code"] == "EMPTY_CONTENT"


def test_websocket_whitespace_only_content():
    """Test WebSocket rejects whitespace-only content."""
    with client.websocket_connect("/ws/chat") as websocket:
        message = {
            "type": "message",
            "session_id": None,
            "content": "   \t\n  "
        }
        websocket.send_json(message)
        
        response = websocket.receive_json()
        assert response["type"] == "error"
        assert response["code"] == "EMPTY_CONTENT"


def test_websocket_content_too_long():
    """Test WebSocket rejects content over 2000 characters."""
    with client.websocket_connect("/ws/chat") as websocket:
        message = {
            "type": "message",
            "session_id": None,
            "content": "a" * 2001
        }
        websocket.send_json(message)
        
        response = websocket.receive_json()
        assert response["type"] == "error"
        assert response["code"] == "CONTENT_TOO_LONG"


def test_websocket_invalid_session_id_format():
    """Test WebSocket rejects invalid UUID format."""
    with client.websocket_connect("/ws/chat") as websocket:
        message = {
            "type": "message",
            "session_id": "not-a-uuid",
            "content": "hello"
        }
        websocket.send_json(message)
        
        response = websocket.receive_json()
        assert response["type"] == "error"
        assert response["code"] == "INVALID_SESSION"


def test_websocket_reset_missing_session_id():
    """Test reset requires session_id."""
    with client.websocket_connect("/ws/chat") as websocket:
        message = {"type": "reset"}
        websocket.send_json(message)
        
        response = websocket.receive_json()
        assert response["type"] == "error"
        assert response["code"] == "MISSING_FIELD"


def test_websocket_reset_nonexistent_session():
    """Test reset with nonexistent session."""
    with client.websocket_connect("/ws/chat") as websocket:
        import uuid
        fake_session_id = str(uuid.uuid4())
        
        message = {
            "type": "reset",
            "session_id": fake_session_id
        }
        websocket.send_json(message)
        
        response = websocket.receive_json()
        assert response["type"] == "error"
        assert response["code"] == "INVALID_SESSION"


@pytest.mark.skipif(
    True,  # Skip by default, use --run-live to enable
    reason="Requires live Ollama (use --run-live to enable)"
)
def test_websocket_chat_flow_live():
    """
    Test complete chat flow with live Ollama.
    
    This test requires Ollama to be running and is skipped by default.
    Run with: pytest tests/test_websocket_api.py --run-live -v
    """
    with client.websocket_connect("/ws/chat") as websocket:
        # Send message
        message = {
            "type": "message",
            "session_id": None,
            "content": "What is the price of the headphones?"
        }
        websocket.send_json(message)
        
        # Should receive start
        start_event = websocket.receive_json()
        assert start_event["type"] == "start"
        assert "session_id" in start_event
        assert "turn_id" in start_event
        
        session_id = start_event["session_id"]
        turn_id = start_event["turn_id"]
        
        # Should receive chunks
        received_chunks = False
        full_response = ""
        
        while True:
            event = websocket.receive_json()
            
            if event["type"] == "chunk":
                received_chunks = True
                full_response += event.get("content", "")
            
            elif event["type"] == "done":
                assert event["session_id"] == session_id
                assert event["turn_id"] == turn_id
                assert "total_tokens" in event
                break
            
            elif event["type"] == "error":
                pytest.fail(f"Received error: {event}")
        
        assert received_chunks, "Should have received at least one chunk"
        assert len(full_response) > 0, "Response should not be empty"
        assert "79.99" in full_response or "£79.99" in full_response, "Should mention price"


def pytest_configure(config):
    """Configure pytest with custom options."""
    config.addinivalue_line(
        "markers", "live: marks tests as requiring live Ollama (deselect with '-m \"not live\"')"
    )
