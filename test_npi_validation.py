#!/usr/bin/env python3
"""
Test Strict NPI Validation

This test validates that the agent properly validates NPIs and fails referrals 
when fake NPIs are provided with real provider names.
"""

import asyncio
import httpx
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

class NPIValidationTest:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def close(self):
        await self.client.aclose()
        
    async def send_message(self, message_content: str, task_id: str = None, context_id: str = None):
        """Send message using proper A2A format"""
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
        params["configuration"] = {"blocking": True}
        
        request_data = {
            "jsonrpc": "2.0",
            "method": "message/send",
            "id": str(uuid.uuid4()),
            "params": params
        }
        
        response = await self.client.post(BASE_URL, json=request_data)
        response.raise_for_status()
        return response.json()
        
    async def test_npi_validation(self):
        """Test strict NPI validation scenarios"""
        
        print("🧪 Testing Strict NPI Validation")
        print("=" * 60)
        
        test_cases = [
            {
                "name": "Fake NPI with Real Provider Name",
                "message": "Referral from Dr. Sarah Johnson, NPI 1234567890",
                "expected": "Should FAIL due to NPI mismatch"
            },
            {
                "name": "Real Provider with Valid NPI",
                "message": "Referral from Dr. Joshua Mandel, NPI 1659411569", 
                "expected": "Should PASS with exact provider match"
            },
            {
                "name": "Provider Name Only (No NPI)",
                "message": "Referral from Dr. Josh Mandel",
                "expected": "Should work normally without NPI validation"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📋 Test {i}: {test_case['name']}")
            print(f"Expected: {test_case['expected']}")
            
            try:
                response = await self.send_message(test_case["message"])
                result = response.get("result", {})
                
                # Extract agent response
                status_message = result.get("status", {}).get("message", {})
                if status_message:
                    agent_parts = status_message.get("parts", [])
                    if agent_parts and agent_parts[0].get("kind") == "text":
                        agent_text = agent_parts[0].get("text", "")
                        
                        # Check final state
                        final_state = result.get("status", {}).get("state")
                        
                        print(f"✅ Final State: {final_state}")
                        print(f"✅ Agent Response:")
                        print(f"   {agent_text[:400]}...")
                        
                        # Analyze results
                        if test_case["name"] == "Fake NPI with Real Provider Name":
                            if final_state == "failed" or "mismatch" in agent_text.lower() or "invalid" in agent_text.lower():
                                print(f"   ✅ CORRECT: Agent properly rejected fake NPI")
                            else:
                                print(f"   ❌ PROBLEM: Agent should have failed but didn't!")
                                
                        elif test_case["name"] == "Real Provider with Valid NPI":
                            if "joshua" in agent_text.lower() and "1659411569" in agent_text:
                                print(f"   ✅ CORRECT: Agent found exact NPI match")
                            else:
                                print(f"   ❓ Unclear: Could not verify exact NPI match")
                                
                    else:
                        print("   ❌ No agent text response found")
                else:
                    print("   ❌ No status message found")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
                
            print("-" * 60)
            
        print(f"\n🎯 NPI validation testing complete!")
        
async def main():
    test = NPIValidationTest()
    try:
        await test.test_npi_validation()
    finally:
        await test.close()

if __name__ == "__main__":
    asyncio.run(main())