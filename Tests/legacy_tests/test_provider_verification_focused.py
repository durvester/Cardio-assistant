#!/usr/bin/env python3
"""
Focused Provider Verification Test

Simple test to validate provider verification scenarios without hallucination:
- Mohit Durve: Expected 0 results 
- Josh Mandel: Expected 2 results
- Peter Smith: Expected >3 results requiring refinement
"""

import asyncio
import httpx
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

class ProviderVerificationTest:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def close(self):
        await self.client.aclose()
        
    async def send_message(self, message_content: str, task_id: str = None, context_id: str = None):
        """Send message using proper A2A format from test_a2a_agent.py"""
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
        
    async def test_provider_scenarios(self):
        """Test the three provider verification scenarios"""
        
        providers = [
            ("Mohit Durve", "Should return 0 results"),
            ("Josh Mandel", "Should return 2 results"),
            ("Peter Smith", "Should return >3 results")
        ]
        
        print("🧪 Provider Verification Tests")
        print("=" * 50)
        
        for provider, expected in providers:
            print(f"\n📋 Testing: {provider} ({expected})")
            
            try:
                response = await self.send_message(f"I need a referral from Dr. {provider}")
                result = response.get("result", {})
                
                # Extract agent response from status message
                status_message = result.get("status", {}).get("message", {})
                if status_message:
                    agent_parts = status_message.get("parts", [])
                    if agent_parts and agent_parts[0].get("kind") == "text":
                        agent_text = agent_parts[0].get("text", "")
                        print(f"✅ Agent Response:")
                        print(f"   {agent_text[:300]}...")
                        
                        # Check for hallucination in Josh Mandel case
                        if provider == "Josh Mandel":
                            fake_indicators = ["1234567890", "Boston, MA", "Cambridge, MA"]
                            real_indicators = ["1659411569", "1154612372", "NEW YORK", "SAFETY HARBOR"]
                            
                            has_fake = any(fake in agent_text for fake in fake_indicators)
                            has_real = any(real in agent_text for real in real_indicators)
                            
                            if has_fake:
                                print("   ❌ HALLUCINATION DETECTED - Using fake provider data!")
                            elif has_real:
                                print("   ✅ Using real NPPES data")
                            else:
                                print("   ❓ Cannot determine if real data used")
                    else:
                        print("   ❌ No agent text response found")
                else:
                    print("   ❌ No status message found")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
                
            print("-" * 50)
            
        # Test Peter Smith refinement scenario
        await self.test_peter_smith_refinement()
        
    async def test_peter_smith_refinement(self):
        """Test Peter Smith location refinement"""
        print(f"\n📋 Testing: Peter Smith Refinement")
        
        try:
            # Initial request
            response1 = await self.send_message("Referral from Dr. Peter Smith")
            result1 = response1.get("result", {})
            
            task_id = result1.get("id")
            context_id = result1.get("contextId")
            
            if task_id and context_id:
                # Follow-up with location
                response2 = await self.send_message(
                    "Dr. Peter Smith practices in Aurora, Colorado",
                    task_id, 
                    context_id
                )
                result2 = response2.get("result", {})
                
                # Extract agent response
                status_message = result2.get("status", {}).get("message", {})
                if status_message:
                    agent_parts = status_message.get("parts", [])
                    if agent_parts and agent_parts[0].get("kind") == "text":
                        agent_text = agent_parts[0].get("text", "")
                        print(f"✅ Refinement Response:")
                        print(f"   {agent_text[:300]}...")
                        
                        # Check final state
                        final_state = result2.get("status", {}).get("state")
                        print(f"   Final State: {final_state}")
                    else:
                        print("   ❌ No refinement response found")
                else:
                    print("   ❌ No refinement status message")
            else:
                print("   ❌ Failed to get task/context IDs for continuation")
                
        except Exception as e:
            print(f"   ❌ Refinement Error: {e}")
            
        print("-" * 50)
        
async def main():
    test = ProviderVerificationTest()
    try:
        await test.test_provider_scenarios()
        print("\n🎯 Provider verification testing complete!")
    finally:
        await test.close()

if __name__ == "__main__":
    asyncio.run(main())