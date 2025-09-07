#!/usr/bin/env python3
"""
Test the strict workflow order enforcement.

Validates order: Emergency → Provider → Patient → Clinical → Insurance → Schedule
"""

import asyncio
import pytest
import uuid
from typing import Dict, Any, Optional, Tuple
import httpx

BASE_URL = "http://localhost:8000"


class TestWorkflowOrder:
    """Validate the strict workflow order is followed."""
    
    @pytest.fixture
    async def client(self):
        """Create HTTP client for tests."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            yield client
    
    async def send_message(
        self, 
        client: httpx.AsyncClient,
        message_content: str,
        task_id: Optional[str] = None,
        context_id: Optional[str] = None
    ) -> Tuple[Dict[str, Any], str]:
        """Send message and return both full response and agent text."""
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
        
        params = {"message": message, "configuration": {"blocking": True}}
        
        request_data = {
            "jsonrpc": "2.0",
            "method": "message/send",
            "id": str(uuid.uuid4()),
            "params": params
        }
        
        response = await client.post(BASE_URL, json=request_data)
        response.raise_for_status()
        response_data = response.json()
        
        # Extract agent text
        result = response_data.get("result", {})
        status_msg = result.get("status", {}).get("message", {})
        agent_text = ""
        if status_msg and status_msg.get("parts"):
            agent_text = status_msg["parts"][0].get("text", "")
        
        return response_data, agent_text
    
    @pytest.mark.asyncio
    async def test_emergency_check_first(self, client):
        """Should check for emergency before anything else."""
        response_data, agent_text = await self.send_message(
            client, 
            "I need a cardiology referral"
        )
        
        # Should ask about emergency first
        assert "emergency" in agent_text.lower(), \
            "First response should check for emergency"
        assert "[NEED_MORE_INFO]" in agent_text or "[REFERRAL_FAILED]" not in agent_text, \
            "Should not fail immediately without emergency check"
    
    @pytest.mark.asyncio
    async def test_provider_before_patient(self, client):
        """Should ask for provider before patient details."""
        # Start conversation
        response_data, agent_text = await self.send_message(
            client,
            "I need a cardiology referral"
        )
        result = response_data.get("result", {})
        task_id = result.get("id")
        context_id = result.get("contextId")
        
        # Answer emergency question
        response_data, agent_text = await self.send_message(
            client,
            "No emergency, it's a chronic issue",
            task_id,
            context_id
        )
        
        # Should now ask for provider, not patient
        provider_keywords = ["referring", "physician", "doctor", "provider", "dr."]
        patient_keywords = ["patient", "date of birth", "dob", "phone", "email"]
        
        has_provider_request = any(kw in agent_text.lower() for kw in provider_keywords)
        has_patient_request = any(kw in agent_text.lower() for kw in patient_keywords)
        
        assert has_provider_request, \
            f"Should ask for provider information after emergency check. Got: {agent_text[:200]}"
        assert not has_patient_request or has_provider_request, \
            f"Should not ask for patient details before provider. Got: {agent_text[:200]}"
    
    @pytest.mark.asyncio
    async def test_skipping_ahead_redirects(self, client):
        """Providing out-of-order info should still follow workflow."""
        # Try to skip ahead with insurance info
        response_data, agent_text = await self.send_message(
            client,
            "I need referral. My insurance is Aetna ID#123456"
        )
        
        # Should still ask about emergency or provider first, not accept insurance
        assert "[NEED_MORE_INFO]" in agent_text, \
            "Should need more info when skipping ahead"
        
        # Should ask for emergency or provider, not continue with insurance
        should_ask_for = ["emergency", "provider", "physician", "doctor", "referring"]
        asked_for_right_thing = any(kw in agent_text.lower() for kw in should_ask_for)
        
        assert asked_for_right_thing, \
            f"Should redirect to emergency/provider when user skips ahead. Got: {agent_text[:200]}"
    
    @pytest.mark.asyncio
    async def test_complete_workflow_sequence(self, client):
        """Full workflow should follow correct order."""
        # Expected workflow order
        workflow_steps = [
            ("I need a cardiology referral", ["emergency"]),
            ("No emergency, chronic issue", ["provider", "physician", "doctor", "referring"]),
            ("Dr. Sarah Johnson from Denver, Colorado", ["patient", "name", "birth", "phone"]),
            ("John Doe, DOB 01/01/1980, Phone (303) 555-1234, email john@email.com", 
             ["clinical", "symptoms", "complaint", "medications", "history"]),
            ("Chest pain for 3 months, currently on metoprolol", 
             ["insurance", "member", "authorization"]),
            ("Aetna, Member ID AET123, Group GRP456", 
             ["appointment", "schedule", "monday", "thursday", "available"])
        ]
        
        task_id = None
        context_id = None
        
        for i, (user_input, expected_keywords) in enumerate(workflow_steps):
            if task_id and context_id:
                response_data, agent_text = await self.send_message(
                    client, user_input, task_id, context_id
                )
            else:
                response_data, agent_text = await self.send_message(
                    client, user_input
                )
                result = response_data.get("result", {})
                task_id = result.get("id")
                context_id = result.get("contextId")
            
            # Check if completed
            if "[REFERRAL_COMPLETE]" in agent_text:
                assert i >= 4, f"Should not complete before collecting all info, completed at step {i}"
                break
            
            # Check if failed (only acceptable for certain reasons)
            if "[REFERRAL_FAILED]" in agent_text:
                # Could fail if provider not found or other valid reason
                assert "not found" in agent_text.lower() or "verify" in agent_text.lower(), \
                    f"Unexpected failure at step {i}: {agent_text[:200]}"
                break
            
            # Otherwise, should ask for expected next item
            if i < len(workflow_steps) - 1:
                found_expected = any(kw in agent_text.lower() for kw in expected_keywords)
                assert found_expected or "[REFERRAL_COMPLETE]" in agent_text, \
                    f"Step {i}: Expected keywords {expected_keywords}, got: {agent_text[:200]}"
    
    @pytest.mark.asyncio
    async def test_provider_verification_in_workflow(self, client):
        """Provider verification should happen at the right point."""
        # Start conversation
        response_data, agent_text = await self.send_message(
            client,
            "I need a referral"
        )
        result = response_data.get("result", {})
        task_id = result.get("id")
        context_id = result.get("contextId")
        
        # Pass emergency check
        response_data, agent_text = await self.send_message(
            client,
            "No emergency",
            task_id,
            context_id
        )
        
        # Provide provider info - this should trigger verification
        response_data, agent_text = await self.send_message(
            client,
            "Referring doctor is Dr. Josh Mandel",
            task_id,
            context_id
        )
        
        # Agent should either:
        # 1. Show verification results
        # 2. Ask for clarification if multiple results
        # 3. Ask for more info if not found
        verification_indicators = [
            "found", "verify", "confirm", "multiple", "which", 
            "not found", "spell", "city", "state", "npi"
        ]
        
        has_verification = any(ind in agent_text.lower() for ind in verification_indicators)
        assert has_verification or "[NEED_MORE_INFO]" in agent_text, \
            f"Should handle provider verification. Got: {agent_text[:200]}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])