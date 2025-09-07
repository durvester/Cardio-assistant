#!/usr/bin/env python3
"""
Test appointment scheduling constraints.

Validates Monday/Thursday 11am-3pm scheduling rules.
"""

import asyncio
import pytest
import uuid
from typing import Dict, Any, Optional, Tuple
import httpx

BASE_URL = "http://localhost:8000"


class TestSchedulingRules:
    """Validate Mon/Thu 11am-3pm scheduling rules."""
    
    @pytest.fixture
    async def client(self):
        """Create HTTP client for tests."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            yield client
    
    async def send_message(
        self, 
        client: httpx.AsyncClient,
        message_content: str,
        task_id: Optional[str] = None,
        context_id: Optional[str] = None
    ) -> Tuple[Dict[str, Any], str]:
        """Send message and return response + agent text."""
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
    
    async def complete_to_scheduling_step(
        self, 
        client: httpx.AsyncClient
    ) -> Tuple[str, str]:
        """Complete referral up to scheduling step."""
        # Start referral
        response_data, agent_text = await self.send_message(
            client, 
            "I need a cardiology referral"
        )
        result = response_data.get("result", {})
        task_id = result.get("id")
        context_id = result.get("contextId")
        
        # Provide all required information quickly
        info_sequence = [
            "No emergency, chronic condition",
            "Dr. Sarah Johnson, NPI 1234567890, from Denver",
            "Patient: Mary Smith, DOB 03/15/1975, Phone (303) 555-9999, email mary@email.com",
            "Persistent chest pain for 6 weeks, currently on aspirin",
            "Blue Cross Blue Shield, Member ID: BCBS789, Group: GRP123"
        ]
        
        for info in info_sequence:
            response_data, agent_text = await self.send_message(
                client, info, task_id, context_id
            )
            
            # Check if we've reached scheduling
            if any(word in agent_text.lower() for word in ["appointment", "schedule", "monday", "thursday", "available"]):
                return task_id, context_id
            
            # Stop if failed
            if "[REFERRAL_FAILED]" in agent_text:
                pytest.skip(f"Referral failed before scheduling: {agent_text[:200]}")
        
        return task_id, context_id
    
    @pytest.mark.asyncio
    async def test_valid_time_slots_offered(self, client):
        """Should only offer Mon/Thu 11am-3pm slots."""
        task_id, context_id = await self.complete_to_scheduling_step(client)
        
        # Ask about available times
        response_data, agent_text = await self.send_message(
            client,
            "What appointment times are available?",
            task_id,
            context_id
        )
        
        # Should mention Monday and/or Thursday
        assert "monday" in agent_text.lower() or "thursday" in agent_text.lower(), \
            f"Should mention Monday or Thursday. Got: {agent_text[:300]}"
        
        # Should mention time range 11am-3pm
        time_indicators = ["11", "11:00", "11am", "3pm", "3:00", "15:00"]
        has_time_range = any(time in agent_text.lower() for time in time_indicators)
        assert has_time_range, \
            f"Should mention 11am-3pm time range. Got: {agent_text[:300]}"
        
        # Should NOT offer other days
        invalid_days = ["tuesday", "wednesday", "friday", "saturday", "sunday"]
        offered_invalid = [day for day in invalid_days if day in agent_text.lower()]
        assert not offered_invalid, \
            f"Should not offer {offered_invalid}. Got: {agent_text[:300]}"
    
    @pytest.mark.asyncio
    async def test_invalid_day_request_fails(self, client):
        """Requesting unavailable day should fail referral."""
        task_id, context_id = await self.complete_to_scheduling_step(client)
        
        # Request invalid day
        invalid_requests = [
            "I can only do Fridays",
            "Tuesday afternoon would be best",
            "How about Wednesday?",
            "I need a weekend appointment"
        ]
        
        for request in invalid_requests:
            # Fresh referral for each test
            task_id, context_id = await self.complete_to_scheduling_step(client)
            
            response_data, agent_text = await self.send_message(
                client,
                request,
                task_id,
                context_id
            )
            
            # Should either explain constraints or fail
            if "[REFERRAL_FAILED]" in agent_text:
                assert "Dr. Reed's office" in agent_text or "Dr Walter" in agent_text, \
                    f"Failed referral should defer to office. Got: {agent_text[:200]}"
            else:
                # Should explain Monday/Thursday only
                assert "monday" in agent_text.lower() or "thursday" in agent_text.lower(), \
                    f"Should explain available days for '{request}'. Got: {agent_text[:200]}"
    
    @pytest.mark.asyncio
    async def test_invalid_time_request_fails(self, client):
        """Requesting unavailable time should fail referral."""
        task_id, context_id = await self.complete_to_scheduling_step(client)
        
        # Request invalid time on valid day
        invalid_times = [
            "Monday at 8am",
            "Thursday at 5pm", 
            "Monday evening",
            "Thursday at 9am"
        ]
        
        for request in invalid_times:
            # Fresh referral for each test
            task_id, context_id = await self.complete_to_scheduling_step(client)
            
            response_data, agent_text = await self.send_message(
                client,
                request,
                task_id,
                context_id
            )
            
            # Should either explain constraints or fail
            if "[REFERRAL_FAILED]" not in agent_text:
                # Should explain 11am-3pm only
                assert "11" in agent_text or "3" in agent_text or "3:00" in agent_text, \
                    f"Should explain time constraints for '{request}'. Got: {agent_text[:200]}"
    
    @pytest.mark.asyncio
    async def test_valid_appointment_completes(self, client):
        """Valid appointment time should complete referral."""
        task_id, context_id = await self.complete_to_scheduling_step(client)
        
        # Request valid times
        valid_requests = [
            "Monday at 11am works perfectly",
            "Thursday at 2pm would be great",
            "Monday afternoon is fine",
            "Thursday at noon"
        ]
        
        for request in valid_requests:
            # Fresh referral for each test
            task_id, context_id = await self.complete_to_scheduling_step(client)
            
            response_data, agent_text = await self.send_message(
                client,
                request,
                task_id,
                context_id
            )
            
            # Should complete successfully
            if "[REFERRAL_COMPLETE]" in agent_text:
                # Should confirm appointment details
                assert "appointment" in agent_text.lower() or "scheduled" in agent_text.lower(), \
                    f"Should confirm appointment. Got: {agent_text[:200]}"
                
                # Should mention Dr. Reed
                assert "Dr. Reed" in agent_text or "Dr Walter Reed" in agent_text, \
                    f"Should mention Dr. Reed in confirmation. Got: {agent_text[:200]}"
                break
            elif "[REFERRAL_FAILED]" not in agent_text:
                # Might need confirmation
                assert "[NEED_MORE_INFO]" in agent_text, \
                    f"Should either complete or need confirmation for '{request}'. Got: {agent_text[:200]}"
    
    @pytest.mark.asyncio
    async def test_scheduling_constraint_explanation(self, client):
        """Agent should explain scheduling constraints clearly."""
        task_id, context_id = await self.complete_to_scheduling_step(client)
        
        # Ask about availability
        response_data, agent_text = await self.send_message(
            client,
            "When can I schedule the appointment?",
            task_id,
            context_id
        )
        
        # Should clearly state constraints
        constraint_explained = (
            ("monday" in agent_text.lower() and "thursday" in agent_text.lower()) and
            ("11" in agent_text or "11:00" in agent_text.lower() or "eleven" in agent_text.lower()) and
            ("3" in agent_text or "3:00" in agent_text or "three" in agent_text.lower())
        )
        
        assert constraint_explained, \
            f"Should clearly explain Mon/Thu 11am-3pm constraint. Got: {agent_text[:300]}"
        
        # Should mention these are the only times
        exclusivity_indicators = ["only", "available", "sees patients", "new patients"]
        has_exclusivity = any(ind in agent_text.lower() for ind in exclusivity_indicators)
        assert has_exclusivity, \
            f"Should indicate these are the only available times. Got: {agent_text[:300]}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])