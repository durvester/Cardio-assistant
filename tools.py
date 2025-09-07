"""
Provider verification tools for the Walter Reed Cardiology Agent.

This module contains tools for verifying healthcare providers using the NPPES API
and other external services.
"""

import asyncio
import logging
from typing import Dict, Optional, Any
import httpx
from config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProviderVerificationError(Exception):
    """Custom exception for provider verification errors."""
    pass


class NPPESClient:
    """Client for interacting with the NPPES NPI Registry API."""
    
    def __init__(self):
        """Initialize the NPPES client."""
        self.base_url = config.NPPES_BASE_URL
        self.version = config.NPPES_API_VERSION
        self.timeout = config.NPPES_REQUEST_TIMEOUT
        self.max_retries = config.NPPES_MAX_RETRIES
    
    async def search_providers(
        self,
        first_name: str,
        last_name: str,
        city: Optional[str] = None,
        state: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search for healthcare providers in the NPPES registry.
        
        Args:
            first_name: Provider's first name (required)
            last_name: Provider's last name (required)
            city: City to narrow search (optional)
            state: State abbreviation to narrow search (optional)
            limit: Maximum number of results (default 10)
            
        Returns:
            Dict containing search results and metadata
            
        Raises:
            ProviderVerificationError: If API request fails
        """
        params = {
            "version": self.version,
            "first_name": first_name.strip(),
            "last_name": last_name.strip(),
            "enumeration_type": "NPI-1",  # Individual providers
            "limit": limit,
            "pretty": "false"
        }
        
        # Add optional parameters if provided
        if city:
            params["city"] = city.strip()
        if state:
            params["state"] = state.strip().upper()
        
        logger.info(f"Searching NPPES for: {first_name} {last_name}" +
                   (f" in {city}, {state}" if city or state else ""))
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(self.max_retries):
                try:
                    response = await client.get(self.base_url, params=params)
                    response.raise_for_status()
                    
                    data = response.json()
                    logger.info(f"NPPES search returned {data.get('result_count', 0)} results")
                    return data
                    
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 429:  # Rate limit
                        wait_time = 2 ** attempt  # Exponential backoff
                        logger.warning(f"Rate limited, waiting {wait_time}s before retry {attempt + 1}")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"NPPES API HTTP error {e.response.status_code}: {e}")
                        raise ProviderVerificationError(f"NPPES API error: {e.response.status_code}")
                        
                except httpx.RequestError as e:
                    if attempt == self.max_retries - 1:
                        logger.error(f"NPPES API request failed after {self.max_retries} attempts: {e}")
                        raise ProviderVerificationError(f"Unable to connect to NPPES API: {e}")
                    
                    wait_time = 1 * (attempt + 1)
                    logger.warning(f"Request failed, retrying in {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
        
        raise ProviderVerificationError("Max retries exceeded")


async def verify_provider_nppes(
    first_name: str,
    last_name: str,
    city: Optional[str] = None,
    state: Optional[str] = None,
    npi: Optional[str] = None
) -> Dict[str, Any]:
    """
    Verify a healthcare provider using the NPPES NPI Registry.
    
    This function implements intelligent result handling:
    - 0 results: Provider not found
    - 1-3 results: Return providers for user selection
    - >3 results: Request more details (city/state)
    
    Args:
        first_name: Provider's first name
        last_name: Provider's last name  
        city: City to narrow search (optional)
        state: State to narrow search (optional)
        npi: NPI number to validate against found providers (optional)
        
    Returns:
        Dict containing verification results:
        {
            "status": "success" | "not_found" | "too_many" | "error",
            "message": "Human-readable status message",
            "result_count": int,
            "providers": [list of provider objects],
            "needs_refinement": bool,
            "suggested_params": ["city", "state"] # if refinement needed
        }
    """
    try:
        # Validate input
        if not first_name or not last_name:
            return {
                "status": "error",
                "message": "Both first name and last name are required for provider verification",
                "result_count": 0,
                "providers": [],
                "needs_refinement": False
            }
        
        client = NPPESClient()
        data = await client.search_providers(first_name, last_name, city, state)
        
        result_count = data.get("result_count", 0)
        results = data.get("results", [])
        
        # Process results based on count
        if result_count == 0:
            return {
                "status": "not_found",
                "message": f"No healthcare providers found matching '{first_name} {last_name}'" +
                          (f" in {city}, {state}" if city or state else "") + 
                          ". Please verify the spelling or try a different search.",
                "result_count": 0,
                "providers": [],
                "needs_refinement": False
            }
        
        elif result_count <= 3:
            # Process each provider to extract key information
            processed_providers = []
            npi_match_found = False
            
            for provider in results:
                basic = provider.get("basic", {})
                addresses = provider.get("addresses", [])
                provider_npi = provider.get("number", "")
                
                # Get primary address (usually first one)
                primary_address = addresses[0] if addresses else {}
                
                # Check if provider is active
                status = basic.get("status", "")
                is_active = status == "A"
                
                processed_provider = {
                    "npi": provider_npi,
                    "name": f"{basic.get('first_name', '')} {basic.get('middle_name', '')} {basic.get('last_name', '')}".strip(),
                    "credentials": basic.get("credential", ""),
                    "status": "Active" if is_active else "Inactive",
                    "is_active": is_active,
                    "city": primary_address.get("city", ""),
                    "state": primary_address.get("state", ""),
                    "enumeration_date": basic.get("enumeration_date", "")
                }
                processed_providers.append(processed_provider)
                
                # Check for NPI match if provided
                if npi and provider_npi == npi.strip():
                    npi_match_found = True
            
            # If NPI was provided but no match found, return validation failure
            if npi and not npi_match_found:
                return {
                    "status": "npi_mismatch",
                    "message": f"NPI {npi} does not match any provider named '{first_name} {last_name}'. " +
                              f"Found {result_count} provider(s) with that name but different NPIs. " +
                              "Please verify the NPI number or provider name.",
                    "result_count": result_count,
                    "providers": processed_providers,
                    "needs_refinement": False,
                    "provided_npi": npi
                }
            
            return {
                "status": "success",
                "message": f"Found {result_count} provider(s) matching '{first_name} {last_name}'" +
                          (f" in {city}, {state}" if city or state else "") + 
                          ". Please select the correct provider.",
                "result_count": result_count,
                "providers": processed_providers,
                "needs_refinement": False
            }
        
        else:
            # Too many results - need refinement, but check NPI first if provided
            if npi:
                # Check if any of the results match the provided NPI
                npi_match_found = False
                matching_provider = None
                
                for provider in results:
                    provider_npi = provider.get("number", "")
                    if provider_npi == npi.strip():
                        npi_match_found = True
                        # Process the matching provider
                        basic = provider.get("basic", {})
                        addresses = provider.get("addresses", [])
                        primary_address = addresses[0] if addresses else {}
                        status = basic.get("status", "")
                        is_active = status == "A"
                        
                        matching_provider = {
                            "npi": provider_npi,
                            "name": f"{basic.get('first_name', '')} {basic.get('middle_name', '')} {basic.get('last_name', '')}".strip(),
                            "credentials": basic.get("credential", ""),
                            "status": "Active" if is_active else "Inactive",
                            "is_active": is_active,
                            "city": primary_address.get("city", ""),
                            "state": primary_address.get("state", ""),
                            "enumeration_date": basic.get("enumeration_date", "")
                        }
                        break
                
                if not npi_match_found:
                    return {
                        "status": "npi_mismatch",
                        "message": f"NPI {npi} does not match any provider named '{first_name} {last_name}'. " +
                                  f"Found {result_count} provider(s) with that name but none have the provided NPI. " +
                                  "Please verify the NPI number or provider name.",
                        "result_count": result_count,
                        "providers": [],
                        "needs_refinement": False,
                        "provided_npi": npi
                    }
                else:
                    # Return the matching provider
                    return {
                        "status": "success",
                        "message": f"Found exact match: {matching_provider['name']} with NPI {npi}.",
                        "result_count": 1,
                        "providers": [matching_provider],
                        "needs_refinement": False
                    }
            
            # No NPI provided or NPI matched - proceed with normal refinement
            refinement_params = []
            if not city:
                refinement_params.append("city")
            if not state:
                refinement_params.append("state")
            
            return {
                "status": "too_many",
                "message": f"Found {result_count} providers matching '{first_name} {last_name}'" +
                          (f" in {city}, {state}" if city or state else "") + 
                          f". Please provide additional information to narrow the search: {', '.join(refinement_params)}.",
                "result_count": result_count,
                "providers": [],
                "needs_refinement": True,
                "suggested_params": refinement_params
            }
    
    except ProviderVerificationError as e:
        logger.error(f"Provider verification failed: {e}")
        return {
            "status": "error",
            "message": f"Unable to verify provider: {str(e)}",
            "result_count": 0,
            "providers": [],
            "needs_refinement": False
        }
    
    except Exception as e:
        logger.error(f"Unexpected error in provider verification: {e}")
        return {
            "status": "error",
            "message": "An unexpected error occurred during provider verification. Please try again.",
            "result_count": 0,
            "providers": [],
            "needs_refinement": False
        }


# Convenience functions for different verification scenarios
async def verify_provider_by_name(first_name: str, last_name: str) -> Dict[str, Any]:
    """Verify provider by name only."""
    return await verify_provider_nppes(first_name, last_name)


async def verify_provider_with_location(
    first_name: str, 
    last_name: str, 
    city: str, 
    state: str
) -> Dict[str, Any]:
    """Verify provider with location details."""
    return await verify_provider_nppes(first_name, last_name, city, state)


# Health check for the verification service
async def nppes_health_check() -> bool:
    """
    Check if the NPPES API is accessible.
    
    Returns:
        bool: True if API is accessible, False otherwise
    """
    try:
        client = NPPESClient()
        # Test with a minimal search that should return results quickly
        await client.search_providers("John", "Smith", limit=1)
        return True
    except Exception as e:
        logger.error(f"NPPES health check failed: {e}")
        return False