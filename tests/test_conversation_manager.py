"""
Tests for conversation manager.
Focus on: trimming, topic switches, reset, session isolation.
"""

import pytest
from backend.conversation_manager import ConversationManager, ConversationSession
from backend.prompt_builder import PromptBuilder


class MockOllamaClient:
    """Mock Ollama client for testing without live model."""
    
    def __init__(self):
        self.call_count = 0
        self.last_messages = None
    
    def chat(self, messages, stream=False):
        self.call_count += 1
        self.last_messages = messages
        # Return a simple mock response
        return f"Mock response {self.call_count}"
    
    def health_check(self):
        return True


@pytest.fixture
def mock_client():
    return MockOllamaClient()


@pytest.fixture
def manager(mock_client):
    return ConversationManager(ollama_client=mock_client, max_history_turns=3)


def test_create_session(manager):
    """Test session creation."""
    session_id = manager.create_session()
    assert session_id is not None
    assert manager.session_exists(session_id)


def test_session_isolation(manager):
    """Test that sessions have isolated state."""
    session1 = manager.create_session()
    session2 = manager.create_session()
    
    # Send messages to each session
    response1 = manager.get_response(session1, "Hello from session 1")
    response2 = manager.get_response(session2, "Hello from session 2")
    
    # Get histories
    with manager.global_lock:
        history1 = manager.sessions[session1].history
        history2 = manager.sessions[session2].history
    
    # Verify isolation
    assert len(history1) == 2  # user + assistant
    assert len(history2) == 2
    assert history1[0]["content"] == "Hello from session 1"
    assert history2[0]["content"] == "Hello from session 2"


def test_reset_session(manager):
    """Test session reset clears history."""
    session_id = manager.create_session()
    
    # Add some messages
    manager.get_response(session_id, "First message")
    manager.get_response(session_id, "Second message")
    
    with manager.global_lock:
        assert len(manager.sessions[session_id].history) == 4  # 2 turns
    
    # Reset
    result = manager.reset_session(session_id)
    assert result is True
    
    with manager.global_lock:
        assert len(manager.sessions[session_id].history) == 0


def test_history_trimming(manager):
    """Test that old turns are trimmed when exceeding max_history_turns."""
    session_id = manager.create_session()
    
    # Max is 3 turns; send 5 messages
    for i in range(5):
        manager.get_response(session_id, f"Message {i+1}")
    
    with manager.global_lock:
        history = manager.sessions[session_id].history
        user_messages = [m for m in history if m["role"] == "user"]
    
    # Should have at most 3 user messages (most recent)
    assert len(user_messages) <= 3
    
    # Verify oldest messages were removed
    assert "Message 1" not in [m["content"] for m in user_messages]
    assert "Message 2" not in [m["content"] for m in user_messages]
    
    # Verify newest messages remain
    assert "Message 5" in [m["content"] for m in user_messages]


def test_topic_switch_context(manager, mock_client):
    """Test that context updates when topic switches."""
    session_id = manager.create_session()
    
    # Discuss headphones
    manager.get_response(session_id, "Tell me about the headphones")
    
    # Switch to keyboard
    manager.get_response(session_id, "What about the keyboard?")
    
    # Both should be in history
    with manager.global_lock:
        history = manager.sessions[session_id].history
        user_messages = [m["content"] for m in history if m["role"] == "user"]
    
    assert "headphones" in user_messages[0]
    assert "keyboard" in user_messages[1]


def test_nonexistent_session(manager):
    """Test handling of requests to nonexistent session."""
    response = manager.get_response("fake-session-id", "Hello")
    assert response is None


def test_delete_session(manager):
    """Test session deletion."""
    session_id = manager.create_session()
    assert manager.session_exists(session_id)
    
    result = manager.delete_session(session_id)
    assert result is True
    assert not manager.session_exists(session_id)


def test_get_session_info(manager):
    """Test retrieving session metadata."""
    session_id = manager.create_session()
    manager.get_response(session_id, "Test message")
    
    info = manager.get_session_info(session_id)
    assert info is not None
    assert info["session_id"] == session_id
    assert info["turn_count"] == 1
    assert "created_at" in info
    assert "last_activity" in info


def test_concurrent_turn_guard(manager):
    """Test that overlapping requests are blocked per session."""
    session_id = manager.create_session()
    
    # Simulate in_progress flag
    with manager.global_lock:
        session = manager.sessions[session_id]
    
    # Acquire lock manually to simulate in-progress request
    session.lock.acquire()
    
    try:
        # Try to send another message (should be blocked)
        response = manager.get_response(session_id, "Concurrent message")
        assert "[ERROR: Another request is in progress" in response
    finally:
        session.lock.release()
