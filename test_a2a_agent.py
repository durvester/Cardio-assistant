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
    # TEST CATEGORY 6: LLM INTELLIGENCE
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
            if any(keyword in test["test"] for keyword in ["History", "Workflow", "Continuation"])
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
