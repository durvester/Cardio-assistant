"""
Main entry point for the Walter Reed Cardiology Agent A2A Server.

This module sets up and runs the A2A-compliant server using the A2A Python SDK.
"""

import json
import logging
import uvicorn
from pathlib import Path

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard

from config import config
from agent_executor import cardiology_executor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_agent_card() -> AgentCard:
    """
    Load the agent card from agentcard.json file.
    
    Returns:
        AgentCard object parsed from JSON
    """
    try:
        agent_card_path = Path(config.AGENT_CARD_PATH)
        if not agent_card_path.exists():
            raise FileNotFoundError(f"Agent card file not found: {agent_card_path}")
        
        with open(agent_card_path, 'r') as f:
            agent_card_data = json.load(f)
        
        # Convert JSON to AgentCard object
        # The A2A SDK should handle this conversion automatically
        agent_card = AgentCard.model_validate(agent_card_data)
        
        logger.info(f"Loaded agent card: {agent_card.name}")
        return agent_card
        
    except Exception as e:
        logger.error(f"Error loading agent card: {e}")
        raise


def create_app() -> A2AStarletteApplication:
    """
    Create and configure the A2A Starlette application.
    
    Returns:
        Configured A2AStarletteApplication instance
    """
    try:
        # Load agent card
        agent_card = load_agent_card()
        
        # Create task store for managing task state
        task_store = InMemoryTaskStore()
        
        # Create request handler with our agent executor
        request_handler = DefaultRequestHandler(
            agent_executor=cardiology_executor,
            task_store=task_store
        )
        
        # Create the A2A Starlette application
        app = A2AStarletteApplication(
            agent_card=agent_card,
            http_handler=request_handler
        )
        
        logger.info("A2A application created successfully")
        return app
        
    except Exception as e:
        logger.error(f"Error creating A2A application: {e}")
        raise


def main():
    """
    Main function to start the A2A server.
    """
    try:
        # Validate configuration
        config.validate()
        logger.info("Configuration validated successfully")
        
        # Create the application
        app = create_app()
        
        # Build the Starlette app
        starlette_app = app.build()
        
        # Log startup information
        logger.info(f"Starting {config.AGENT_NAME} v{config.AGENT_VERSION}")
        logger.info(f"Server will run on http://{config.HOST}:{config.PORT}")
        logger.info(f"Agent card available at: http://{config.HOST}:{config.PORT}/.well-known/agent-card.json")
        logger.info(f"A2A endpoint available at: {config.A2A_BASE_URL}")
        
        # Start the server
        uvicorn.run(
            starlette_app,
            host=config.HOST,
            port=config.PORT,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise


if __name__ == "__main__":
    main()
