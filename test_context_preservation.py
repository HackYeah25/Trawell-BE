#!/usr/bin/env python3
"""
Test conversation context preservation in brainstorm
"""
import asyncio
import websockets
import json
import httpx

async def test_context():
    # Create session
    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:8000/api/brainstorm/start")
        session_data = response.json()
        session_id = session_data['session_id']
        print(f"✅ Session: {session_id}\n")

    ws_url = f"ws://localhost:8000/api/brainstorm/ws/{session_id}"

    async with websockets.connect(ws_url) as ws:
        # Message 1
        print("📤 Message 1: Marzę o Tajlandii")
        await ws.send(json.dumps({"type": "message", "content": "Marzę o Tajlandii"}))

        response1 = ""
        while True:
            msg = json.loads(await ws.recv())
            if msg.get("type") == "token":
                response1 += msg["token"]
                print(msg["token"], end="", flush=True)
            elif msg.get("type") == "message":
                break

        print("\n" + "="*60)

        # Message 2 - test if AI remembers Tajlandia
        print("\n📤 Message 2: Jakie są najlepsze plaże tam?")
        await ws.send(json.dumps({"type": "message", "content": "Jakie są najlepsze plaże tam?"}))

        response2 = ""
        while True:
            msg = json.loads(await ws.recv())
            if msg.get("type") == "token":
                response2 += msg["token"]
                print(msg["token"], end="", flush=True)
            elif msg.get("type") == "message":
                break

        print("\n" + "="*60)

        # Check if response mentions Thailand/Tajlandia
        if "Tajland" in response2 or "Thailan" in response2 or "Koh" in response2:
            print("\n✅ CONTEXT PRESERVED! AI remembered we're talking about Thailand")
        else:
            print("\n❌ CONTEXT LOST! AI didn't remember Thailand")
            print(f"Response 2: {response2[:200]}")

if __name__ == "__main__":
    asyncio.run(test_context())
