"""
Simple WebSocket test client for manual testing.
Tests streaming chat functionality.
"""

import asyncio
import json
import websockets


async def test_chat():
    """Test basic chat with streaming."""
    uri = "ws://localhost:8000/ws/chat"
    
    print("=" * 70)
    print("GadgetMart WebSocket Test Client")
    print("=" * 70)
    print(f"\nConnecting to {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected!\n")
            
            # Test 1: Simple product question
            print("Test 1: Product question (streaming)")
            print("-" * 70)
            
            message = {
                "type": "message",
                "session_id": None,  # Auto-create session
                "content": "What is the price of the headphones?"
            }
            
            print(f"Sending: {json.dumps(message, indent=2)}\n")
            await websocket.send(json.dumps(message))
            
            session_id = None
            turn_id = None
            full_response = ""
            
            print("Response stream:")
            while True:
                response = await websocket.recv()
                data = json.loads(response)
                
                event_type = data.get("type")
                
                if event_type == "start":
                    session_id = data.get("session_id")
                    turn_id = data.get("turn_id")
                    print(f"[START] session_id: {session_id[:8]}..., turn_id: {turn_id[:8]}...")
                    print("Assistant: ", end="", flush=True)
                
                elif event_type == "chunk":
                    content = data.get("content", "")
                    full_response += content
                    print(content, end="", flush=True)
                
                elif event_type == "done":
                    tokens = data.get("total_tokens")
                    print(f"\n[DONE] Tokens: {tokens}")
                    break
                
                elif event_type == "error":
                    error = data.get("error")
                    code = data.get("code")
                    print(f"\n[ERROR] {code}: {error}")
                    return
            
            print("\n")
            
            # Test 2: Follow-up question (same session)
            print("Test 2: Follow-up question (same session)")
            print("-" * 70)
            
            message2 = {
                "type": "message",
                "session_id": session_id,
                "content": "Is it returnable?"
            }
            
            print(f"Sending: {json.dumps(message2, indent=2)}\n")
            await websocket.send(json.dumps(message2))
            
            print("Response stream:")
            full_response2 = ""
            
            while True:
                response = await websocket.recv()
                data = json.loads(response)
                
                event_type = data.get("type")
                
                if event_type == "start":
                    print(f"[START] turn_id: {data.get('turn_id')[:8]}...")
                    print("Assistant: ", end="", flush=True)
                
                elif event_type == "chunk":
                    content = data.get("content", "")
                    full_response2 += content
                    print(content, end="", flush=True)
                
                elif event_type == "done":
                    tokens = data.get("total_tokens")
                    print(f"\n[DONE] Tokens: {tokens}")
                    break
                
                elif event_type == "error":
                    error = data.get("error")
                    code = data.get("code")
                    print(f"\n[ERROR] {code}: {error}")
                    return
            
            print("\n")
            
            # Test 3: Reset session
            print("Test 3: Reset session")
            print("-" * 70)
            
            reset_msg = {
                "type": "reset",
                "session_id": session_id
            }
            
            print(f"Sending: {json.dumps(reset_msg, indent=2)}\n")
            await websocket.send(json.dumps(reset_msg))
            
            response = await websocket.recv()
            data = json.loads(response)
            
            if data.get("type") == "reset":
                print(f"✅ Session reset acknowledged: {data.get('session_id')[:8]}...\n")
            else:
                print(f"Unexpected response: {data}\n")
            
            # Test 4: Question after reset (should not remember headphones)
            print("Test 4: Question after reset (context should be cleared)")
            print("-" * 70)
            
            message3 = {
                "type": "message",
                "session_id": session_id,
                "content": "What product was I asking about?"
            }
            
            print(f"Sending: {json.dumps(message3, indent=2)}\n")
            await websocket.send(json.dumps(message3))
            
            print("Response stream:")
            
            while True:
                response = await websocket.recv()
                data = json.loads(response)
                
                event_type = data.get("type")
                
                if event_type == "start":
                    print(f"[START] turn_id: {data.get('turn_id')[:8]}...")
                    print("Assistant: ", end="", flush=True)
                
                elif event_type == "chunk":
                    content = data.get("content", "")
                    print(content, end="", flush=True)
                
                elif event_type == "done":
                    tokens = data.get("total_tokens")
                    print(f"\n[DONE] Tokens: {tokens}")
                    break
                
                elif event_type == "error":
                    error = data.get("error")
                    code = data.get("code")
                    print(f"\n[ERROR] {code}: {error}")
                    break
            
            print("\n")
            print("=" * 70)
            print("✅ All tests completed!")
            print("=" * 70)
    
    except ConnectionRefusedError:
        print("❌ Connection refused. Is the server running?")
        print("   Start with: python -m backend.main")
    
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")


async def test_validation():
    """Test validation and error handling."""
    uri = "ws://localhost:8000/ws/chat"
    
    print("\n" + "=" * 70)
    print("Validation Tests")
    print("=" * 70)
    
    try:
        async with websockets.connect(uri) as websocket:
            # Test: Empty content
            print("\nTest: Empty content")
            print("-" * 70)
            
            message = {
                "type": "message",
                "session_id": None,
                "content": ""
            }
            
            await websocket.send(json.dumps(message))
            response = await websocket.recv()
            data = json.loads(response)
            
            if data.get("type") == "error":
                print(f"✅ Error caught: {data.get('code')} - {data.get('error')}")
            else:
                print(f"❌ Expected error, got: {data}")
            
            # Test: Invalid JSON
            print("\nTest: Invalid JSON")
            print("-" * 70)
            
            await websocket.send("not valid json")
            response = await websocket.recv()
            data = json.loads(response)
            
            if data.get("code") == "INVALID_JSON":
                print(f"✅ Error caught: {data.get('code')} - {data.get('error')}")
            else:
                print(f"❌ Expected INVALID_JSON, got: {data}")
            
            # Test: Content too long
            print("\nTest: Content too long (>2000 chars)")
            print("-" * 70)
            
            message = {
                "type": "message",
                "session_id": None,
                "content": "a" * 2001
            }
            
            await websocket.send(json.dumps(message))
            response = await websocket.recv()
            data = json.loads(response)
            
            if data.get("code") == "CONTENT_TOO_LONG":
                print(f"✅ Error caught: {data.get('code')} - {data.get('error')}")
            else:
                print(f"❌ Expected CONTENT_TOO_LONG, got: {data}")
            
            print("\n" + "=" * 70)
            print("✅ Validation tests completed!")
            print("=" * 70)
    
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")


async def main():
    """Run all tests."""
    await test_chat()
    await test_validation()


if __name__ == "__main__":
    print("\nMake sure the server is running:")
    print("  python -m backend.main")
    print("\nPress Ctrl+C to cancel, or Enter to continue...")
    input()
    
    asyncio.run(main())
