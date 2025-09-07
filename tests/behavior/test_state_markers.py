#!/usr/bin/env python3
"""
Test state control markers.

Validates that exactly one state marker appears in each response.
"""

import asyncio
import pytest
import uuid
from typing import Dict, Any, Optional, List
import httpx
import re

BASE_URL = "http://localhost:8000"


class TestStateMarkers:
    """Validate state control marker usage."""
    
    STATE_MARKERS = [
        "[NEED_MORE_INFO]",
        "[REFERRAL_COMPLETE]",
        "[REFERRAL_FAILED]"
    ]
    
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
    ) -> Dict[str, Any]:
        """Send message and return response."""
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
        return response.json()
    
    def count_markers(self, text: str) -> Dict[str, int]:
        """Count occurrences of each state marker."""
        counts = {}
        for marker in self.STATE_MARKERS:
            counts[marker] = text.count(marker)
        return counts
    
    def extract_agent_text(self, response_data: Dict[str, Any]) -> str:
        """Extract agent text from response."""
        result = response_data.get("result", {})
        status_msg = result.get("status", {}).get("message", {})
        if status_msg and status_msg.get("parts"):
            return status_msg["parts"][0].get("text", "")
        return ""
    
    @pytest.mark.asyncio
    async def test_one_marker_per_response(self, client):
        """Each response must have exactly one state marker."""
        test_messages = [
            "I need a cardiology referral",
            "What is heart disease?",
            "I'm having chest pain right now",
            "My doctor is Dr. Smith",
            "Can you help me?"
        ]
        
        for message in test_messages:
            response_data = await self.send_message(client, message)
            agent_text = self.extract_agent_text(response_data)
            
            # Count markers
            marker_counts = self.count_markers(agent_text)
            total_markers = sum(marker_counts.values())
            
            # Assert exactly one marker
            assert total_markers == 1, \
                f"Expected exactly 1 marker for '{message}', found {total_markers}: {marker_counts}"
            
            # Log which marker was used
            used_marker = [m for m, c in marker_counts.items() if c > 0][0]
            print(f"Message: '{message[:50]}...' → {used_marker}")
    
    @pytest.mark.asyncio
    async def test_marker_state_transitions(self, client):
        """Validate legal state transitions."""
        # Start conversation
        response_data = await self.send_message(client, "I need a referral")
        agent_text = self.extract_agent_text(response_data)
        result = response_data.get("result", {})
        task_id = result.get("id")
        context_id = result.get("contextId")
        
        # Track state progression
        state_history = []
        
        # First response should be NEED_MORE_INFO (after emergency check)
        if "[NEED_MORE_INFO]" in agent_text:
            state_history.append("NEED_MORE_INFO")
        elif "[REFERRAL_FAILED]" in agent_text:
            # Could fail immediately for non-referral
            state_history.append("REFERRAL_FAILED")
            return  # Terminal state
        
        # Continue conversation
        conversation_flow = [
            "No emergency",
            "Dr. Sarah Johnson from Denver", 
            "Patient John Doe, DOB 01/01/1980, phone (303) 555-1234, email john@email.com",
            "Chest pain for 2 weeks",
            "Aetna insurance, ID AET123",
            "Monday at 11am works"
        ]
        
        for message in conversation_flow:
            response_data = await self.send_message(client, message, task_id, context_id)
            agent_text = self.extract_agent_text(response_data)
            
            # Identify current state
            if "[NEED_MORE_INFO]" in agent_text:
                current_state = "NEED_MORE_INFO"
            elif "[REFERRAL_COMPLETE]" in agent_text:
                current_state = "REFERRAL_COMPLETE"
            elif "[REFERRAL_FAILED]" in agent_text:
                current_state = "REFERRAL_FAILED"
            else:
                pytest.fail(f"No state marker found in response: {agent_text[:100]}")
            
            # Check for illegal transitions
            if state_history and state_history[-1] in ["REFERRAL_COMPLETE", "REFERRAL_FAILED"]:
                pytest.fail(f"Illegal transition: {state_history[-1]} → {current_state} (terminal states should not transition)")
            
            state_history.append(current_state)
            
            # Stop if terminal state reached
            if current_state in ["REFERRAL_COMPLETE", "REFERRAL_FAILED"]:
                break
        
        # Validate we reached a terminal state eventually
        assert state_history[-1] in ["REFERRAL_COMPLETE", "REFERRAL_FAILED"], \
            f"Conversation should reach terminal state. History: {state_history}"
    
    @pytest.mark.asyncio
    async def test_terminal_states_end_conversation(self, client):
        """REFERRAL_COMPLETE and REFERRAL_FAILED should be terminal."""
        # Test REFERRAL_FAILED terminal state
        response_data = await self.send_message(client, "What causes heart attacks?")
        agent_text = self.extract_agent_text(response_data)
        result = response_data.get("result", {})
        
        if "[REFERRAL_FAILED]" in agent_text:
            task_id = result.get("id")
            context_id = result.get("contextId")
            
            # Try to continue - should not process or should indicate conversation is over
            response_data = await self.send_message(
                client, 
                "Wait, I actually need a referral",
                task_id,
                context_id
            )
            
            # Check state - should be completed/failed
            state = response_data.get("result", {}).get("status", {}).get("state")
            assert state in ["completed", "failed"], \
                f"Terminal state should end conversation, but got state: {state}"
    
    @pytest.mark.asyncio
    async def test_appropriate_marker_usage(self, client):
        """Verify markers are used appropriately for the context."""
        test_cases = [
            {
                "message": "I'm having severe chest pain right now",
                "expected_marker": "[REFERRAL_FAILED]",
                "reason": "Emergency should trigger REFERRAL_FAILED"
            },
            {
                "message": "I need a cardiology referral from my doctor",
                "expected_marker": "[NEED_MORE_INFO]",
                "reason": "Valid referral should trigger NEED_MORE_INFO"
            },
            {
                "message": "What is a heart murmur?",
                "expected_marker": "[REFERRAL_FAILED]",
                "reason": "Non-referral should trigger REFERRAL_FAILED"
            }
        ]
        
        for test_case in test_cases:
            response_data = await self.send_message(client, test_case["message"])
            agent_text = self.extract_agent_text(response_data)
            
            assert test_case["expected_marker"] in agent_text, \
                f"{test_case['reason']}. Expected {test_case['expected_marker']}, got: {agent_text[:100]}"
    
    @pytest.mark.asyncio
    async def test_marker_position_in_response(self, client):
        """Markers should appear in the response (not necessarily at the end)."""
        response_data = await self.send_message(client, "I need a referral")
        agent_text = self.extract_agent_text(response_data)
        
        # Find marker position
        marker_positions = {}
        for marker in self.STATE_MARKERS:
            pos = agent_text.find(marker)
            if pos != -1:
                marker_positions[marker] = pos
        
        # Should have exactly one marker
        assert len(marker_positions) == 1, \
            f"Should have exactly one marker, found: {list(marker_positions.keys())}"
        
        # Marker should be in the text (position >= 0)
        marker, position = list(marker_positions.items())[0]
        assert position >= 0, f"Marker {marker} should be in the response text"
        
        # Log where marker appears
        text_length = len(agent_text)
        relative_position = position / text_length if text_length > 0 else 0
        print(f"Marker {marker} at position {position}/{text_length} ({relative_position:.1%} through text)")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])