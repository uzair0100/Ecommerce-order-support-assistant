"""
Tests for prompt builder.
"""

import pytest
from backend.prompt_builder import PromptBuilder


@pytest.fixture
def builder():
    return PromptBuilder()


def test_load_system_prompt(builder):
    """Test that system prompt loads from file."""
    assert builder.system_prompt is not None
    assert len(builder.system_prompt) > 0
    assert "GadgetMart" in builder.system_prompt


def test_build_messages_basic(builder):
    """Test building messages with empty history."""
    messages = builder.build_messages(
        history=[],
        user_message="Hello"
    )
    
    assert len(messages) == 2  # system + user
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == "Hello"


def test_build_messages_with_history(builder):
    """Test building messages with conversation history."""
    history = [
        {"role": "user", "content": "First message"},
        {"role": "assistant", "content": "First response"},
        {"role": "user", "content": "Second message"},
        {"role": "assistant", "content": "Second response"}
    ]
    
    messages = builder.build_messages(
        history=history,
        user_message="Third message"
    )
    
    # system + 4 history + 1 current = 6
    assert len(messages) == 6
    assert messages[0]["role"] == "system"
    assert messages[-1]["role"] == "user"
    assert messages[-1]["content"] == "Third message"


def test_build_messages_with_summary(builder):
    """Test including session summary in system message."""
    messages = builder.build_messages(
        history=[],
        user_message="Hello",
        session_summary="discussing headphones"
    )
    
    system_msg = messages[0]
    assert "Session context: discussing headphones" in system_msg["content"]


def test_should_trim_history(builder):
    """Test trim detection."""
    # 3 turns (6 messages)
    history = [
        {"role": "user", "content": "1"},
        {"role": "assistant", "content": "R1"},
        {"role": "user", "content": "2"},
        {"role": "assistant", "content": "R2"},
        {"role": "user", "content": "3"},
        {"role": "assistant", "content": "R3"}
    ]
    
    assert not builder.should_trim_history(history, max_turns=3)
    assert not builder.should_trim_history(history, max_turns=5)
    assert builder.should_trim_history(history, max_turns=2)


def test_trim_history(builder):
    """Test history trimming removes oldest turns."""
    history = [
        {"role": "user", "content": "Turn 1"},
        {"role": "assistant", "content": "Response 1"},
        {"role": "user", "content": "Turn 2"},
        {"role": "assistant", "content": "Response 2"},
        {"role": "user", "content": "Turn 3"},
        {"role": "assistant", "content": "Response 3"},
        {"role": "user", "content": "Turn 4"},
        {"role": "assistant", "content": "Response 4"}
    ]
    
    trimmed = builder.trim_history(history, max_turns=2)
    
    # Should keep last 2 turns (4 messages)
    assert len(trimmed) == 4
    
    # Verify oldest turns removed
    contents = [m["content"] for m in trimmed]
    assert "Turn 1" not in contents
    assert "Turn 2" not in contents
    
    # Verify newest turns kept
    assert "Turn 3" in contents
    assert "Turn 4" in contents


def test_create_session_summary_product(builder):
    """Test session summary extracts product context."""
    history = [
        {"role": "user", "content": "Tell me about the headphones"},
        {"role": "assistant", "content": "The headphones cost £79.99"}
    ]
    
    summary = builder.create_session_summary(history)
    assert "headphones" in summary


def test_create_session_summary_tracking(builder):
    """Test session summary extracts tracking status."""
    history = [
        {"role": "user", "content": "My tracking says In Transit"},
        {"role": "assistant", "content": "That means it's on the way"}
    ]
    
    summary = builder.create_session_summary(history)
    assert "in transit" in summary.lower()


def test_create_session_summary_return_type(builder):
    """Test session summary distinguishes return types."""
    history_faulty = [
        {"role": "user", "content": "My webcam arrived damaged"},
        {"role": "assistant", "content": "That's covered under faulty items"}
    ]
    
    summary_faulty = builder.create_session_summary(history_faulty)
    assert "faulty" in summary_faulty.lower()
    
    history_change = [
        {"role": "user", "content": "I want to return the keyboard, I changed my mind"},
        {"role": "assistant", "content": "That's a change-of-mind return"}
    ]
    
    summary_change = builder.create_session_summary(history_change)
    assert "change-of-mind" in summary_change.lower()


def test_estimate_token_count(builder):
    """Test token estimation."""
    # Rough heuristic: ~4 chars per token
    text = "Hello world"  # 11 chars
    tokens = builder.estimate_token_count(text)
    assert tokens == 2  # 11 // 4 = 2
    
    text = "This is a longer sentence with more words."  # 43 chars
    tokens = builder.estimate_token_count(text)
    assert tokens == 10  # 43 // 4 = 10
