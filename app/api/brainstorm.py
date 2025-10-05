"""
Brainstorm API v2 - Database-persisted brainstorm sessions
Creates conversations in DB with LangChain memory
"""
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from typing import Dict, Optional, List, Any
import uuid
import asyncio
import json
import re
from datetime import datetime

from app.models.user import UserProfile, UserPreferences, UserConstraints, TokenData
from app.models.destination import Rating, DestinationInfo, DestinationRecommendation

from app.services.supabase_service import get_supabase
from app.agents.brainstorm_agent import BrainstormAgent
from app.api.deps import get_current_user_optional

router = APIRouter(prefix="/api/brainstorm", tags=["brainstorm"])

# In-memory storage for active agents (rehydrated from DB on reconnect)
active_agents: Dict[str, BrainstormAgent] = {}

# Test user ID for development
TEST_USER_ID = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"


def extract_location_proposals(text: str) -> tuple[str, Optional[List[Dict]]]:
    """
    Extract location proposals from <locations> XML tags
    
    Args:
        text: Response text potentially containing <locations> tags
        
    Returns:
        Tuple of (cleaned_text, locations_list)
        - cleaned_text: Text with <locations> tags removed
        - locations_list: Parsed JSON array of locations, or None if not found
    """
    print(f"\n{'='*80}")
    print(f"🔍 LOCATION EXTRACTION - Analyzing response (length: {len(text)} chars)")
    print(f"{'='*80}")
    
    # Show first 200 chars of response
    preview = text[:200].replace('\n', ' ')
    print(f"📝 Response preview: {preview}...")
    
    # Find <locations> tags
    pattern = r'<locations>\s*(\[[\s\S]*?\])\s*</locations>'
    match = re.search(pattern, text)
    
    if not match:
        print(f"❌ NO LOCATION TAGS FOUND in response")
        print(f"   Searched for pattern: <locations>[...]</locations>")
        
        # Check if "location" appears anywhere to help debug
        if 'location' in text.lower():
            print(f"   ℹ️  Found 'location' keyword in text, but not in proper format")
            # Show context around "location" keyword
            loc_index = text.lower().find('location')
            context_start = max(0, loc_index - 50)
            context_end = min(len(text), loc_index + 100)
            print(f"   Context: ...{text[context_start:context_end]}...")
        else:
            print(f"   ℹ️  'location' keyword not found in response at all")
        
        print(f"{'='*80}\n")
        return text, None
    
    print(f"✅ FOUND <locations> TAGS!")
    
    # Extract JSON
    locations_json = match.group(1)
    print(f"📦 Extracted JSON (length: {len(locations_json)} chars):")
    print(f"{locations_json[:300]}...")  # Show first 300 chars
    
    try:
        # Parse JSON
        locations = json.loads(locations_json)
        
        print(f"✅ Successfully parsed JSON - found {len(locations)} location(s)")
        
        # Log each location
        for idx, loc in enumerate(locations, 1):
            print(f"   {idx}. {loc.get('name', 'N/A')}, {loc.get('country', 'N/A')}")
            print(f"      ID: {loc.get('id', 'N/A')}")
            print(f"      Teaser: {loc.get('teaser', 'N/A')[:60]}...")
        
        # Remove the <locations> block from text
        cleaned_text = re.sub(pattern, '', text).strip()
        
        print(f"🧹 Cleaned text (length after removal: {len(cleaned_text)} chars)")
        print(f"{'='*80}\n")
        
        return cleaned_text, locations
        
    except json.JSONDecodeError as e:
        print(f"❌ FAILED TO PARSE LOCATIONS JSON!")
        print(f"   Error: {e}")
        print(f"   JSON string: {locations_json[:200]}...")
        print(f"{'='*80}\n")
        # Return original text if parsing fails
        return text, None


@router.get("/sessions")
async def list_brainstorm_sessions(
    current_user: Optional[TokenData] = Depends(get_current_user_optional)
):
    """
    List all brainstorm sessions for current user

    Returns:
        sessions: List of conversation sessions with metadata
    """
    user_id = current_user.user_id if current_user else TEST_USER_ID
    supabase = get_supabase()

    try:
        if not supabase.client:
            raise HTTPException(status_code=500, detail="Database not available")

        # Query conversations table for brainstorm module
        result = supabase.client.table("conversations").select(
            "conversation_id, context_summary, created_at, updated_at, messages, mode"
        ).eq("user_id", user_id).eq("module", "brainstorm").order(
            "updated_at", desc=True
        ).execute()

        sessions = []
        for conv in result.data:
            # Get last message preview
            messages = conv.get("messages", [])
            last_message = messages[-1] if messages else None

            sessions.append({
                "id": conv["conversation_id"],
                "title": conv.get("context_summary") or "New Brainstorm",
                "lastMessage": last_message.get("content", "")[:100] if last_message else "",
                "createdAt": conv["created_at"],
                "updatedAt": conv["updated_at"],
                "messageCount": len(messages),
                "isShared": conv.get("mode") == "group"
            })

        return {"sessions": sessions}

    except Exception as e:
        print(f"ERROR listing brainstorm sessions: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions")
async def create_brainstorm_session(
    title: Optional[str] = None,
    current_user: Optional[TokenData] = Depends(get_current_user_optional)
):
    """
    Create new brainstorm session
    Persists to database and returns session details

    Args:
        title: Optional title for the session

    Returns:
        session_id, first_message, websocket_url
    """
    user_id = current_user.user_id if current_user else TEST_USER_ID
    supabase = get_supabase()

    try:
        # Get user profile
        user_profile = await supabase.get_user_profile(user_id)

        if not user_profile:
            # Use test profile for development
            print(f"WARNING: No profile for user {user_id}, using test profile")
            user_profile = UserProfile(
                user_id=user_id,
                preferences=UserPreferences(
                    traveler_type="explorer",
                    activity_level="high",
                    environment="mixed",
                    accommodation_style="boutique",
                    budget_sensitivity="medium",
                    culture_interest="high",
                    food_importance="high"
                ),
                constraints=UserConstraints(
                    dietary_restrictions=[],
                    climate_preferences=["mild_temperate", "hot_tropical"],
                    language_preferences=[]
                ),
                wishlist_regions=["Southeast Asia", "Iceland"],
                past_destinations=["Paris", "Barcelona"]
            )

        # Generate session ID
        session_id = f"brainstorm_{uuid.uuid4().hex[:12]}"

        # Create agent with user profile
        agent = BrainstormAgent(user_profile)
        active_agents[session_id] = agent

        # Generate personalized first message
        first_message = agent.generate_first_message()

        # Create conversation in database
        if supabase.client:
            conversation_data = {
                "conversation_id": session_id,
                "user_id": user_id,
                "module": "brainstorm",
                "mode": "solo",
                "messages": [{
                    "role": "assistant",
                    "content": first_message,
                    "timestamp": datetime.utcnow().isoformat()
                }],
                "context_summary": title or "New Travel Brainstorm",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }

            supabase.client.table("conversations").insert(conversation_data).execute()
            print(f"✅ Created conversation {session_id} in database")

        return {
            "session_id": session_id,
            "title": title or "New Travel Brainstorm",
            "first_message": first_message,
            "websocket_url": f"/api/brainstorm/ws/{session_id}"
        }

    except Exception as e:
        print(f"ERROR creating brainstorm session: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}")
async def get_brainstorm_session(
    session_id: str,
    current_user: Optional[TokenData] = Depends(get_current_user_optional)
):
    """
    Get brainstorm session details and full conversation history
    """
    user_id = current_user.user_id if current_user else TEST_USER_ID
    supabase = get_supabase()

    try:
        if not supabase.client:
            raise HTTPException(status_code=500, detail="Database not available")

        # Get conversation from database
        result = supabase.client.table("conversations").select("*").eq(
            "conversation_id", session_id
        ).eq("user_id", user_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Session not found")

        conversation = result.data[0]

        return {
            "session_id": conversation["conversation_id"],
            "title": conversation.get("context_summary", "Brainstorm Session"),
            "messages": conversation.get("messages", []),
            "createdAt": conversation["created_at"],
            "updatedAt": conversation["updated_at"],
            "mode": conversation.get("mode", "solo")
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR getting brainstorm session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws/{session_id}")
async def brainstorm_websocket(
    websocket: WebSocket,
    session_id: str
):
    """
    WebSocket endpoint for real-time brainstorm conversation
    Streams responses and persists to database
    """
    await websocket.accept()
    supabase = get_supabase()

    try:
        # Load or rehydrate agent
        if session_id not in active_agents:
            # Try to load from database
            if not supabase.client:
                await websocket.close(code=1011, reason="Database not available")
                return

            result = supabase.client.table("conversations").select("*").eq(
                "conversation_id", session_id
            ).execute()

            if not result.data:
                await websocket.close(code=1008, reason="Session not found")
                return

            conversation = result.data[0]

            # Get user profile
            user_profile = await supabase.get_user_profile(conversation["user_id"])
            if not user_profile:
                # Use test profile for development (same as session creation)
                print(f"⚠️  No profile for user {conversation['user_id']}, using test profile")
                user_profile = UserProfile(
                    user_id=conversation["user_id"],
                    preferences=UserPreferences(
                        traveler_type="explorer",
                        activity_level="high",
                        environment="mixed",
                        accommodation_style="boutique",
                        budget_sensitivity="medium",
                        culture_interest="high",
                        food_importance="high"
                    ),
                    constraints=UserConstraints(
                        dietary_restrictions=[],
                        climate_preferences=["mild_temperate", "hot_tropical"],
                        language_preferences=[]
                    ),
                    wishlist_regions=["Southeast Asia", "Iceland"],
                    past_destinations=["Paris", "Barcelona"]
                )

            # Rehydrate agent with conversation history
            agent = BrainstormAgent(user_profile)

            # Restore conversation memory from messages
            messages = conversation.get("messages", [])
            for msg in messages:
                if msg["role"] == "user":
                    agent.memory.chat_memory.add_user_message(msg["content"])
                elif msg["role"] == "assistant":
                    agent.memory.chat_memory.add_ai_message(msg["content"])

            active_agents[session_id] = agent
            print(f"✅ Rehydrated agent for session {session_id} with {len(messages)} messages")

        agent = active_agents[session_id]

        while True:
            # Receive message from user
            data = await websocket.receive_json()

            if data.get("type") == "message":
                user_message = data.get("content")
                print(f"DEBUG: Received message: {user_message[:50]}...")

                # Send thinking indicator
                await websocket.send_json({
                    "type": "thinking",
                    "session_id": session_id
                })

                # Stream response from agent with tag detection
                print(f"\n🤖 Starting to stream agent response...")
                full_response = ""
                token_count = 0
                inside_locations_tag = False
                stream_buffer = ""  # Buffer to detect tags in real-time
                pending_tokens = []  # Tokens waiting to be sent (in case partial tag detected)
                
                async for token in agent.chat(user_message):
                    full_response += token
                    token_count += 1
                    stream_buffer += token
                    pending_tokens.append(token)
                    
                    # Keep buffer reasonable size (last 200 chars to catch full tag)
                    if len(stream_buffer) > 200:
                        # Only trim if we're sure we're not in the middle of a tag
                        if not any(partial in stream_buffer[-200:-180] for partial in ["<loc", "<loca", "<locat"]):
                            stream_buffer = stream_buffer[-200:]
                    
                    # Check if we're entering <locations> tag
                    if not inside_locations_tag and "<locations>" in stream_buffer:
                        inside_locations_tag = True
                        print(f"🚫 Detected <locations> tag - suppressing stream")
                        
                        # Find where tag starts and send only tokens before it
                        tag_start_in_buffer = stream_buffer.find("<locations>")
                        # Calculate how many pending tokens are before the tag
                        chars_before_tag = tag_start_in_buffer
                        safe_content = stream_buffer[:chars_before_tag]
                        
                        # Send only the safe content before the tag
                        if safe_content:
                            await websocket.send_json({
                                "type": "token",
                                "session_id": session_id,
                                "token": safe_content
                            })
                        
                        pending_tokens = []
                        stream_buffer = ""
                        continue
                    
                    # If inside locations tag, don't send tokens
                    if inside_locations_tag:
                        pending_tokens = []  # Clear pending
                        # Check if we've closed the tag
                        if "</locations>" in stream_buffer:
                            inside_locations_tag = False
                            # Find content after closing tag
                            tag_end = stream_buffer.find("</locations>") + len("</locations>")
                            stream_buffer = stream_buffer[tag_end:]
                            print(f"✅ Detected </locations> tag - resuming stream")
                        continue
                    
                    # Check if buffer might contain start of tag (be cautious)
                    last_chars = stream_buffer[-15:] if len(stream_buffer) >= 15 else stream_buffer
                    possible_tag_start = any(last_chars.endswith(partial) for partial in ["<", "<l", "<lo", "<loc", "<loca", "<locat", "<locati", "<locatio", "<location"])
                    
                    if possible_tag_start:
                        # Hold tokens until we know if it's really a tag
                        if len(pending_tokens) <= 15:  # Max tag length
                            continue  # Wait for more tokens
                    
                    # Safe to send - no tag detected
                    if pending_tokens:
                        combined = "".join(pending_tokens)
                        await websocket.send_json({
                            "type": "token",
                            "session_id": session_id,
                            "token": combined
                        })
                        pending_tokens = []
                    
                    await asyncio.sleep(0.01)
                
                # Send any remaining pending tokens at the end
                if pending_tokens and not inside_locations_tag:
                    combined = "".join(pending_tokens)
                    await websocket.send_json({
                        "type": "token",
                        "session_id": session_id,
                        "token": combined
                    })
                    print(f"📤 Sent {len(pending_tokens)} remaining tokens at stream end")

                print(f"✅ Streaming complete - received {token_count} tokens, total length: {len(full_response)} chars")

                # Log full raw response for debugging
                print(f"\n{'='*80}")
                print(f"📜 RAW LLM RESPONSE (full text):")
                print(f"{'='*80}")
                print(full_response)
                print(f"{'='*80}\n")

                # Extract location proposals if present
                print(f"\n🔎 Checking for location proposals in response...")
                cleaned_response, locations = extract_location_proposals(full_response)

                # Send location proposals if found
                if locations:
                    print(f"\n📍 SENDING LOCATIONS TO CLIENT:")
                    print(f"   Session: {session_id}")
                    print(f"   Count: {len(locations)}")
                    for idx, loc in enumerate(locations, 1):
                        print(f"   {idx}. {loc.get('name')} ({loc.get('id')})")
                    
                    await websocket.send_json({
                        "type": "locations",
                        "session_id": session_id,
                        "locations": locations
                    })
                    print(f"✅ Location proposals sent via WebSocket")
                else:
                    print(f"ℹ️  No location proposals to send (locations is None)")

                # Send complete message (without location tags)
                print(f"\n💬 Sending final message to client (cleaned text, length: {len(cleaned_response)} chars)")
                await websocket.send_json({
                    "type": "message",
                    "session_id": session_id,
                    "role": "assistant",
                    "content": cleaned_response
                })
                print(f"✅ Complete message sent")

                # Persist to database (store cleaned response without location tags)
                if supabase.client:
                    # Get current conversation
                    result = supabase.client.table("conversations").select("messages").eq(
                        "conversation_id", session_id
                    ).execute()

                    if result.data:
                        current_messages = result.data[0].get("messages", [])

                        # Append new messages (use cleaned response)
                        current_messages.append({
                            "role": "user",
                            "content": user_message,
                            "timestamp": datetime.utcnow().isoformat()
                        })
                        current_messages.append({
                            "role": "assistant",
                            "content": cleaned_response,  # Store cleaned text without <locations>
                            "timestamp": datetime.utcnow().isoformat(),
                            "has_locations": locations is not None  # Flag for frontend
                        })

                        # Update conversation
                        supabase.client.table("conversations").update({
                            "messages": current_messages,
                            "updated_at": datetime.utcnow().isoformat()
                        }).eq("conversation_id", session_id).execute()

                        print(f"✅ Persisted conversation to database")

                print(f"DEBUG: Sent response, length: {len(full_response)}")

    except WebSocketDisconnect:
        print(f"DEBUG: WebSocket disconnected for session {session_id}")
    except Exception as e:
        print(f"ERROR: WebSocket error: {e}")
        import traceback
        traceback.print_exc()


@router.delete("/sessions/{session_id}")
async def delete_brainstorm_session(
    session_id: str,
    current_user: Optional[TokenData] = Depends(get_current_user_optional)
):
    """Delete brainstorm session from database"""
    user_id = current_user.user_id if current_user else TEST_USER_ID
    supabase = get_supabase()

    try:
        if not supabase.client:
            raise HTTPException(status_code=500, detail="Database not available")

        # Delete from database
        supabase.client.table("conversations").delete().eq(
            "conversation_id", session_id
        ).eq("user_id", user_id).execute()

        # Clean up in-memory agent
        if session_id in active_agents:
            del active_agents[session_id]

        print(f"✅ Deleted session {session_id}")

        return {"message": "Session deleted successfully"}

    except Exception as e:
        print(f"ERROR deleting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/{session_id}/recommendations")
async def create_recommendation_from_location(
    session_id: str,
    location_data: Dict[str, Any],
    current_user: Optional[TokenData] = Depends(get_current_user_optional)
):
    """
    Create a trip recommendation from a rated location proposal
    This converts a location proposal into a full trip plan
    """
    user_id = current_user.user_id if current_user else TEST_USER_ID
    supabase = get_supabase()

    try:
        if not supabase.client:
            raise HTTPException(status_code=500, detail="Database not available")

        # Verify session exists and belongs to user
        result = supabase.client.table("conversations").select("*").eq(
            "conversation_id", session_id
        ).eq("user_id", user_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Session not found")

        # Extract location data
        location_id = location_data.get("id")
        location_name = location_data.get("name")
        country = location_data.get("country")
        teaser = location_data.get("teaser")
        rating = location_data.get("rating")

        # Create destination info
        destination_info = DestinationInfo(
            name=location_name,
            city=location_name,  # Use location name as city
            country=country,
            region=country,  # Can be refined later
            description=teaser
        )

        # Create recommendation ID
        recommendation_id = uuid.uuid4()

        # Prepare data for database (bypassing Pydantic model to match DB schema)
        data = {
            "recommendation_id": str(recommendation_id),
            "user_id": user_id,
            "destination": destination_info.model_dump(),
            "reasoning": f"Selected from brainstorm session with {rating}/3 stars",
            "status": "selected",
            "confidence_score": float(rating) / 3.0 if rating else None,
            "source_conversation_id": session_id,
            "location_proposal_id": location_id,
        }
        
        response = supabase.client.table("destination_recommendations").insert(data).execute()

        print(f"✅ Created recommendation {recommendation_id} from session {session_id}")
        print(f"   Location: {location_name}, {country}")
        print(f"   Rating: {rating}/3")

        # Add trip creation message to conversation history for persistence
        try:
            trip_message = {
                "role": "assistant",
                "content": f"🎉 **Trip Created!**\n\nYour trip to **{location_name}** has been created successfully! You can now start planning your adventure.",
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {
                    "type": "trip_created",
                    "tripId": str(recommendation_id),
                    "title": f"Trip to {location_name}",
                    "locationName": location_name,
                    "imageUrl": location_data.get("imageUrl")
                }
            }
            
            # Fetch current conversation
            conv_result = supabase.client.table("conversations").select("messages").eq(
                "conversation_id", session_id
            ).execute()
            
            if conv_result.data:
                current_messages = conv_result.data[0].get("messages", [])
                current_messages.append(trip_message)
                
                # Update conversation with new message
                supabase.client.table("conversations").update({
                    "messages": current_messages,
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("conversation_id", session_id).execute()
                
                print(f"✅ Added trip creation message to conversation {session_id}")
        except Exception as e:
            print(f"⚠️  Failed to add trip message to conversation: {e}")
            # Don't fail the whole request if message persistence fails

        return {
            "recommendation_id": str(recommendation_id),
            "destination": destination_info.model_dump(),
            "status": "selected",
            "message": f"Trip to {location_name} created! Continue planning in Trip View."
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR creating recommendation: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/recommendations")
async def get_session_recommendations(
    session_id: str,
    current_user: Optional[TokenData] = Depends(get_current_user_optional)
):
    """
    Get all recommendations/trips created from this brainstorm session
    """
    user_id = current_user.user_id if current_user else TEST_USER_ID
    supabase = get_supabase()

    try:
        if not supabase.client:
            raise HTTPException(status_code=500, detail="Database not available")

        # Get recommendations for this session
        result = supabase.client.table("destination_recommendations").select("*").eq(
            "source_conversation_id", session_id
        ).eq("user_id", user_id).execute()

        recommendations = []
        for rec in result.data:
            recommendations.append({
                "id": rec["recommendation_id"],
                "destination": rec["destination"],
                "status": rec["status"],
                "rating": rec.get("confidence_score"),
                "createdAt": rec["created_at"],
                "location_proposal_id": rec.get("location_proposal_id")
            })

        return {"recommendations": recommendations}

    except Exception as e:
        print(f"ERROR fetching session recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations/{recommendation_id}")
async def get_recommendation_by_id(
    recommendation_id: str,
    current_user: Optional[TokenData] = Depends(get_current_user_optional)
):
    """
    Get a specific recommendation by ID (for trip planning view)
    """
    user_id = current_user.user_id if current_user else TEST_USER_ID
    supabase = get_supabase()

    try:
        if not supabase.client:
            raise HTTPException(status_code=500, detail="Database not available")

        # Get recommendation from database
        result = supabase.client.table("destination_recommendations").select("*").eq(
            "recommendation_id", recommendation_id
        ).eq("user_id", user_id).execute()

        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=404, detail="Recommendation not found")

        recommendation = result.data[0]
        
        return {
            "recommendation_id": recommendation["recommendation_id"],
            "destination": recommendation["destination"],
            "status": recommendation.get("status", "suggested"),
            "reasoning": recommendation.get("reasoning"),
            "confidence_score": recommendation.get("confidence_score"),
            "source_conversation_id": recommendation.get("source_conversation_id"),
            "created_at": recommendation["created_at"],
            "updated_at": recommendation["updated_at"]
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR fetching recommendation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/session/{session_id}/create_recommendation")
async def create_recommendation(session_id: str):
    """Create recommendation for a session (legacy endpoint)"""
    if session_id not in active_agents:
        raise HTTPException(status_code=404, detail="Session not found")

    agent = active_agents[session_id]
    recommendation = agent.create_recommendation()
    return recommendation

@router.get("/session/{session_id}/recommendation")
async def get_recommendation(session_id: str):
    """Get recommendation for a session"""
    if session_id not in active_agents:
        raise HTTPException(status_code=404, detail="Session not found")

    agent = active_agents[session_id]
    recommendation = agent.get_recommendation()
    return recommendation

@router.post("/session/{session_id}/recommendation/")
async def update_recommendation(
    session_id: str,
    id: str, 
    rating: Rating,
    **kwargs):
    """Update recommendation for a session"""
    if session_id not in active_agents:
        raise HTTPException(status_code=404, detail="Session not found")

    agent = active_agents[session_id]
    recommendation = agent.update_recommendation(id, rating)
    return recommendation