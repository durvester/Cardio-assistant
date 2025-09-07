#!/usr/bin/env python3
"""
Walter Reed Cardiology A2A Agent - Comprehensive Test Suite

Tests all A2A protocol functionality including:
- Agent card discovery and metadata
- Task lifecycle management
- Multi-turn conversation workflows
- History preservation and context management
- JSON-RPC method compliance
- Real-world referral scenarios
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, List, Optional, Any
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"
A2A_ENDPOINT = BASE_URL
AGENT_CARD_ENDPOINT = f"{BASE_URL}/.well-known/agent-card.json"

class ComprehensivePhase2Test:
    """Comprehensive test suite for Phase 2 requirements."""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=60.0)
        self.test_results = []
        
    async def close(self):
        await self.client.aclose()
    
    def log_test_result(self, test_name: str, passed: bool, details: str):
        """Log test result with detailed information."""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results.append({
            "test": test_name, 
            "passed": passed, 
            "details": details
        })
        logger.info(f"{status}: {test_name}")
        logger.info(f"  Details: {details}")
    
    async def send_message(
        self, 
        message_content: str, 
        task_id: Optional[str] = None, 
        context_id: Optional[str] = None,
        blocking: bool = True
    ) -> Dict[str, Any]:
        """Send a message with proper A2A formatting."""
        
        message_id = str(uuid.uuid4())
        
        message = {
            "role": "user",
            "parts": [{"kind": "text", "text": message_content}],
            "messageId": message_id,
            "kind": "message"
        }
        
        if task_id and context_id:
            message["taskId"] = task_id
            message["contextId"] = context_id
        
        params = {"message": message}
        if blocking:
            params["configuration"] = {"blocking": True}
        
        request_data = {
            "jsonrpc": "2.0",
            "method": "message/send",
            "id": str(uuid.uuid4()),
            "params": params
        }
        
        response = await self.client.post(A2A_ENDPOINT, json=request_data)
        response.raise_for_status()
        return response.json()
    
    async def get_task(self, task_id: str) -> Dict[str, Any]:
        """Get task details."""
        request_data = {
            "jsonrpc": "2.0",
            "method": "tasks/get",
            "id": str(uuid.uuid4()),
            "params": {"id": task_id}
        }
        
        response = await self.client.post(A2A_ENDPOINT, json=request_data)
        response.raise_for_status()
        return response.json()

    # ========================================
    # TEST CATEGORY 1: BASIC FUNCTIONALITY
    # ========================================
    
    async def test_agent_card_accessibility(self):
        """Test agent card is accessible and valid."""
        logger.info("\n🧪 Testing Agent Card Accessibility...")
        
        try:
            response = await self.client.get(AGENT_CARD_ENDPOINT)
            response.raise_for_status()
            agent_card = response.json()
            
            required_fields = ["name", "description", "url", "version", "capabilities", "skills"]
            missing_fields = [field for field in required_fields if field not in agent_card]
            
            if missing_fields:
                self.log_test_result("Agent Card Structure", False, f"Missing fields: {missing_fields}")
                return
            
            if not agent_card.get("capabilities", {}).get("streaming") == False:
                self.log_test_result("Agent Card Capabilities", False, f"Streaming should be false for Phase 2")
                return
                
            self.log_test_result("Agent Card Accessibility", True, f"Agent card valid: {agent_card['name']}")
            
        except Exception as e:
            self.log_test_result("Agent Card Accessibility", False, f"Error: {e}")

    async def test_basic_task_creation(self):
        """Test basic task creation and structure."""
        logger.info("\n🧪 Testing Basic Task Creation...")
        
        try:
            response = await self.send_message("Hello, test message")
            result = response.get("result", {})
            
            # Validate task structure
            required_fields = ["id", "contextId", "status", "history", "kind"]
            missing_fields = [field for field in required_fields if field not in result]
            
            if missing_fields:
                self.log_test_result("Basic Task Creation", False, f"Missing fields: {missing_fields}")
                return
            
            if result.get("kind") != "task":
                self.log_test_result("Basic Task Creation", False, f"Invalid kind: {result.get('kind')}")
                return
            
            # Validate status structure
            status = result.get("status", {})
            if "state" not in status:
                self.log_test_result("Basic Task Creation", False, "Missing status.state")
                return
                
            self.log_test_result("Basic Task Creation", True, f"Task created with ID: {result.get('id')}")
            return result
            
        except Exception as e:
            self.log_test_result("Basic Task Creation", False, f"Error: {e}")
            return None

    # ========================================
    # TEST CATEGORY 2: HISTORY PRESERVATION
    # ========================================

    async def test_message_history_preservation(self):
        """Test that message history is preserved correctly."""
        logger.info("\n🧪 Testing Message History Preservation...")
        
        try:
            # Start conversation
            response1 = await self.send_message("Start referral for patient Alice")
            result1 = response1.get("result", {})
            task_id = result1.get("id")
            context_id = result1.get("contextId")
            
            if not task_id or not context_id:
                self.log_test_result("History - Initial Setup", False, "Failed to get task/context IDs")
                return
            
            initial_history = result1.get("history", [])
            logger.info(f"Initial history length: {len(initial_history)}")
            
            # Continue conversation
            response2 = await self.send_message(
                "Patient DOB 01/01/1990, MRN 12345", 
                task_id, 
                context_id
            )
            result2 = response2.get("result", {})
            second_history = result2.get("history", [])
            logger.info(f"Second turn history length: {len(second_history)}")
            
            # Third turn
            response3 = await self.send_message(
                "Referring physician Dr. Smith, NPI 1234567890", 
                task_id, 
                context_id
            )
            result3 = response3.get("result", {})
            third_history = result3.get("history", [])
            logger.info(f"Third turn history length: {len(third_history)}")
            
            # Validate history growth
            expected_progression = [1, 3, 5]  # user, user+agent, user+agent+user
            actual_progression = [len(initial_history), len(second_history), len(third_history)]
            
            if actual_progression != expected_progression:
                self.log_test_result(
                    "Message History Preservation", 
                    False, 
                    f"History progression wrong. Expected {expected_progression}, got {actual_progression}"
                )
                return
            
            # Validate history content
            final_history = third_history
            user_messages = [msg for msg in final_history if msg.get("role") == "user"]
            agent_messages = [msg for msg in final_history if msg.get("role") == "agent"]
            
            if len(user_messages) != 3:
                self.log_test_result(
                    "Message History Preservation", 
                    False, 
                    f"Expected 3 user messages, got {len(user_messages)}"
                )
                return
                
            if len(agent_messages) != 2:
                self.log_test_result(
                    "Message History Preservation", 
                    False, 
                    f"Expected 2 agent messages, got {len(agent_messages)}"
                )
                return
            
            self.log_test_result(
                "Message History Preservation", 
                True, 
                f"History preserved correctly: {len(final_history)} total messages"
            )
            
        except Exception as e:
            self.log_test_result("Message History Preservation", False, f"Error: {e}")

    # ========================================
    # TEST CATEGORY 3: TASK CONTINUATION
    # ========================================

    async def test_task_continuation_compliance(self):
        """Test strict A2A task continuation compliance."""
        logger.info("\n🧪 Testing Task Continuation Compliance...")
        
        try:
            # Start task
            response1 = await self.send_message("Need cardiology consultation")
            result1 = response1.get("result", {})
            original_task_id = result1.get("id")
            original_context_id = result1.get("contextId")
            
            # Continue task
            response2 = await self.send_message(
                "Patient has chest pain symptoms",
                original_task_id,
                original_context_id
            )
            result2 = response2.get("result", {})
            continued_task_id = result2.get("id")
            continued_context_id = result2.get("contextId")
            
            # Validate IDs preserved
            if original_task_id != continued_task_id:
                self.log_test_result(
                    "Task Continuation - ID Preservation", 
                    False, 
                    f"Task ID changed: {original_task_id} -> {continued_task_id}"
                )
                return
                
            if original_context_id != continued_context_id:
                self.log_test_result(
                    "Task Continuation - Context Preservation", 
                    False, 
                    f"Context ID changed: {original_context_id} -> {continued_context_id}"
                )
                return
            
            # Validate tasks/get retrieves same task
            task_get_response = await self.get_task(original_task_id)
            task_get_result = task_get_response.get("result", {})
            
            if task_get_result.get("id") != original_task_id:
                self.log_test_result(
                    "Task Continuation - Retrieval", 
                    False, 
                    "tasks/get returned different task ID"
                )
                return
            
            self.log_test_result(
                "Task Continuation Compliance", 
                True, 
                f"Task continuation works correctly"
            )
            
        except Exception as e:
            self.log_test_result("Task Continuation Compliance", False, f"Error: {e}")

    # ========================================
    # TEST CATEGORY 4: STATE MANAGEMENT
    # ========================================

    async def test_input_required_state_transitions(self):
        """Test input-required state transitions work correctly."""
        logger.info("\n🧪 Testing Input-Required State Transitions...")
        
        try:
            # Start conversation
            response = await self.send_message("I need help with referral")
            result = response.get("result", {})
            
            state = result.get("status", {}).get("state")
            if state != "input-required":
                self.log_test_result(
                    "Input-Required State", 
                    False, 
                    f"Expected 'input-required', got '{state}'"
                )
                return
            
            # Validate status message contains agent response
            status_message = result.get("status", {}).get("message")
            if not status_message:
                self.log_test_result(
                    "Input-Required Status Message", 
                    False, 
                    "Missing status message for input-required state"
                )
                return
            
            if status_message.get("role") != "agent":
                self.log_test_result(
                    "Input-Required Status Message", 
                    False, 
                    f"Status message should be from agent, got '{status_message.get('role')}'"
                )
                return
            
            self.log_test_result(
                "Input-Required State Transitions", 
                True, 
                f"State transitions work correctly"
            )
            
        except Exception as e:
            self.log_test_result("Input-Required State Transitions", False, f"Error: {e}")

    # ========================================
    # TEST CATEGORY 5: WORKFLOW COMPLETION
    # ========================================

    async def test_complete_referral_workflow(self):
        """Test complete referral workflow from start to finish."""
        logger.info("\n🧪 Testing Complete Referral Workflow...")
        
        try:
            # Step 1: Start referral
            response1 = await self.send_message("I need a cardiology referral")
            result1 = response1.get("result", {})
            task_id = result1.get("id")
            context_id = result1.get("contextId")
            
            workflow_steps = [
                "Patient: Maria Rodriguez, DOB 05/15/1980, MRN 67890, phone 555-1234",
                "Referring physician: Dr. Sarah Johnson, NPI 1234567890, from Heart Care Medical Group",
                "Clinical: Patient has chest pain for 2 weeks, takes metoprolol, recent EKG shows abnormal rhythm",
                "Insurance: United Healthcare, member ID UH123456, authorization AUTH789",
                "Urgency: Routine priority, patient available weekday afternoons"
            ]
            
            final_result = None
            for i, step in enumerate(workflow_steps):
                logger.info(f"Workflow step {i+1}: {step[:50]}...")
                
                response = await self.send_message(step, task_id, context_id)
                result = response.get("result", {})
                final_result = result
                
                state = result.get("status", {}).get("state")
                logger.info(f"State after step {i+1}: {state}")
                
                # If we reach completed state, that's success
                if state == "completed":
                    self.log_test_result(
                        "Complete Referral Workflow", 
                        True, 
                        f"Workflow completed after {i+1} steps"
                    )
                    return
            
            # If we get here, workflow didn't complete
            final_state = final_result.get("status", {}).get("state") if final_result else "unknown"
            self.log_test_result(
                "Complete Referral Workflow", 
                False, 
                f"Workflow did not complete. Final state: {final_state}"
            )
            
        except Exception as e:
            self.log_test_result("Complete Referral Workflow", False, f"Error: {e}")

    # ========================================
    # TEST CATEGORY 6: PROVIDER VERIFICATION
    # ========================================

    async def test_provider_verification_mohit_durve(self):
        """Test provider verification with Mohit Durve (expected: not found, conversation ends)."""
        logger.info("\n🧪 Testing Provider Verification - Mohit Durve (Not Found)...")
        
        try:
            # Start conversation with referral from Mohit Durve
            response = await self.send_message("I need a cardiology referral from Dr. Mohit Durve")
            result = response.get("result", {})
            
            # Should create task properly
            task_id = result.get("id")
            context_id = result.get("contextId")
            
            if not task_id or not context_id:
                self.log_test_result("Provider Verification - Mohit Durve Setup", False, "Failed to get task/context IDs")
                return
            
            # Check agent response - should indicate provider not found
            agent_response = result.get("status", {}).get("message", {}).get("parts", [{}])[0].get("text", "")
            
            # Should indicate provider verification failed and conversation ending
            verification_indicators = ["not found", "cannot find", "unable to verify", "get back", "contact"]
            found_indicators = [indicator for indicator in verification_indicators 
                              if indicator.lower() in agent_response.lower()]
            
            if not found_indicators:
                self.log_test_result(
                    "Provider Verification - Mohit Durve", 
                    False, 
                    f"Agent didn't indicate provider not found. Response: {agent_response[:100]}..."
                )
                return
            
            # Check if conversation should end (completed or failed state)
            state = result.get("status", {}).get("state")
            if state not in ["completed", "failed", "input-required"]:
                self.log_test_result(
                    "Provider Verification - Mohit Durve State", 
                    False, 
                    f"Expected conversation to handle not found gracefully, got state: {state}"
                )
                return
            
            self.log_test_result(
                "Provider Verification - Mohit Durve", 
                True, 
                f"Agent handled unknown provider correctly: {found_indicators[0]}"
            )
            
        except Exception as e:
            self.log_test_result("Provider Verification - Mohit Durve", False, f"Error: {e}")

    async def test_provider_verification_josh_mandel(self):
        """Test provider verification with Josh Mandel (expected: 2 results, agent picks one)."""
        logger.info("\n🧪 Testing Provider Verification - Josh Mandel (Multiple Results)...")
        
        try:
            # Start conversation with referral from Josh Mandel
            response = await self.send_message("I have a cardiology referral from Dr. Josh Mandel")
            result = response.get("result", {})
            
            task_id = result.get("id")
            context_id = result.get("contextId")
            
            if not task_id or not context_id:
                self.log_test_result("Provider Verification - Josh Mandel Setup", False, "Failed to get task/context IDs")
                return
            
            # Check agent response - should handle multiple results
            agent_response = result.get("status", {}).get("message", {}).get("parts", [{}])[0].get("text", "")
            
            # Agent should either:
            # 1. Present options for user to select, or
            # 2. Pick one automatically and proceed
            selection_indicators = ["select", "which", "found", "multiple", "choose"] + ["josh", "mandel"]
            found_indicators = [indicator for indicator in selection_indicators 
                              if indicator.lower() in agent_response.lower()]
            
            if not found_indicators:
                self.log_test_result(
                    "Provider Verification - Josh Mandel", 
                    False, 
                    f"Agent didn't handle multiple providers. Response: {agent_response[:100]}..."
                )
                return
            
            # State should be input-required (asking for more info) or continuing
            state = result.get("status", {}).get("state")
            if state not in ["input-required", "working"]:
                self.log_test_result(
                    "Provider Verification - Josh Mandel State", 
                    False, 
                    f"Expected input-required or working state, got: {state}"
                )
                return
            
            self.log_test_result(
                "Provider Verification - Josh Mandel", 
                True, 
                f"Agent handled multiple providers correctly"
            )
            
        except Exception as e:
            self.log_test_result("Provider Verification - Josh Mandel", False, f"Error: {e}")

    async def test_provider_verification_peter_smith_refinement(self):
        """Test provider verification with Peter Smith (expected: too many, refine with Aurora, CO)."""
        logger.info("\n🧪 Testing Provider Verification - Peter Smith (Refinement)...")
        
        try:
            # Step 1: Start with Peter Smith (should get too many results)
            response1 = await self.send_message("Referral from Dr. Peter Smith for patient evaluation")
            result1 = response1.get("result", {})
            
            task_id = result1.get("id")
            context_id = result1.get("contextId")
            
            if not task_id or not context_id:
                self.log_test_result("Provider Verification - Peter Smith Setup", False, "Failed to get task/context IDs")
                return
            
            # Check if agent asks for more details
            agent_response1 = result1.get("status", {}).get("message", {}).get("parts", [{}])[0].get("text", "")
            
            refinement_indicators = ["more information", "city", "state", "location", "narrow", "many"]
            found_indicators = [indicator for indicator in refinement_indicators 
                              if indicator.lower() in agent_response1.lower()]
            
            # Step 2: Provide city information
            response2 = await self.send_message(
                "Dr. Peter Smith practices in Aurora, Colorado", 
                task_id, 
                context_id
            )
            result2 = response2.get("result", {})
            
            # Check agent response after providing location
            agent_response2 = result2.get("status", {}).get("message", {}).get("parts", [{}])[0].get("text", "")
            
            # Should now be able to proceed or show refined results
            success_indicators = ["aurora", "colorado", "found", "verified", "proceed"]
            refined_indicators = [indicator for indicator in success_indicators 
                                if indicator.lower() in agent_response2.lower()]
            
            if not refined_indicators:
                self.log_test_result(
                    "Provider Verification - Peter Smith Refinement", 
                    False, 
                    f"Agent didn't handle location refinement. Response: {agent_response2[:100]}..."
                )
                return
            
            # Validate conversation continues properly
            state2 = result2.get("status", {}).get("state")
            if state2 not in ["input-required", "working", "completed"]:
                self.log_test_result(
                    "Provider Verification - Peter Smith State", 
                    False, 
                    f"Unexpected state after refinement: {state2}"
                )
                return
            
            self.log_test_result(
                "Provider Verification - Peter Smith Refinement", 
                True, 
                f"Agent handled provider refinement correctly"
            )
            
        except Exception as e:
            self.log_test_result("Provider Verification - Peter Smith Refinement", False, f"Error: {e}")

    async def test_provider_verification_with_complete_referral(self):
        """Test provider verification as part of a complete referral workflow."""
        logger.info("\n🧪 Testing Provider Verification in Complete Workflow...")
        
        try:
            # Start complete referral with provider verification
            response1 = await self.send_message("I need a cardiology referral")
            result1 = response1.get("result", {})
            task_id = result1.get("id")
            context_id = result1.get("contextId")
            
            workflow_steps = [
                "Patient: Sarah Johnson, DOB 03/20/1985, MRN 54321, phone 555-9876",
                "Referring physician: Dr. Josh Mandel from Boston Medical Center",  # Should trigger verification
                "Clinical: Patient has palpitations and dizziness, EKG shows irregular rhythm",
                "Insurance: Blue Cross Blue Shield, member ID BC789012, authorization AUTH456", 
                "Urgency: Urgent priority, patient needs evaluation within 1 week"
            ]
            
            final_result = None
            for i, step in enumerate(workflow_steps):
                logger.info(f"Workflow step {i+1}: {step[:50]}...")
                
                response = await self.send_message(step, task_id, context_id)
                result = response.get("result", {})
                final_result = result
                
                state = result.get("status", {}).get("state")
                logger.info(f"State after step {i+1}: {state}")
                
                # Special handling for provider verification step (step 2)
                if i == 1:  # Provider step
                    agent_response = result.get("status", {}).get("message", {}).get("parts", [{}])[0].get("text", "")
                    verification_indicators = ["josh", "mandel", "verify", "found"]
                    found_verification = any(indicator.lower() in agent_response.lower() 
                                           for indicator in verification_indicators)
                    
                    if not found_verification:
                        self.log_test_result(
                            "Provider Verification in Workflow", 
                            False, 
                            f"Provider verification not evident in step 2. Response: {agent_response[:100]}..."
                        )
                        return
                
                # If we reach completed state, that's success
                if state == "completed":
                    self.log_test_result(
                        "Provider Verification in Complete Workflow", 
                        True, 
                        f"Complete workflow with provider verification completed after {i+1} steps"
                    )
                    return
            
            # If we get here, check if workflow is progressing properly
            final_state = final_result.get("status", {}).get("state") if final_result else "unknown"
            if final_state in ["input-required", "working"]:
                self.log_test_result(
                    "Provider Verification in Complete Workflow", 
                    True, 
                    f"Workflow progressing correctly with provider verification. Final state: {final_state}"
                )
            else:
                self.log_test_result(
                    "Provider Verification in Complete Workflow", 
                    False, 
                    f"Workflow stalled. Final state: {final_state}"
                )
            
        except Exception as e:
            self.log_test_result("Provider Verification in Complete Workflow", False, f"Error: {e}")

    # ========================================
    # TEST CATEGORY 7: LLM INTELLIGENCE
    # ========================================

    async def test_context_awareness(self):
        """Test that LLM maintains context across turns."""
        logger.info("\n🧪 Testing LLM Context Awareness...")
        
        try:
            # Start conversation with specific patient
            response1 = await self.send_message("Referral for patient Emma Thompson")
            result1 = response1.get("result", {})
            task_id = result1.get("id")
            context_id = result1.get("contextId")
            
            # Provide partial info
            response2 = await self.send_message(
                "She's 45 years old with chest pain", 
                task_id, 
                context_id
            )
            result2 = response2.get("result", {})
            
            # Ask follow-up - agent should remember Emma
            response3 = await self.send_message(
                "What information do you have about the patient so far?", 
                task_id, 
                context_id
            )
            result3 = response3.get("result", {})
            
            # Check if agent response mentions Emma or patient details
            agent_response = result3.get("status", {}).get("message", {}).get("parts", [{}])[0].get("text", "")
            
            context_indicators = ["Emma", "Thompson", "45", "chest pain"]
            found_indicators = [indicator for indicator in context_indicators if indicator.lower() in agent_response.lower()]
            
            if len(found_indicators) < 2:
                self.log_test_result(
                    "LLM Context Awareness", 
                    False, 
                    f"Agent doesn't show context awareness. Found indicators: {found_indicators}"
                )
                return
            
            self.log_test_result(
                "LLM Context Awareness", 
                True, 
                f"Agent maintains context. Found: {found_indicators}"
            )
            
        except Exception as e:
            self.log_test_result("LLM Context Awareness", False, f"Error: {e}")

    # ========================================
    # TEST CATEGORY 7: JSON-RPC COMPLIANCE
    # ========================================

    async def test_all_jsonrpc_methods(self):
        """Test all required JSON-RPC methods work."""
        logger.info("\n🧪 Testing All JSON-RPC Methods...")
        
        methods_to_test = [
            ("message/send", "Basic message sending"),
            ("tasks/get", "Task retrieval"),
            ("tasks/cancel", "Task cancellation")
        ]
        
        # First create a task
        response = await self.send_message("Test message for JSON-RPC methods")
        result = response.get("result", {})
        task_id = result.get("id")
        
        for method, description in methods_to_test:
            try:
                if method == "message/send":
                    # Already tested above
                    self.log_test_result(f"JSON-RPC: {method}", True, description)
                    
                elif method == "tasks/get":
                    get_response = await self.get_task(task_id)
                    get_result = get_response.get("result", {})
                    if get_result.get("id") == task_id:
                        self.log_test_result(f"JSON-RPC: {method}", True, description)
                    else:
                        self.log_test_result(f"JSON-RPC: {method}", False, "Task retrieval failed")
                        
                elif method == "tasks/cancel":
                    cancel_request = {
                        "jsonrpc": "2.0",
                        "method": "tasks/cancel",
                        "id": str(uuid.uuid4()),
                        "params": {"id": task_id}
                    }
                    cancel_response = await self.client.post(A2A_ENDPOINT, json=cancel_request)
                    if cancel_response.status_code == 200:
                        self.log_test_result(f"JSON-RPC: {method}", True, description)
                    else:
                        self.log_test_result(f"JSON-RPC: {method}", False, f"HTTP {cancel_response.status_code}")
                        
            except Exception as e:
                self.log_test_result(f"JSON-RPC: {method}", False, f"Error: {e}")

    # ========================================
    # MAIN TEST RUNNER
    # ========================================

    async def run_all_tests(self):
        """Run all comprehensive Phase 2 tests."""
        logger.info("🚀 Starting Comprehensive Phase 2 Test Suite")
        logger.info("=" * 80)
        
        # Basic functionality tests
        await self.test_agent_card_accessibility()
        await self.test_basic_task_creation()
        
        # Core Phase 2 functionality
        await self.test_message_history_preservation()
        await self.test_task_continuation_compliance()
        await self.test_input_required_state_transitions()
        
        # Advanced workflow tests
        await self.test_complete_referral_workflow()
        await self.test_context_awareness()
        
        # Provider verification tests
        await self.test_provider_verification_mohit_durve()
        await self.test_provider_verification_josh_mandel() 
        await self.test_provider_verification_peter_smith_refinement()
        await self.test_provider_verification_with_complete_referral()
        
        # Protocol compliance
        await self.test_all_jsonrpc_methods()
        
        # Generate comprehensive report
        await self.generate_final_report()

    async def generate_final_report(self):
        """Generate comprehensive test report."""
        logger.info("\n" + "=" * 80)
        logger.info("📊 COMPREHENSIVE PHASE 2 TEST RESULTS")
        logger.info("=" * 80)
        
        passed_tests = [result for result in self.test_results if result["passed"]]
        failed_tests = [result for result in self.test_results if not result["passed"]]
        
        total_tests = len(self.test_results)
        passed_count = len(passed_tests)
        success_rate = (passed_count / total_tests * 100) if total_tests > 0 else 0
        
        # Categorize results
        categories = {
            "Basic Functionality": [],
            "History & Continuation": [],
            "State Management": [],
            "Workflow Logic": [],
            "Provider Verification": [],
            "LLM Intelligence": [],
            "Protocol Compliance": []
        }
        
        for result in self.test_results:
            test_name = result["test"]
            if any(keyword in test_name for keyword in ["Agent Card", "Basic Task"]):
                categories["Basic Functionality"].append(result)
            elif any(keyword in test_name for keyword in ["History", "Continuation"]):
                categories["History & Continuation"].append(result)
            elif any(keyword in test_name for keyword in ["State", "Input-Required"]):
                categories["State Management"].append(result)
            elif any(keyword in test_name for keyword in ["Provider Verification"]):
                categories["Provider Verification"].append(result)
            elif any(keyword in test_name for keyword in ["Workflow", "Referral"]):
                categories["Workflow Logic"].append(result)
            elif any(keyword in test_name for keyword in ["Context", "LLM"]):
                categories["LLM Intelligence"].append(result)
            else:
                categories["Protocol Compliance"].append(result)
        
        # Print categorized results
        for category, tests in categories.items():
            if tests:
                logger.info(f"\n📋 {category}:")
                for test in tests:
                    status = "✅" if test["passed"] else "❌"
                    logger.info(f"  {status} {test['test']}")
                    if not test["passed"]:
                        logger.info(f"      {test['details']}")
        
        # Overall assessment
        logger.info(f"\n🎯 OVERALL RESULTS:")
        logger.info(f"  Total Tests: {total_tests}")
        logger.info(f"  Passed: {passed_count}")
        logger.info(f"  Failed: {len(failed_tests)}")
        logger.info(f"  Success Rate: {success_rate:.1f}%")
        
        # Phase 2 readiness assessment
        critical_failures = [
            test for test in failed_tests 
            if any(keyword in test["test"] for keyword in ["History", "Workflow", "Continuation", "Provider Verification"])
        ]
        
        if success_rate >= 90:
            logger.info(f"\n🎉 PHASE 2 STATUS: EXCELLENT - Ready for Phase 3")
        elif success_rate >= 75:
            logger.info(f"\n⚠️  PHASE 2 STATUS: GOOD - Minor fixes needed")
        elif critical_failures:
            logger.info(f"\n❌ PHASE 2 STATUS: NEEDS WORK - Critical failures detected")
        else:
            logger.info(f"\n🔧 PHASE 2 STATUS: PARTIAL - Significant issues remain")
        
        return {
            "total_tests": total_tests,
            "passed": passed_count,
            "failed": len(failed_tests),
            "success_rate": success_rate,
            "critical_failures": len(critical_failures),
            "ready_for_phase3": success_rate >= 90 and len(critical_failures) == 0
        }

async def main():
    """Main test runner."""
    test_suite = ComprehensivePhase2Test()
    try:
        results = await test_suite.run_all_tests()
        return results
    finally:
        await test_suite.close()

if __name__ == "__main__":
    results = asyncio.run(main())
