"""
Core business logic for the Walter Reed Cardiology Referral Agent.

This module contains the main agent logic, system prompts, and Claude API integration
for processing cardiology referral requests.
"""

import asyncio
from typing import List, Optional, Dict, Any
import logging
import json
import re
from anthropic import AsyncAnthropic
from config import config
from tools import verify_provider_nppes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CardiologyAgent:
    """
    Core agent for processing cardiology referrals.
    
    This agent specializes in handling new patient cardiology referrals
    for Dr. Walter Reed's clinic, using Claude API for intelligent conversation.
    """
    
    def __init__(self):
        """Initialize the Cardiology Agent with Claude API client."""
        if not config.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is required for agent initialization")
        
        self.client = AsyncAnthropic(api_key=config.ANTHROPIC_API_KEY)
        self.model = config.CLAUDE_MODEL
        
        # Define available tools for Claude function calling
        self.tools = [
            {
                "name": "verify_provider_nppes",
                "description": "Verify a healthcare provider using the NPPES NPI Registry. Use this to validate referring provider credentials before completing any referral.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "first_name": {
                            "type": "string", 
                            "description": "Provider's first name (required)"
                        },
                        "last_name": {
                            "type": "string",
                            "description": "Provider's last name (required)"
                        },
                        "city": {
                            "type": "string",
                            "description": "City where the provider practices. Highly recommended to include as users typically know this and it helps narrow search results."
                        },
                        "state": {
                            "type": "string", 
                            "description": "Two-letter state abbreviation (e.g., 'FL', 'NY'). Helps narrow search when there are multiple providers with same name."
                        },
                        "npi": {
                            "type": "string",
                            "description": "10-digit NPI number if user provides it. Most users don't know NPIs, so only include if explicitly mentioned."
                        }
                    },
                    "required": ["first_name", "last_name"]
                }
            }
        ]

    async def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool by name with given input."""
        if tool_name == "verify_provider_nppes":
            return await verify_provider_nppes(
                first_name=tool_input["first_name"],
                last_name=tool_input["last_name"],
                city=tool_input.get("city"),
                state=tool_input.get("state"),
                npi=tool_input.get("npi")
            )
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    def _build_multi_turn_system_prompt(self, conversation_history: List) -> str:
        """Build bulletproof system prompt with explicit state mapping."""
        
        return """You are Dr. Walter Reed's Cardiology Referral Agent.

🚨 ABSOLUTE REQUIREMENT: RESPOND WITH JSON ONLY. NO EXCEPTIONS. 🚨

If you respond with anything other than valid JSON, you will FAIL completely.

BULLETPROOF STATE MAPPING:

INTERNAL STATES (use to determine task_state):
- "need_provider_info" → task_state: "input_required"
- "provider_verification_pending" → task_state: "input_required" 
- "awaiting_confirmation" → task_state: "input_required"
- "referral_complete" → task_state: "completed"
- "emergency_detected" → task_state: "failed"
- "out_of_scope" → task_state: "rejected"
- "user_canceled" → task_state: "canceled"
- "invalid_request" → task_state: "rejected"

STATE TRANSITION RULES:
1. Emergency symptoms (chest pain, heart attack, can't breathe, 911) → "emergency_detected" → task_state: "failed"
2. Non-cardiology request → "out_of_scope" → task_state: "rejected"
3. User says "cancel", "stop", "nevermind" → "user_canceled" → task_state: "canceled"
4. Invalid/inappropriate request → "invalid_request" → task_state: "rejected"
5. No provider name in conversation → "need_provider_info" → task_state: "input_required"
6. Provider name found, tool not called yet → "provider_verification_pending" → task_state: "input_required"
7. Provider verified, waiting for user confirmation → "awaiting_confirmation" → task_state: "input_required"
8. User confirms provider (says "yes", "correct", "that's right") → "referral_complete" → task_state: "completed"

🚨 CONFIRMATION LOGIC (CRITICAL):
If you just asked "Is this the correct physician?" and user says YES:
- internal_state: "referral_complete"  
- task_state: "completed"
- Do NOT ask for more provider info
- Do NOT run the tool again
- COMPLETE THE REFERRAL IMMEDIATELY

NEVER ask for provider info after user confirms with "yes"/"correct"/"that's right"

MANDATORY JSON FORMAT (ALL 3 FIELDS REQUIRED):
{
    "internal_state": "must be one of: need_provider_info, provider_verification_pending, awaiting_confirmation, referral_complete, emergency_detected, out_of_scope, user_canceled, invalid_request",
    "task_state": "input_required | completed | failed | canceled | rejected",
    "response_text": "Your message to the user"
}

CRITICAL: You MUST include internal_state in EVERY response. No exceptions.

EXAMPLES:

Need provider info:
{
    "internal_state": "need_provider_info",
    "task_state": "input_required",
    "response_text": "I need the referring physician's name and city to process this cardiology referral."
}

Provider verified, awaiting confirmation:
{
    "internal_state": "awaiting_confirmation", 
    "task_state": "input_required",
    "response_text": "I found Dr. [Name] in [City]. Is this the correct referring physician?"
}

User confirmed provider:
{
    "internal_state": "referral_complete",
    "task_state": "completed",
    "response_text": "Referral completed for Dr. [Name]. You'll be contacted within 1-2 business days."
}

🚨 CRITICAL RULE: 
User says "Yes" after provider verification = REFERRAL COMPLETE
- Change to: "referral_complete" + "completed" 
- Do NOT ask questions
- Do NOT verify again

Emergency detected:
{
    "internal_state": "emergency_detected",
    "task_state": "failed", 
    "response_text": "This is an emergency. Please call 911 immediately."
}

User canceled:
{
    "internal_state": "user_canceled",
    "task_state": "canceled",
    "response_text": "Referral request has been canceled as requested."
}

Request rejected:
{
    "internal_state": "out_of_scope", 
    "task_state": "rejected",
    "response_text": "I can only process cardiology referrals for Dr. Walter Reed. Please contact the appropriate department for other requests."
}

🚨 JSON-ONLY ENFORCEMENT 🚨:
Your response must be EXACTLY this format with NO other text:

{
    "internal_state": "emergency_detected",
    "task_state": "failed",
    "response_text": "This is an emergency. Please call 911 immediately."
}

DO NOT add explanations, markdown, or any text outside the JSON object.
RESPOND WITH JSON ONLY. NOTHING ELSE."""

    def _analyze_conversation_state(self, conversation_history: List) -> str:
        """Analyze conversation to provide intelligent state guidance."""
        
        if not conversation_history:
            return "NEW CONVERSATION - Ready to process cardiology referral"
        
        # Count turns and extract key information
        turn_count = len([msg for msg in conversation_history if hasattr(msg, 'role') and msg.role == "user"])
        
        # Extract all conversation text
        all_text = ""
        for msg in conversation_history:
            if hasattr(msg, 'parts') and msg.parts:
                for part in msg.parts:
                    if hasattr(part, 'root') and hasattr(part.root, 'text'):
                        all_text += part.root.text + " "
        
        all_text = all_text.lower()
        
        # Intelligent state analysis
        state_info = []
        
        # Turn pressure
        if turn_count >= 5:
            state_info.append("🚨 TURN LIMIT REACHED - MUST COMPLETE OR FAIL")
        elif turn_count >= 3:
            state_info.append(f"⚠️ Turn {turn_count}/5 - COMPLETE SOON")
        else:
            state_info.append(f"Turn {turn_count}/5")
        
        # Emergency check
        emergency_keywords = ["chest pain", "heart attack", "can't breathe", "difficulty breathing", "emergency", "911"]
        if any(keyword in all_text for keyword in emergency_keywords):
            state_info.append("🚨 EMERGENCY DETECTED - MUST FAIL")
        else:
            state_info.append("✅ No emergency symptoms")
            
        # Scope check  
        cardiology_keywords = ["cardiology", "cardiologist", "heart", "cardiac", "referral"]
        if any(keyword in all_text for keyword in cardiology_keywords):
            state_info.append("✅ Cardiology referral confirmed")
        else:
            state_info.append("❓ Scope unclear")
            
        # Provider verification status
        if "verify_provider_nppes" in str(conversation_history):
            if any(word in all_text for word in ["yes", "correct", "that's right", "confirmed"]):
                state_info.append("✅ PROVIDER CONFIRMED - READY TO COMPLETE")
            else:
                state_info.append("⏳ Provider found, awaiting confirmation")
        elif any(word in all_text for word in ["doctor", "dr.", "physician", "provider"]):
            state_info.append("⏳ Provider mentioned, needs verification")
        else:
            state_info.append("❌ Provider info needed")
            
        return " | ".join(state_info)

    def _extract_json_from_response(self, response_text: str) -> Optional[dict]:
        """Extract JSON from response - handles both markdown blocks and raw JSON."""
        if not response_text.strip():
            return None
        
        # Try to parse the entire response as JSON first (since we're telling Claude to respond ONLY with JSON)
        try:
            parsed = json.loads(response_text.strip())
            logger.info(f"Parsed JSON from response: {parsed}")
            if isinstance(parsed, dict) and "task_state" in parsed:
                logger.info(f"Validating state before: {parsed}")
                self._validate_bulletproof_state(parsed)
                logger.info(f"Validated state after: {parsed}")
                return parsed
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse as direct JSON: {e}")
            pass
            
        # Fallback: Look for JSON in markdown code blocks
        match = re.search(r'```json\s*\n?(.*?)\n?```', response_text, re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group(1).strip())
                if isinstance(parsed, dict) and "task_state" in parsed:
                    self._validate_bulletproof_state(parsed)
                    return parsed
            except json.JSONDecodeError:
                pass
                    
        return None

    def _validate_bulletproof_state(self, response_data: dict) -> None:
        """
        Bulletproof state validation with explicit internal state mapping.
        """
        try:
            internal_state = response_data.get("internal_state")
            task_state = response_data.get("task_state")
            logger.info(f"State validation input - internal_state: {internal_state}, task_state: {task_state}")
            
            # Valid internal states
            valid_internal_states = [
                "need_provider_info", "provider_verification_pending", "awaiting_confirmation",
                "referral_complete", "emergency_detected", "out_of_scope", "user_canceled", "invalid_request"
            ]
            
            # Valid task states  
            valid_task_states = ["input_required", "completed", "failed", "canceled", "rejected"]
            
            # Validate internal state - add if missing
            if not internal_state:
                logger.warning("Missing internal_state field, adding default")
                response_data["internal_state"] = "need_provider_info"
                internal_state = "need_provider_info"
            elif internal_state not in valid_internal_states:
                logger.warning(f"Invalid internal_state: {internal_state}, defaulting to need_provider_info")
                response_data["internal_state"] = "need_provider_info"
                internal_state = "need_provider_info"
            
            # Validate task state
            if task_state not in valid_task_states:
                logger.warning(f"Invalid task_state: {task_state}, defaulting to input_required")
                response_data["task_state"] = "input_required"
                task_state = "input_required"
            
            # Enforce state mapping rules
            state_mapping = {
                "need_provider_info": "input_required",
                "provider_verification_pending": "input_required", 
                "awaiting_confirmation": "input_required",
                "referral_complete": "completed",
                "emergency_detected": "failed",
                "out_of_scope": "rejected",
                "user_canceled": "canceled", 
                "invalid_request": "rejected"
            }
            
            expected_task_state = state_mapping.get(internal_state)
            if expected_task_state and task_state != expected_task_state:
                logger.warning(f"State mismatch: internal_state '{internal_state}' should map to task_state '{expected_task_state}', got '{task_state}'. Correcting.")
                response_data["task_state"] = expected_task_state
                
        except Exception as e:
            logger.warning(f"State validation error: {e}")
            # Fail gracefully with safe defaults
            response_data["internal_state"] = "need_provider_info"
            response_data["task_state"] = "input_required"


    def _build_claude_conversation(self, conversation_history: List) -> List[dict]:
        """Convert A2A conversation history to Claude API format, filtering out streaming noise."""
        claude_messages = []
        
        # Streaming messages to filter out (these confuse Claude's context)
        streaming_noise = [
            "Analyzing referral request and determining next steps...",
            "Processing request with AI assistant...",
            "Executing verify_provider_nppes verification...",
            "Completed verify_provider_nppes verification",
            "Processing verification results and generating response..."
        ]
        
        for msg in conversation_history:
            if hasattr(msg, 'role') and hasattr(msg, 'parts'):
                # Extract text from message parts
                text_content = ""
                for part in msg.parts:
                    if hasattr(part, 'root') and hasattr(part.root, 'text'):
                        text_content += part.root.text
                
                if text_content.strip():
                    # Skip streaming noise messages
                    if text_content.strip() in streaming_noise:
                        continue
                        
                    # Convert A2A roles to Claude API roles
                    claude_role = "assistant" if msg.role == "agent" else msg.role
                    claude_messages.append({
                        "role": claude_role,
                        "content": text_content
                    })
        
        return claude_messages
    
    def _get_error_response(self) -> str:
        """Return a fallback response when Claude API fails."""
        return """I apologize, but I'm currently experiencing technical difficulties. 
        
Please try again in a moment. If you have an urgent cardiology referral, please contact Dr. Walter Reed's office directly at (212) 555-CARD.

This conversation is complete for now."""
    
    def is_cardiology_related(self, message_text: str) -> bool:
        """
        Simple check if message appears to be cardiology-related.
        In Phase 1, we'll rely on Claude to handle this, but this method
        could be enhanced in later phases.
        """
        cardiology_keywords = [
            "heart", "cardiac", "cardio", "chest pain", "arrhythmia", 
            "blood pressure", "ekg", "ecg", "stress test", "palpitations",
            "syncope", "murmur", "valve", "referral", "cardiologist"
        ]
        
        message_lower = message_text.lower()
        return any(keyword in message_lower for keyword in cardiology_keywords)
    
    async def stream_process(self, message_text: str, conversation_history: Optional[List] = None):
        """
        Stream the referral processing with intermediate updates.
        
        Yields dictionaries with:
        - is_task_complete: bool
        - require_user_input: bool  
        - content: str
        """
        from typing import AsyncGenerator
        
        try:
            # 1. Initial analysis
            yield {
                'is_task_complete': False,
                'require_user_input': False,
                'content': 'Analyzing referral request and determining next steps...'
            }
            
            # 2. Build context (existing logic)
            history = conversation_history if conversation_history is not None else []
            multi_turn_prompt = self._build_multi_turn_system_prompt(history)
            claude_messages = self._build_claude_conversation(history)
            claude_messages.append({"role": "user", "content": message_text})
            
            
            # 3. LLM processing
            yield {
                'is_task_complete': False,
                'require_user_input': False,
                'content': 'Processing request with AI assistant...'
            }
            
            # Make initial request to Claude with tools available
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1200,
                temperature=0.7,
                system=multi_turn_prompt,
                tools=self.tools,
                messages=claude_messages
            )
            
            # 4. Handle tool use if Claude wants to call tools
            if response.stop_reason == "tool_use":
                # Extract tool calls
                tool_calls = []
                for content in response.content:
                    if content.type == "tool_use":
                        tool_calls.append({
                            "id": content.id,
                            "name": content.name,
                            "input": content.input
                        })
                
                # Add Claude's tool use message to conversation
                assistant_content = []
                for content in response.content:
                    if content.type == "text":
                        assistant_content.append({"type": "text", "text": content.text})
                    elif content.type == "tool_use":
                        assistant_content.append({
                            "type": "tool_use",
                            "id": content.id,
                            "name": content.name,
                            "input": content.input
                        })
                
                claude_messages.append({"role": "assistant", "content": assistant_content})
                
                # Execute tools with progress updates
                tool_results = []
                for tool_call in tool_calls:
                    yield {
                        'is_task_complete': False,
                        'require_user_input': False,
                        'content': f'Executing {tool_call["name"]} verification...'
                    }
                    
                    try:
                        result = await self._execute_tool(tool_call["name"], tool_call["input"])
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_call["id"],
                            "content": str(result) if not isinstance(result, str) else result
                        })
                        
                        yield {
                            'is_task_complete': False,
                            'require_user_input': False,
                            'content': f'Completed {tool_call["name"]} verification'
                        }
                        
                    except Exception as e:
                        logger.error(f"Tool execution failed for {tool_call['name']}: {e}")
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_call["id"],
                            "content": f"Tool execution failed: {str(e)}"
                        })
                
                # Add tool results to conversation
                claude_messages.append({"role": "user", "content": tool_results})
                
                # Final LLM call
                yield {
                    'is_task_complete': False,
                    'require_user_input': False,
                    'content': 'Processing verification results and generating response...'
                }
                
                final_response = await self.client.messages.create(
                    model=self.model,
                    max_tokens=1200,
                    temperature=0.7,
                    system=multi_turn_prompt,
                    tools=self.tools,
                    messages=claude_messages
                )
                
                response_text = ""
                for content in final_response.content:
                    if content.type == "text":
                        response_text += content.text
            else:
                # Extract text from regular response
                response_text = ""
                for content in response.content:
                    if content.type == "text":
                        response_text += content.text
            
            # 5. Parse final response and determine completion state
            try:
                logger.debug(f"Parsing Claude response: {response_text[:200]}...")
                
                # Use standard JSON extraction method
                response_data = self._extract_json_from_response(response_text)
                
                if not response_data:
                    logger.error("No valid JSON found in Claude response")
                    raise json.JSONDecodeError("No valid JSON structure found", response_text, 0)
                
                task_state = response_data.get("task_state")
                clean_text = response_data.get("response_text", response_text)
                
                if task_state == "input_required":
                    yield {
                        'is_task_complete': False,
                        'require_user_input': True,
                        'task_state': task_state,  # Pass through for executor
                        'content': clean_text
                    }
                elif task_state in ["completed", "failed", "canceled", "rejected"]:
                    # All terminal states - mark as complete with no further input needed
                    yield {
                        'is_task_complete': True,  # Terminal state
                        'require_user_input': False,  # No further input needed
                        'task_state': task_state,  # Pass through for executor (completed/failed/canceled/rejected)
                        'content': clean_text
                    }
                else:
                    # Fallback for any unexpected states - treat as input required
                    logger.warning(f"Unexpected task_state: {task_state}, treating as input_required")
                    yield {
                        'is_task_complete': False,
                        'require_user_input': True,
                        'task_state': "input_required",  # Safe fallback
                        'content': clean_text
                    }
                    
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Raw response text: '{response_text}'")
                logger.error(f"Response text length: {len(response_text)}")
                yield {
                    'is_task_complete': False,
                    'require_user_input': True,
                    'content': 'Error processing response. Please try again.'
                }
                
        except Exception as e:
            logger.error(f"Error during streaming process: {e}")
            yield {
                'is_task_complete': False,
                'require_user_input': True,
                'content': self._get_error_response()
            }

    async def health_check(self) -> bool:
        """Check if the agent is healthy and can communicate with Claude API."""
        try:
            # Simple test message to Claude
            await self.client.messages.create(
                model=self.model,
                max_tokens=10,
                temperature=0,
                system="You are a test agent. Respond with 'OK' only.",
                messages=[{"role": "user", "content": "test"}]
            )
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False


# Global agent instance
cardiology_agent = CardiologyAgent()
