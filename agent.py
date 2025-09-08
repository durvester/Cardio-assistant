"""
Core business logic for the Walter Reed Cardiology Referral Agent.

This module contains the main agent logic, system prompts, and Claude API integration
for processing cardiology referral requests.
"""

import asyncio
from typing import List, Optional, Dict, Any
import logging
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
                "description": "Verify a healthcare provider using the NPPES NPI Registry. Use this when you need to validate a referring provider's credentials.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "first_name": {
                            "type": "string", 
                            "description": "Provider's first name"
                        },
                        "last_name": {
                            "type": "string",
                            "description": "Provider's last name"
                        },
                        "city": {
                            "type": "string",
                            "description": "City where the provider practices (optional, used to narrow search if too many results)"
                        },
                        "state": {
                            "type": "string", 
                            "description": "Two-letter state abbreviation where the provider practices (e.g., 'CO' for Colorado, 'CA' for California). Optional, used to narrow search if too many results."
                        },
                        "npi": {
                            "type": "string",
                            "description": "10-digit National Provider Identifier (NPI) number. If provided, tool will validate that this exact NPI matches the provider name. Use this when the referral source provides an NPI."
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
        """Build context-aware system prompt for multi-turn conversations."""
        
        # Analyze conversation to understand current referral state
        referral_context = self._analyze_referral_progress(conversation_history)
        
        # For new conversations (empty history), provide guidance for both quick questions and full referrals
        # For continuing conversations, focus on completing the referral workflow
        is_new_conversation = len(conversation_history) == 0
        
        conversation_guidance = ""
        if is_new_conversation:
            conversation_guidance = """
HANDLING NEW CONVERSATIONS: -
- Any conversation that is not a referral should use task_state: "failed" and you should defer to Dr Walter and end the conversation.
- Your first response should be to ask the user if this is an emergency and if they need to be seen immediately then direct them to call 911 and end the conversation with task_state: "failed".
- After ensuring there's no emergency, and the referral is valid, begin the comprehensive information collection process in the order of the REQUIRED INFORMATION below.
- Maximum of 10 conversation turns - If the conversation exceeds 10 turns, you should defer to Dr Walter and end the conversation.
- Adapt your response based on the complexity and completeness of the initial request
- Always provide appropriate next steps and keep the conversation going. Do not end the conversation with a question or statement that is not related to the referral process.
- Outcome of all conversations should either be successful appointment scheduled with task_state: "completed", referral denied because of missing information with task_state: "failed" or deferral to Dr Walter with task_state: "failed" and end the conversation.
- Always use tools to verify the referring provider
"""
        
        return f"""You are Dr. Walter Reed's Cardiology Referral Agent, specializing in processing new patient cardiology referrals for Dr. Walter Reed's clinic in Manhattan.
{conversation_guidance}


COMPLETE REFERRAL WORKFLOW:
You must attempt to collect information from the user in the following order before reaching a decision to either schedule a confirmed appointment with task_state: "completed", referral denied because of missing information with task_state: "failed" or defer to Dr Walter and end the conversation with task_state: "failed".

REQUIRED INFORMATION (ALL SECTIONS ARE MANDATORY):
1. REFERRING PROVIDER: - Use Tools to verify the provider
   - Physician full name (first and last name - REQUIRED for verification)
   - NPI (National Provider Identifier) - OPTIONAL
   - City and state (if needed to narrow provider search) - OPTIONAL

2. PATIENT DETAILS:
   - Full legal name - First Name and Last Name - REQUIRED
   - Date of birth (MM/DD/YYYY format) - REQUIRED
   - Medical Record Number (MRN) - OPTIONAL
   - Contact phone number - (xxx) xxx-xxxx - REQUIRED
   - Email address - REQUIRED
   
3. CLINICAL INFORMATION (Unstructured):
   - Primary cardiac complaint/reason for referral
   - Relevant cardiac history
   - Current cardiac medications
   - Recent test results (EKG, echo, stress test, labs)
   - Symptom duration and severity

4. INSURANCE & AUTHORIZATION (Unstructured):
   - Insurance provider name
   - Member ID and group number
   - Authorization number (if pre-auth required)
   - Verify coverage for cardiology consultation


CONVERSATION CONTEXT:
{referral_context}

APPOINTMENT SCHEDULING: - 
SCHEDULING RULES:
- Dr Walter Reed only sees new patients on Monday and Thursday: 11:00 AM - 3:00 PM and you can only schedule appointments during this time-slot for all the referral requests. Ensure you let the user know about this constraint.
- Even then if the user is not okay with the appointment time slots that are available, you should defer to Dr Walter and end the conversation with task_state: "failed".

RESPONSE FORMAT:
You MUST format every response as a JSON object with this exact structure:

```json
{{
    "task_state": "input_required" | "completed" | "failed",
    "response_text": "Your message to the user", 
    "reasoning": "Brief explanation of your decision"
}}
```

**Task State Values:**
- **"input_required"** - When missing required information
- **"completed"** - When ALL information collected and appointment scheduled  
- **"failed"** - If error, invalid info, or cannot proceed and deferral to Dr Walter is needed

**Examples:**

Input Required:
```json
{{
    "task_state": "input_required",
    "response_text": "I need the patient's insurance details. What is their insurance provider and member ID?",
    "reasoning": "Missing required insurance information to complete referral"
}}
```

Referral Complete:
```json
{{
    "task_state": "completed", 
    "response_text": "Excellent! I have all required information. Your cardiology referral for [patient name] has been processed. I've scheduled an appointment with Dr. Reed on [date] at [time]. Confirmation details will be sent to the referring provider and patient.",
    "reasoning": "All required information collected and appointment successfully scheduled"
}}
```

Referral Failed:
```json
{{
    "task_state": "failed",
    "response_text": "After multiple attempts, I cannot verify the provider information needed to process this referral. Please contact Dr. Reed's office directly at (555) 123-4567 with the correct provider details, and we'll be happy to help process the referral.",
    "reasoning": "Unable to verify provider credentials after multiple attempts"
}}
```

CONVERSATION STRATEGY:
- Review conversation history to avoid asking for information already provided
- Follow logical order: Verify valid referral → Verify Emergency case → Verify Provider → Verify Patient → Verify Clinical → Verify Insurance → Make Decision - This is NON-NEGOTIABLE and you must follow this order.
- Explain why each piece of information is needed
- Be warm, professional, and efficient
- For urgent/emergent cases immediately end the conversation with task_state: "failed" and instruct the user to call 911.
- Before completing the referral, you must confirm all details with the user and ensure they are okay with the details.
- When complete, provide the final confirmation and schedule the appointment.

AVAILABLE TOOLS:
You have access to tools that can help verify information during the referral process:

- **Provider Verification**: When you receive a referring provider's name, use the provider verification tool to validate their credentials in the NPPES database. This ensures the referral comes from a legitimate healthcare provider.
  - Use the tool when you have the provider's first and last name
  - **EXTRACT NPIs FROM TEXT**: Look for NPI numbers in the message (patterns like "NPI 1234567890", "NPI: 1234567890", or "NPI#1234567890")
  - **NPI VALIDATION**: If an NPI is mentioned in the text, extract it and include it in the tool call for verification
  - **EXAMPLES**:
    - "Dr. Sarah Johnson, NPI 1234567890" → Call tool with npi="1234567890"
    - "Referring physician: Dr. Smith (NPI: 9876543210)" → Call tool with npi="9876543210"
  - **TOOL RESPONSE HANDLING**:
    * If tool returns "not_found" status: Ask for clarification (spelling, NPI, location)
    * If tool returns "error" status: Ask for alternative provider information 
    * If tool returns "npi_mismatch" status: The provided NPI doesn't match - ask for correct NPI or ask the user to specify the provider
    * If the tool returns multiple providers less than or equal to 3, show the actual options with their real details and ask the user to pick a provider by providing the details of all the results
    * If the tool returns too many results greater than 3, ask for the provider's city and state to narrow the search. If the results are still too many, ask the user to pick a provider by providing the details of the narrowed results
    * **CRITICAL**: Always use the EXACT data returned by the tool - never make up provider details
  
TOOL USAGE REQUIREMENTS:
- Present the actual provider information from the tool response (real NPIs, names, locations, credentials)
- Use tools naturally as part of the conversation flow
- **NEVER fabricate or guess provider information**
- **ALWAYS use the exact provider data returned by the verification tool**
- **Present real NPIs, names, cities, states, and credentials from the tool response**
- **MANDATORY NPI VALIDATION**: When NPI is provided, include it in tool call and if mismatch ask for clarification

REFERRAL FAILURE THRESHOLDS:
- After 10 conversation turns without completion, use task_state: "failed" by deferring to Dr Walter and end the conversation
- Emergency cases immediately use task_state: "failed" and end the conversation
- If the user is not okay with the appointment time slots that are available, you should defer to Dr Walter and end the conversation with task_state: "failed"
- Out of context conversations immediately use task_state: "failed" and end the conversation
- Any suspicious activity immediately use task_state: "failed" and end the conversation
- If the information provided is not good enough to process the referral, use task_state: "failed" by deferring to Dr Walter and end the conversation


IMPORTANT: You MUST respond with valid JSON using exactly one of the three task_state values: "input_required", "completed", or "failed"."""

    def _analyze_referral_progress(self, conversation_history: List) -> str:
        """Analyze conversation history to understand referral completion status."""
        
        # Handle empty conversation history
        if not conversation_history:
            return "INFORMATION COLLECTED SO FAR: None yet - this is a new conversation\nSTILL NEEDED: All required information"
        
        # Extract all user messages to analyze collected information
        user_messages = []
        for msg in conversation_history:
            if hasattr(msg, 'role') and msg.role == "user":
                if hasattr(msg, 'parts') and msg.parts:
                    for part in msg.parts:
                        if hasattr(part, 'root') and hasattr(part.root, 'text'):
                            user_messages.append(part.root.text)
        
        all_user_text = " ".join(user_messages).lower()
        
        # Simple analysis of what information might be present
        collected_info = []
        missing_info = []
        
        # Check for patient information
        if any(keyword in all_user_text for keyword in ["patient", "name", "john", "jane", "dob", "birth", "mrn"]):
            collected_info.append("Patient information (partial or complete)")
        else:
            missing_info.append("Patient information")
        
        # Check for provider information  
        if any(keyword in all_user_text for keyword in ["doctor", "dr.", "physician", "provider", "npi"]):
            collected_info.append("Provider information (partial or complete)")
        else:
            missing_info.append("Provider information")
            
        # Check for clinical information
        if any(keyword in all_user_text for keyword in ["chest pain", "arrhythmia", "symptoms", "condition", "history"]):
            collected_info.append("Clinical information (partial or complete)")
        else:
            missing_info.append("Clinical information")
            
        # Check for insurance
        if any(keyword in all_user_text for keyword in ["insurance", "aetna", "blue cross", "united", "cigna"]):
            collected_info.append("Insurance information (partial or complete)")
        else:
            missing_info.append("Insurance information")
        
        context = f"INFORMATION COLLECTED SO FAR: {collected_info if collected_info else 'None yet'}\n"
        context += f"STILL NEEDED: {missing_info if missing_info else 'All required information appears to be collected'}"
        
        return context

    def _build_claude_conversation(self, conversation_history: List) -> List[dict]:
        """Convert A2A conversation history to Claude API format."""
        claude_messages = []
        
        for msg in conversation_history:
            if hasattr(msg, 'role') and hasattr(msg, 'parts'):
                # Extract text from message parts
                text_content = ""
                for part in msg.parts:
                    if hasattr(part, 'root') and hasattr(part.root, 'text'):
                        text_content += part.root.text
                
                if text_content.strip():
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
        import json
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
                if not response_text.strip():
                    logger.error(f"Empty response text from Claude API")
                    raise json.JSONDecodeError("Empty response", "", 0)
                    
                logger.debug(f"Parsing Claude response: {response_text[:200]}...")
                
                # Handle Claude 4 Sonnet markdown code blocks
                clean_response = response_text.strip()
                if clean_response.startswith('```json') and clean_response.endswith('```'):
                    # Extract JSON from markdown code block
                    clean_response = clean_response[7:-3].strip()  # Remove ```json and ```
                elif clean_response.startswith('```') and clean_response.endswith('```'):
                    # Extract content from any code block
                    clean_response = clean_response[3:-3].strip()
                
                response_data = json.loads(clean_response)
                task_state = response_data.get("task_state")
                clean_text = response_data.get("response_text", response_text)
                
                if task_state == "input_required":
                    yield {
                        'is_task_complete': False,
                        'require_user_input': True,
                        'content': clean_text
                    }
                elif task_state == "completed":
                    yield {
                        'is_task_complete': True,
                        'require_user_input': False,
                        'content': clean_text
                    }
                else:  # failed
                    yield {
                        'is_task_complete': False,
                        'require_user_input': True,
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
