"""
Trip Planning API endpoints with WebSocket support
"""
import asyncio
import json
import re
from typing import Dict, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from datetime import datetime

from app.services.supabase_service import get_supabase
from app.agents.planning_agent import PlanningAgent
from app.models.user import UserProfile, UserPreferences, UserConstraints
from app.models.destination import DestinationRecommendation, DestinationInfo
from app.api.deps import get_current_user_optional
from app.models.user import TokenData

router = APIRouter(tags=["planning"])

# Store active planning agents per recommendation_id
active_planning_agents: Dict[str, PlanningAgent] = {}

# Test user ID for development
TEST_USER_ID = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"


def extract_trip_updates(text: str) -> list:
    """
    Extract <trip_update> tags from LLM response for structured data extraction
    Returns list of {field, value, currency} dicts
    """
    pattern = r'<trip_update>\s*(\{[^}]+\})\s*</trip_update>'
    matches = re.findall(pattern, text, re.DOTALL)
    
    updates = []
    for match in matches:
        try:
            data = json.loads(match)
            updates.append(data)
            print(f"✅ Extracted trip update: {data.get('field')} = {data.get('value')}")
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse trip update JSON: {e}")
            continue
    
    return updates


async def apply_trip_updates(recommendation_id: str, user_id: str, updates: list):
    """
    Apply structured updates to destination_recommendations table
    """
    if not updates:
        return
    
    supabase = get_supabase()
    if not supabase.client:
        print("⚠️ Supabase not available, skipping trip updates")
        return
    
    try:
        # Build update dict
        update_data = {"updated_at": datetime.utcnow().isoformat()}
        
        for update in updates:
            field = update.get("field")
            value = update.get("value")
            
            if field and value is not None:
                update_data[field] = value
                
                # Handle currency separately if present
                if field == "estimated_budget" and "currency" in update:
                    update_data["currency"] = update["currency"]
        
        # Update database
        result = supabase.client.table("destination_recommendations").update(
            update_data
        ).eq("recommendation_id", recommendation_id).eq("user_id", user_id).execute()
        
        print(f"✅ Applied {len(updates)} trip updates to recommendation {recommendation_id}")
        
    except Exception as e:
        print(f"❌ Error applying trip updates: {e}")


@router.websocket("/ws/{recommendation_id}")
async def planning_websocket(
    websocket: WebSocket,
    recommendation_id: str
):
    """
    WebSocket endpoint for real-time trip planning conversation
    """
    await websocket.accept()
    print(f"🔌 Planning WebSocket connected for recommendation: {recommendation_id}")
    
    try:
        # Get user_id from query params or use test user
        user_id = websocket.query_params.get("user_id", TEST_USER_ID)
        supabase = get_supabase()
        
        if not supabase.client:
            await websocket.close(code=1011, reason="Database not available")
            return
        
        # Fetch recommendation from database
        rec_result = supabase.client.table("destination_recommendations").select("*").eq(
            "recommendation_id", recommendation_id
        ).eq("user_id", user_id).execute()
        
        if not rec_result.data or len(rec_result.data) == 0:
            await websocket.close(code=1008, reason="Recommendation not found")
            return
        
        rec_data = rec_result.data[0]
        
        # Fetch user profile
        profile_result = supabase.client.table("user_profiles").select("*").eq(
            "user_id", user_id
        ).execute()
        
        if not profile_result.data or len(profile_result.data) == 0:
            # Fallback test profile (same as brainstorm)
            print(f"⚠️ No profile found for {user_id}, using fallback test profile")
            user_profile = UserProfile(
                user_id=user_id,
                preferences=UserPreferences(
                    traveler_type="explorer",
                    activity_level="high",
                    accommodation_style="boutique",
                    environment="mixed",
                    budget_sensitivity="medium",
                    culture_interest="high",
                    food_importance="high"
                ),
                constraints=UserConstraints()
            )
        else:
            profile_data = profile_result.data[0]
            user_profile = UserProfile(
                user_id=profile_data["user_id"],
                preferences=UserPreferences(**profile_data.get("preferences", {})),
                constraints=UserConstraints(**profile_data.get("constraints", {}))
            )
        
        # Build DestinationRecommendation object
        destination = DestinationInfo(**rec_data["destination"])
        recommendation = DestinationRecommendation(
            recommendation_id=rec_data["recommendation_id"],
            user_id=rec_data["user_id"],
            destination=destination
        )
        
        # Add optional fields if present
        if rec_data.get("optimal_season"):
            recommendation.optimal_season = rec_data["optimal_season"]
        if rec_data.get("estimated_budget"):
            recommendation.estimated_budget = rec_data["estimated_budget"]
        if rec_data.get("highlights"):
            recommendation.highlights = rec_data["highlights"]
        
        # TODO: Fetch existing planning messages from database (when we have trip_conversations table)
        existing_messages = []
        
        # Create or reuse planning agent
        if recommendation_id not in active_planning_agents:
            agent = PlanningAgent(
                recommendation=recommendation,
                user_profile=user_profile,
                existing_messages=existing_messages
            )
            active_planning_agents[recommendation_id] = agent
            print(f"✅ Created new planning agent for {recommendation_id}")
        else:
            agent = active_planning_agents[recommendation_id]
            print(f"🔄 Reusing existing planning agent for {recommendation_id}")
        
        # WebSocket message loop
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "message":
                user_message = data.get("content", "")
                print(f"📨 Received planning message: {user_message[:100]}...")
                
                # Send "thinking" status
                await websocket.send_json({
                    "type": "thinking",
                    "recommendation_id": recommendation_id
                })
                
                # Stream response from planning agent
                full_response = ""
                token_count = 0
                
                # Real-time tag filtering (hide <trip_update> tags from stream)
                stream_buffer = ""
                pending_tokens = []
                inside_update_tag = False
                
                async for token in agent.chat(user_message):
                    full_response += token
                    token_count += 1
                    stream_buffer += token
                    pending_tokens.append(token)
                    
                    # Keep buffer reasonable size
                    if len(stream_buffer) > 200:
                        if not any(partial in stream_buffer[-200:-180] for partial in ["<tri", "<trip"]):
                            stream_buffer = stream_buffer[-200:]
                    
                    # Check if we're entering <trip_update> tag
                    if not inside_update_tag and "<trip_update>" in stream_buffer:
                        inside_update_tag = True
                        print(f"🚫 Detected <trip_update> tag - suppressing stream")
                        
                        # Send only content before tag
                        tag_start = stream_buffer.find("<trip_update>")
                        safe_content = stream_buffer[:tag_start]
                        
                        if safe_content:
                            await websocket.send_json({
                                "type": "token",
                                "recommendation_id": recommendation_id,
                                "token": safe_content
                            })
                        
                        pending_tokens = []
                        stream_buffer = ""
                        continue
                    
                    # If inside update tag, don't send tokens
                    if inside_update_tag:
                        pending_tokens = []
                        # Check if we've closed the tag
                        if "</trip_update>" in stream_buffer:
                            inside_update_tag = False
                            tag_end = stream_buffer.find("</trip_update>") + len("</trip_update>")
                            stream_buffer = stream_buffer[tag_end:]
                            print(f"✅ Detected </trip_update> tag - resuming stream")
                        continue
                    
                    # Check if buffer might contain start of tag
                    last_chars = stream_buffer[-15:] if len(stream_buffer) >= 15 else stream_buffer
                    possible_tag_start = any(last_chars.endswith(partial) for partial in ["<", "<t", "<tr", "<tri", "<trip", "<trip_", "<trip_u", "<trip_up"])
                    
                    if possible_tag_start:
                        if len(pending_tokens) <= 15:
                            continue
                    
                    # Safe to send
                    if pending_tokens:
                        combined = "".join(pending_tokens)
                        await websocket.send_json({
                            "type": "token",
                            "recommendation_id": recommendation_id,
                            "token": combined
                        })
                        pending_tokens = []
                    
                    await asyncio.sleep(0.01)
                
                # Send any remaining pending tokens
                if pending_tokens and not inside_update_tag:
                    combined = "".join(pending_tokens)
                    await websocket.send_json({
                        "type": "token",
                        "recommendation_id": recommendation_id,
                        "token": combined
                    })
                
                # Extract and apply structured updates
                updates = extract_trip_updates(full_response)
                if updates:
                    await apply_trip_updates(recommendation_id, user_id, updates)
                    
                    # Notify client about updates
                    await websocket.send_json({
                        "type": "trip_updated",
                        "recommendation_id": recommendation_id,
                        "updates": updates
                    })
                
                # Clean response (remove update tags)
                cleaned_response = re.sub(r'<trip_update>.*?</trip_update>', '', full_response, flags=re.DOTALL).strip()
                
                # Send complete message
                await websocket.send_json({
                    "type": "complete",
                    "recommendation_id": recommendation_id,
                    "content": cleaned_response
                })
                
                print(f"✅ Planning response complete ({token_count} tokens, {len(updates)} updates)")
                
                # TODO: Persist conversation to trip_conversations table
            
            elif message_type == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        print(f"🔌 Planning WebSocket disconnected for {recommendation_id}")
    except Exception as e:
        print(f"❌ Planning WebSocket error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except:
            pass
    finally:
        # Clean up agent after some time (optional - could keep for reuse)
        # For now, keep it cached
        print(f"👋 Planning WebSocket closed for {recommendation_id}")


@router.get("/recommendations/{recommendation_id}/summary")
async def get_trip_summary(
    recommendation_id: str,
    current_user: Optional[TokenData] = Depends(get_current_user_optional)
):
    """
    Get AI-generated summary of trip planning progress
    """
    user_id = current_user.user_id if current_user else TEST_USER_ID
    supabase = get_supabase()
    
    try:
        if not supabase.client:
            raise HTTPException(status_code=500, detail="Database not available")
        
        # Fetch recommendation with all accumulated data
        result = supabase.client.table("destination_recommendations").select("*").eq(
            "recommendation_id", recommendation_id
        ).eq("user_id", user_id).execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=404, detail="Recommendation not found")
        
        rec = result.data[0]
        
        # Build summary from accumulated data
        summary = {
            "destination": rec["destination"],
            "season": rec.get("optimal_season"),
            "budget": {
                "amount": rec.get("estimated_budget"),
                "currency": rec.get("currency", "USD")
            } if rec.get("estimated_budget") else None,
            "highlights": rec.get("highlights", []),
            "status": rec.get("status"),
            "completeness": calculate_completeness(rec)
        }
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR fetching trip summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def calculate_completeness(rec: dict) -> dict:
    """Calculate how complete the trip planning is"""
    total_fields = 8
    completed = 0
    
    if rec.get("optimal_season"):
        completed += 1
    if rec.get("estimated_budget"):
        completed += 1
    if rec.get("highlights") and len(rec["highlights"]) >= 3:
        completed += 1
    # TODO: Add more fields when we extend the schema
    # - dates (start_date, end_date)
    # - accommodation recommendations
    # - flight options
    # - packing list
    # - documents checklist
    
    return {
        "percentage": int((completed / total_fields) * 100),
        "completed_fields": completed,
        "total_fields": total_fields,
        "missing": ["dates", "flights", "accommodation", "packing_list", "documents"] if completed < 4 else []
    }

from app.prompts.loader import get_prompt_loader

@router.get("/technical-details")
async def get_technical_details(
    destination: str,
):
    """
    Get technical details for a destination
    """
    print(f"Getting technical details for {destination}")
    prompt_loader = get_prompt_loader()

    return prompt_loader.load_template(
        module="planning",
        prompt_name="location_technical_details",
        destination=destination
    )