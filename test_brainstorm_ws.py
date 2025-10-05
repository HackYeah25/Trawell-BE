#!/usr/bin/env python3
"""
Test WebSocket connection for brainstorm endpoint
"""
import asyncio
import websockets
import json

async def test_brainstorm_websocket():
    # First, create a session
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:8000/api/brainstorm/start")
        session_data = response.json()
        print(f"✅ Session created: {session_data['session_id']}")
        print(f"📝 First message: {session_data['first_message']}")
        print()

        session_id = session_data['session_id']

    # Connect to WebSocket
    ws_url = f"ws://localhost:8000/api/brainstorm/ws/{session_id}"
    print(f"🔌 Connecting to {ws_url}")

    async with websockets.connect(ws_url) as websocket:
        print("✅ WebSocket connected!")
        print()

        # Send first message
        test_message = "Chciałbym pojechać gdzieś ciepło, z pięknymi plażami"
        print(f"📤 Sending: {test_message}")
        await websocket.send(json.dumps({
            "type": "message",
            "content": test_message
        }))

        # Receive response
        print("📥 Receiving response...")
        full_response = ""
        token_count = 0

        while True:
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                data = json.loads(message)

                if data.get("type") == "thinking":
                    print("🤔 AI is thinking...")

                elif data.get("type") == "token":
                    token = data.get("token", "")
                    full_response += token
                    token_count += 1
                    print(token, end="", flush=True)

                elif data.get("type") == "message":
                    print("\n")
                    print(f"✅ Complete response received ({token_count} tokens)")
                    print(f"📊 Response length: {len(full_response)} chars")
                    break

            except asyncio.TimeoutError:
                print("\n⏰ Timeout waiting for response")
                break

        print()
        print("="*60)
        print("Full conversation:")
        print(f"User: {test_message}")
        print(f"AI: {full_response}")

if __name__ == "__main__":
    asyncio.run(test_brainstorm_websocket())
