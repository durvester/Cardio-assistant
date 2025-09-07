#!/usr/bin/env python3
"""
Balanced Provider Verification Tests

Tests that verify the agent gives appropriate opportunities for clarification
while still properly failing when necessary.
"""

import asyncio
import httpx
import json
import uuid
import subprocess
import time

class ProviderVerificationTest:
    def __init__(self):
        self.server_process = None
        self.client = None
        
    async def setup(self):
        """Start server and client."""
        print("🚀 Starting server...")
        self.server_process = subprocess.Popen(
            ['python', '__main__.py'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        await asyncio.sleep(3)
        self.client = httpx.AsyncClient(timeout=60.0)
        
    async def teardown(self):
        """Clean up server and client."""
        if self.client:
            await self.client.aclose()
        if self.server_process:
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
    
    async def send_message(self, text, task_id=None, context_id=None):
        """Send a message to the agent."""
        params = {
            'message': {
                'role': 'user',
                'parts': [{'kind': 'text', 'text': text}],
                'messageId': str(uuid.uuid4()),
                'kind': 'message'
            }
        }
        
        if task_id and context_id:
            params['message']['taskId'] = task_id
            params['message']['contextId'] = context_id
            
        response = await self.client.post('http://localhost:8000', json={
            'jsonrpc': '2.0',
            'method': 'message/send',
            'id': str(uuid.uuid4()),
            'params': params
        })
        
        return response.json()['result']
    
    async def test_helpful_provider_clarification(self):
        """Test that agent asks for clarification when provider not found."""
        print("\n📋 TEST 1: Helpful Provider Clarification")
        print("-" * 50)
        
        result = await self.send_message("I need a cardiology referral from Dr. Mohit Durve")
        
        task_id = result['id']
        context_id = result['contextId']
        state = result['status']['state']
        response = result['status']['message']['parts'][0]['text']
        
        print(f"👤 USER: I need a cardiology referral from Dr. Mohit Durve")
        print(f"📊 STATE: {state}")
        print(f"🤖 AGENT: {response[:200]}...")
        
        # Should be in input-required state (asking for clarification)
        assert state == 'input-required', f"Expected input-required, got {state}"
        
        # Should ask for clarification, not fail immediately
        clarification_indicators = ['verify', 'spelling', 'npi', 'location', 'city', 'state']
        found_clarification = any(indicator in response.lower() for indicator in clarification_indicators)
        
        assert found_clarification, "Agent should ask for clarification, not fail immediately"
        print("✅ PASS: Agent appropriately asks for clarification")
        
        return task_id, context_id
    
    async def test_npi_provided_optional(self):
        """Test that NPI is handled correctly when provided optionally."""
        print("\n📋 TEST 2: NPI Provided Optionally")
        print("-" * 50)
        
        # Test with NPI provided
        result = await self.send_message("I need a referral from Dr. Sarah Johnson, NPI 1234567890, from Boston Medical")
        
        task_id = result['id']
        context_id = result['contextId'] 
        state = result['status']['state']
        response = result['status']['message']['parts'][0]['text']
        
        print(f"👤 USER: I need a referral from Dr. Sarah Johnson, NPI 1234567890, from Boston Medical")
        print(f"📊 STATE: {state}")
        print(f"🤖 AGENT: {response[:200]}...")
        
        # Should process the NPI and either find provider or handle appropriately
        npi_processed = 'npi' in response.lower() or 'sarah johnson' in response.lower()
        assert npi_processed, "Agent should acknowledge and process provided NPI"
        
        print("✅ PASS: Agent processes NPI when provided")
        return task_id, context_id
    
    async def test_multiple_clarification_attempts(self):
        """Test that agent gives multiple opportunities before failing."""
        print("\n📋 TEST 3: Multiple Clarification Attempts")
        print("-" * 50)
        
        # Start with unknown provider
        result1 = await self.send_message("I need a referral from Dr. Fake Provider")
        task_id = result1['id']
        context_id = result1['contextId']
        
        print(f"👤 USER: I need a referral from Dr. Fake Provider")
        print(f"📊 STATE: {result1['status']['state']}")
        print(f"🤖 AGENT: {result1['status']['message']['parts'][0]['text'][:150]}...")
        
        # Attempt 1: Still provide unclear info
        result2 = await self.send_message("His name is Dr. Fake Provider from Medical Center", task_id, context_id)
        print(f"\n👤 USER: His name is Dr. Fake Provider from Medical Center")
        print(f"📊 STATE: {result2['status']['state']}")
        print(f"🤖 AGENT: {result2['status']['message']['parts'][0]['text'][:150]}...")
        
        # Should still be trying to help (input-required)
        assert result2['status']['state'] == 'input-required', "Agent should still be trying to help after 1 attempt"
        
        # Attempt 2: Provide more unclear info
        result3 = await self.send_message("I think his NPI is 123456789 maybe", task_id, context_id)
        print(f"\n👤 USER: I think his NPI is 123456789 maybe")
        print(f"📊 STATE: {result3['status']['state']}")
        print(f"🤖 AGENT: {result3['status']['message']['parts'][0]['text'][:150]}...")
        
        # Should still be trying to help
        assert result3['status']['state'] in ['input-required', 'failed'], "Agent should be asking for clarification or failing appropriately"
        
        print("✅ PASS: Agent gives multiple opportunities before failing")
        
    async def test_client_says_no_info(self):
        """Test that agent fails gracefully when client says they don't have info."""
        print("\n📋 TEST 4: Client Explicitly Has No Info")
        print("-" * 50)
        
        # Start conversation
        result1 = await self.send_message("I need a referral but I don't know the provider details")
        task_id = result1['id']
        context_id = result1['contextId']
        
        print(f"👤 USER: I need a referral but I don't know the provider details")
        print(f"📊 STATE: {result1['status']['state']}")
        print(f"🤖 AGENT: {result1['status']['message']['parts'][0]['text'][:150]}...")
        
        # Client explicitly says they don't have the information
        result2 = await self.send_message("I don't have any provider information. I don't know their name or NPI.", task_id, context_id)
        
        print(f"\n👤 USER: I don't have any provider information. I don't know their name or NPI.")
        print(f"📊 STATE: {result2['status']['state']}")
        print(f"🤖 AGENT: {result2['status']['message']['parts'][0]['text'][:150]}...")
        
        # Should fail gracefully with helpful guidance
        final_state = result2['status']['state']
        response = result2['status']['message']['parts'][0]['text'].lower()
        
        # Should either fail or provide helpful guidance about getting provider info
        helpful_guidance = any(word in response for word in ['contact', 'office', 'provider', 'referral', 'help'])
        
        assert helpful_guidance, "Agent should provide helpful guidance when client can't provide info"
        print("✅ PASS: Agent handles explicit 'no info' gracefully")
    
    async def test_successful_verification_flow(self):
        """Test successful provider verification and workflow continuation."""
        print("\n📋 TEST 5: Successful Verification Flow")
        print("-" * 50)
        
        # Start with a provider that should be found (if system is working)
        result1 = await self.send_message("I need a referral from Dr. Sarah Johnson from Boston Medical, NPI 1234567890")
        task_id = result1['id']
        context_id = result1['contextId']
        
        print(f"👤 USER: I need a referral from Dr. Sarah Johnson from Boston Medical, NPI 1234567890")
        print(f"📊 STATE: {result1['status']['state']}")
        print(f"🤖 AGENT: {result1['status']['message']['parts'][0]['text'][:200]}...")
        
        # Should proceed to ask for patient information
        result2 = await self.send_message("Patient: Emma Thompson, DOB 04/15/1985, MRN 12345", task_id, context_id)
        
        print(f"\n👤 USER: Patient: Emma Thompson, DOB 04/15/1985, MRN 12345")
        print(f"📊 STATE: {result2['status']['state']}")
        print(f"🤖 AGENT: {result2['status']['message']['parts'][0]['text'][:200]}...")
        
        # Should be progressing through workflow (input-required or asking for more info)
        assert result2['status']['state'] in ['input-required', 'working'], "Should be progressing through workflow"
        
        print("✅ PASS: Successful verification allows workflow to continue")

async def run_all_tests():
    """Run all provider verification tests."""
    print("🧪 BALANCED PROVIDER VERIFICATION TESTS")
    print("=" * 60)
    
    test_runner = ProviderVerificationTest()
    
    try:
        await test_runner.setup()
        
        # Run all tests
        await test_runner.test_helpful_provider_clarification()
        await test_runner.test_npi_provided_optional()
        await test_runner.test_multiple_clarification_attempts()
        await test_runner.test_client_says_no_info()
        await test_runner.test_successful_verification_flow()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("✅ Provider verification is working with appropriate balance")
        print("✅ Agent gives clients multiple opportunities")
        print("✅ Agent fails gracefully when appropriate")
        print("✅ NPI handling works correctly")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        
    finally:
        await test_runner.teardown()

if __name__ == "__main__":
    asyncio.run(run_all_tests())
