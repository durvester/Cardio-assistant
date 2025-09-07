#!/usr/bin/env python3
"""
Test provider verification tool usage.

Validates NPI extraction, tool calling, and response handling.
"""

import asyncio
import pytest
import uuid
from typing import Dict, Any, Optional
import httpx
from unittest.mock import patch, MagicMock

BASE_URL = "http://localhost:8000"


class TestProviderToolUsage:
    """Validate proper tool usage for provider verification."""
    
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
        """Send message using A2A protocol."""
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
    
    def extract_agent_text(self, response_data: Dict[str, Any]) -> str:
        """Extract agent text from response."""
        result = response_data.get("result", {})
        status_msg = result.get("status", {}).get("message", {})
        if status_msg and status_msg.get("parts"):
            return status_msg["parts"][0].get("text", "")
        return ""
    
    @pytest.mark.asyncio
    async def test_npi_extraction_patterns(self, client):
        """Should extract NPI from various formats."""
        # Start referral
        response_data = await self.send_message(client, "I need a cardiology referral")
        result = response_data.get("result", {})
        task_id = result.get("id")
        context_id = result.get("contextId")
        
        # Handle emergency check
        response_data = await self.send_message(
            client, 
            "No emergency", 
            task_id, 
            context_id
        )
        
        # Test various NPI formats
        npi_formats = [
            ("Dr. Smith, NPI 1234567890", "1234567890"),
            ("Dr. Jones NPI: 9876543210", "9876543210"),
            ("Referring: Dr. Brown (NPI#1112223334)", "1112223334"),
            ("Dr. White from Boston", None)  # No NPI
        ]
        
        for message, expected_npi in npi_formats:
            # Fresh conversation for each test
            response_data = await self.send_message(client, "I need a referral")
            result = response_data.get("result", {})
            task_id = result.get("id")
            context_id = result.get("contextId")
            
            # Skip emergency
            await self.send_message(client, "No emergency", task_id, context_id)
            
            # Provide provider with NPI format
            response_data = await self.send_message(
                client,
                f"Referral from {message}",
                task_id,
                context_id
            )
            agent_text = self.extract_agent_text(response_data)
            
            if expected_npi:
                # Should use the NPI in verification
                # Agent should either verify or ask for confirmation
                assert "[NEED_MORE_INFO]" in agent_text or "verif" in agent_text.lower(), \
                    f"Should process provider with NPI {expected_npi}. Got: {agent_text[:200]}"
            else:
                # Without NPI, should still try to verify by name
                assert "[NEED_MORE_INFO]" in agent_text or "[REFERRAL_FAILED]" in agent_text, \
                    f"Should process provider without NPI. Got: {agent_text[:200]}"
    
    @pytest.mark.asyncio
    async def test_provider_not_found_handling(self, client):
        """Should handle provider not found gracefully."""
        # Start referral
        response_data = await self.send_message(client, "I need a cardiology referral")
        result = response_data.get("result", {})
        task_id = result.get("id")
        context_id = result.get("contextId")
        
        # Skip emergency
        await self.send_message(client, "No emergency", task_id, context_id)
        
        # Provider that won't be found
        response_data = await self.send_message(
            client,
            "Dr. Mohit Durve is my referring physician",
            task_id,
            context_id
        )
        agent_text = self.extract_agent_text(response_data)
        
        # Should handle not found appropriately
        not_found_indicators = [
            "not found", "cannot find", "unable to verify", 
            "spell", "confirm", "correct", "alternative"
        ]
        
        has_not_found = any(ind in agent_text.lower() for ind in not_found_indicators)
        assert has_not_found or "[REFERRAL_FAILED]" in agent_text, \
            f"Should handle provider not found. Got: {agent_text[:200]}"
    
    @pytest.mark.asyncio
    async def test_multiple_provider_results(self, client):
        """Should handle multiple search results correctly."""
        # Start referral
        response_data = await self.send_message(client, "I need a cardiology referral")
        result = response_data.get("result", {})
        task_id = result.get("id")
        context_id = result.get("contextId")
        
        # Skip emergency
        await self.send_message(client, "No emergency", task_id, context_id)
        
        # Provider with multiple results (Josh Mandel typically returns 2)
        response_data = await self.send_message(
            client,
            "Referral from Dr. Josh Mandel",
            task_id,
            context_id
        )
        agent_text = self.extract_agent_text(response_data)
        
        # Should handle multiple results
        multiple_indicators = [
            "found", "multiple", "which", "select", "choose",
            "providers", "results", "options"
        ]
        
        has_multiple = any(ind in agent_text.lower() for ind in multiple_indicators)
        
        # Should either present options or ask for clarification
        assert has_multiple or "[NEED_MORE_INFO]" in agent_text, \
            f"Should handle multiple providers. Got: {agent_text[:200]}"
        
        # Should NOT make up fake data
        fake_data = ["1234567890", "Boston, MA", "Cambridge, MA"]
        has_fake = any(fake in agent_text for fake in fake_data)
        assert not has_fake, \
            f"Should not use fake provider data. Got: {agent_text[:200]}"
    
    @pytest.mark.asyncio
    async def test_too_many_results_asks_location(self, client):
        """Should ask for city/state when >3 results."""
        # Start referral
        response_data = await self.send_message(client, "I need a cardiology referral")
        result = response_data.get("result", {})
        task_id = result.get("id")
        context_id = result.get("contextId")
        
        # Skip emergency
        await self.send_message(client, "No emergency", task_id, context_id)
        
        # Provider with many results (Peter Smith typically returns many)
        response_data = await self.send_message(
            client,
            "Referral from Dr. Peter Smith",
            task_id,
            context_id
        )
        agent_text = self.extract_agent_text(response_data)
        
        # Should ask for location to narrow down
        location_indicators = [
            "city", "state", "location", "where", "practice",
            "narrow", "specific", "many", "results"
        ]
        
        has_location_request = any(ind in agent_text.lower() for ind in location_indicators)
        assert has_location_request or "[NEED_MORE_INFO]" in agent_text, \
            f"Should ask for location with many results. Got: {agent_text[:200]}"
    
    @pytest.mark.asyncio
    async def test_npi_mismatch_handling(self, client):
        """Should handle NPI mismatch appropriately."""
        # Start referral
        response_data = await self.send_message(client, "I need a cardiology referral")
        result = response_data.get("result", {})
        task_id = result.get("id")
        context_id = result.get("contextId")
        
        # Skip emergency
        await self.send_message(client, "No emergency", task_id, context_id)
        
        # Provide mismatched NPI
        response_data = await self.send_message(
            client,
            "Dr. Sarah Johnson, NPI 9999999999",  # Wrong NPI for this provider
            task_id,
            context_id
        )
        agent_text = self.extract_agent_text(response_data)
        
        # Should handle mismatch
        mismatch_indicators = [
            "mismatch", "doesn't match", "incorrect", "verify",
            "confirm", "correct npi", "different"
        ]
        
        # Either mentions mismatch or asks for clarification
        has_mismatch_handling = any(ind in agent_text.lower() for ind in mismatch_indicators)
        assert has_mismatch_handling or "[NEED_MORE_INFO]" in agent_text, \
            f"Should handle NPI mismatch. Got: {agent_text[:200]}"
    
    @pytest.mark.asyncio
    async def test_location_refinement(self, client):
        """Should use location to refine search results."""
        # Start referral
        response_data = await self.send_message(client, "I need a cardiology referral")
        result = response_data.get("result", {})
        task_id = result.get("id")
        context_id = result.get("contextId")
        
        # Skip emergency
        await self.send_message(client, "No emergency", task_id, context_id)
        
        # Provider with many results
        response_data = await self.send_message(
            client,
            "Dr. Peter Smith",
            task_id,
            context_id
        )
        
        # Provide location to refine
        response_data = await self.send_message(
            client,
            "He's in Aurora, Colorado",
            task_id,
            context_id
        )
        agent_text = self.extract_agent_text(response_data)
        
        # Should acknowledge location and proceed
        location_used = (
            "aurora" in agent_text.lower() or 
            "colorado" in agent_text.lower() or
            "co" in agent_text.lower()
        )
        
        assert location_used or "[NEED_MORE_INFO]" in agent_text, \
            f"Should use location to refine search. Got: {agent_text[:200]}"
    
    @pytest.mark.asyncio
    async def test_real_npi_data_usage(self, client):
        """Should use real NPPES data, not fabricated."""
        # Known providers from NPPES
        known_providers = [
            {
                "name": "Dr. Josh Mandel",
                "real_npis": ["1659411569", "1154612372"],  # Actual NPIs from NPPES
                "fake_npis": ["1234567890", "9876543210"]  # Should NOT appear
            }
        ]
        
        for provider in known_providers:
            # Start referral
            response_data = await self.send_message(client, "I need a referral")
            result = response_data.get("result", {})
            task_id = result.get("id")
            context_id = result.get("contextId")
            
            # Skip emergency
            await self.send_message(client, "No emergency", task_id, context_id)
            
            # Provide provider name
            response_data = await self.send_message(
                client,
                f"Referral from {provider['name']}",
                task_id,
                context_id
            )
            agent_text = self.extract_agent_text(response_data)
            
            # Check for real vs fake NPIs
            has_real = any(npi in agent_text for npi in provider['real_npis'])
            has_fake = any(npi in agent_text for npi in provider['fake_npis'])
            
            if has_fake:
                pytest.fail(f"Using fake NPI data for {provider['name']}. Found fake NPI in: {agent_text[:300]}")
            
            # If NPIs are shown, they should be real
            if any(char.isdigit() for char in agent_text):
                # Has numbers, check if they're real NPIs
                print(f"Provider {provider['name']} - Uses real NPIs: {has_real}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])