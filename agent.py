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
                        }
                    },
                    "required": ["first_name", "last_name"]
                }
            }
        ]
    
    async def process_message(self, message_text: str, conversation_history: Optional[List] = None) -> str:
        """
        Process an incoming message using Claude API.
        
        Args:
            message_text: The user's message
            conversation_history: Optional conversation history for multi-turn conversations
            
        Returns:
            Agent's response text
        """
        try:
            logger.info(f"Processing message: {message_text[:100]}...")
            
            # Always use multi-turn processing for cleaner, unified logic
            # If conversation_history is None, treat as empty list (new conversation)
            history = conversation_history if conversation_history is not None else []
            return await self._process_multi_turn(message_text, history)
            
        except Exception as e:
            logger.error(f"Error processing message with Claude API: {e}")
            return self._get_error_response()


    async def _process_multi_turn(self, message_text: str, conversation_history: List) -> str:
        """Process message in multi-turn mode with conversation context and tool support."""
        
        # Build multi-turn system prompt with conversation context
        multi_turn_prompt = self._build_multi_turn_system_prompt(conversation_history)
        
        # Create Claude conversation with full history
        claude_messages = self._build_claude_conversation(conversation_history)
        
        # Add current user message
        claude_messages.append({
            "role": "user",
            "content": message_text
        })
        
        # Make initial request to Claude with tools available
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=1200,
            temperature=0.7,
            system=multi_turn_prompt,
            tools=self.tools,  # Include tools for function calling
            messages=claude_messages
        )
        
        # Handle tool use if Claude wants to call tools
        if response.stop_reason == "tool_use":
            return await self._handle_tool_use(response, claude_messages, multi_turn_prompt)
        
        # Extract text from regular response
        response_text = ""
        for content in response.content:
            if content.type == "text":
                response_text += content.text
        
        logger.info(f"Generated multi-turn response: {response_text[:100]}...")
        return response_text

    async def _handle_tool_use(self, initial_response, claude_messages: List, system_prompt: str) -> str:
        """Handle tool use requests from Claude and return final response."""
        
        # Add Claude's tool use message to conversation
        assistant_content = []
        tool_calls = []
        
        for content in initial_response.content:
            if content.type == "text":
                assistant_content.append({
                    "type": "text",
                    "text": content.text
                })
            elif content.type == "tool_use":
                assistant_content.append({
                    "type": "tool_use",
                    "id": content.id,
                    "name": content.name,
                    "input": content.input
                })
                tool_calls.append({
                    "id": content.id,
                    "name": content.name,
                    "input": content.input
                })
        
        claude_messages.append({
            "role": "assistant",
            "content": assistant_content
        })
        
        # Execute tools and collect results
        tool_results = []
        for tool_call in tool_calls:
            try:
                result = await self._execute_tool(tool_call["name"], tool_call["input"])
                tool_results.append({
                    "type": "tool_result", 
                    "tool_use_id": tool_call["id"],
                    "content": str(result) if not isinstance(result, str) else result
                })
                logger.info(f"Executed tool {tool_call['name']} successfully")
            except Exception as e:
                logger.error(f"Tool execution failed for {tool_call['name']}: {e}")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_call["id"], 
                    "content": f"Tool execution failed: {str(e)}"
                })
        
        # Add tool results to conversation
        claude_messages.append({
            "role": "user",
            "content": tool_results
        })
        
        # Get Claude's final response
        final_response = await self.client.messages.create(
            model=self.model,
            max_tokens=1200,
            temperature=0.7,
            system=system_prompt,
            tools=self.tools,
            messages=claude_messages
        )
        
        # Extract final response text
        final_text = ""
        for content in final_response.content:
            if content.type == "text":
                final_text += content.text
        
        logger.info(f"Generated tool-assisted response: {final_text[:100]}...")
        return final_text

    async def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool by name with given input."""
        if tool_name == "verify_provider_nppes":
            return await verify_provider_nppes(
                first_name=tool_input["first_name"],
                last_name=tool_input["last_name"],
                city=tool_input.get("city"),
                state=tool_input.get("state")
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
HANDLING NEW CONVERSATIONS:
- For simple questions or quick inquiries, provide helpful information and mark as [REFERRAL_COMPLETE]
- For full referral requests, begin the comprehensive information collection process
- Adapt your response based on the complexity and completeness of the initial request
- Always provide appropriate next steps
"""
        
        return f"""You are Dr. Walter Reed's Cardiology Referral Agent, specializing in processing new patient cardiology referrals for Dr. Walter Reed's clinic in Manhattan.
{conversation_guidance}

MISSION: Guide users through a complete cardiology referral process via intelligent conversation, ultimately scheduling an appointment with Dr. Reed.

COMPLETE REFERRAL WORKFLOW:
You must collect ALL required information before completing the referral and scheduling an appointment.

REQUIRED INFORMATION (ALL MANDATORY):
1. PATIENT DETAILS:
   - Full legal name
   - Date of birth (MM/DD/YYYY format)
   - Medical Record Number (MRN)
   - Contact phone number

2. REFERRING PROVIDER:
   - Physician full name (first and last name - REQUIRED for verification)
   - NPI (National Provider Identifier) number (optional but preferred)
   - Practice/organization name
   - Contact information
   - City and state (if needed to narrow provider search)

3. CLINICAL INFORMATION:
   - Primary cardiac complaint/reason for referral
   - Relevant cardiac history
   - Current cardiac medications
   - Recent test results (EKG, echo, stress test, labs)
   - Symptom duration and severity

4. INSURANCE & AUTHORIZATION:
   - Insurance provider name
   - Member ID and group number
   - Authorization number (if pre-auth required)
   - Verify coverage for cardiology consultation

5. URGENCY & SCHEDULING:
   - Urgency level (emergent, urgent, routine)
   - Preferred appointment timing
   - Any scheduling constraints

CONVERSATION CONTEXT:
{referral_context}

APPOINTMENT SCHEDULING:
Dr. Reed's available appointment slots:
- Monday & Thursday: 11:00 AM - 3:00 PM
- Urgent cases: Same-day or next-day slots available
- Emergent cases: Immediate evaluation arranged

STATE CONTROL MARKERS:
Use these exact markers to control conversation flow:

**[NEED_MORE_INFO]** - When missing required information
Example: "I need the patient's insurance details. [NEED_MORE_INFO] What is their insurance provider and member ID?"

**[REFERRAL_COMPLETE]** - When ALL information collected and appointment scheduled
Example: "Excellent! I have all required information. [REFERRAL_COMPLETE] Your cardiology referral for [patient name] has been processed. I've scheduled an appointment with Dr. Reed on [date] at [time]. Confirmation details will be sent to the referring provider and patient."

**[REFERRAL_FAILED]** - If error, invalid info, or cannot proceed
Example: "I cannot process this referral due to invalid NPI number. [REFERRAL_FAILED] Please provide a valid 10-digit NPI for the referring physician."

CONVERSATION STRATEGY:
- Review conversation history to avoid asking for information already provided
- Ask for 1-2 specific items at a time (don't overwhelm)
- Follow logical order: Patient → Provider → Clinical → Insurance → Scheduling
- Explain why each piece of information is needed
- Be warm, professional, and efficient
- For urgent/emergent cases, prioritize appropriately
- When complete, confirm all details and provide specific appointment time

AVAILABLE TOOLS:
You have access to tools that can help verify information during the referral process:

- **Provider Verification**: When you receive a referring provider's name, use the provider verification tool to validate their credentials in the NPPES database. This ensures the referral comes from a legitimate healthcare provider.
  - Use the tool when you have the provider's first and last name
  - If you get too many results, ask for the provider's city and state to narrow the search
  - **CRITICAL**: Always use the EXACT data returned by the tool - never make up provider details
  - Present the actual provider information from the tool response (real NPIs, names, locations, credentials)
  - Handle different scenarios appropriately (no results, multiple options, inactive providers)

TOOL USAGE REQUIREMENTS:
- **NEVER fabricate or guess provider information**
- **ALWAYS use the exact provider data returned by the verification tool**
- **Present real NPIs, names, cities, states, and credentials from the tool response**
- If the tool returns multiple providers, show the actual options with their real details
- Use tools naturally as part of the conversation flow

QUALITY STANDARDS:
- Verify critical information (spelling of names, dates, numbers)
- Ensure clinical appropriateness of referral
- Confirm insurance coverage and authorization requirements
- Provide clear next steps and contact information

IMPORTANT: You MUST include exactly ONE state control marker ([NEED_MORE_INFO], [REFERRAL_COMPLETE], or [REFERRAL_FAILED]) in every response."""

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
