"""
Configuration management for the Walter Reed Cardiology Agent.

This module handles loading environment variables and basic configuration
settings for the A2A agent.
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the cardiology agent."""
    
    # Claude API Configuration
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
    
    # Server Configuration
    HOST = os.getenv("HOST", "localhost")
    PORT = int(os.getenv("PORT", "8000"))
    
    # A2A Configuration
    A2A_BASE_URL = f"http://{HOST}:{PORT}/a2a/v1"
    AGENT_CARD_PATH = "agentcard.json"
    
    # Agent Configuration
    AGENT_NAME = "Dr. Walter Reed Cardiology Referral Agent"
    AGENT_VERSION = "1.0.0"
    
    # NPPES API Configuration
    NPPES_BASE_URL = "https://npiregistry.cms.hhs.gov/api"
    NPPES_API_VERSION = "2.1"
    NPPES_REQUEST_TIMEOUT = 30  # seconds
    NPPES_MAX_RETRIES = 3
    
    @classmethod
    def validate(cls):
        """Validate that all required configuration is present."""
        if not cls.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
        # Validate agent card file exists
        if not Path(cls.AGENT_CARD_PATH).exists():
            raise FileNotFoundError(f"Agent card file not found: {cls.AGENT_CARD_PATH}")
        
        return True

# Global config instance
config = Config()
