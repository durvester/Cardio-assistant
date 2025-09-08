"""
Main entry point for the Walter Reed Cardiology Agent A2A Server.

This module sets up and runs the A2A-compliant server using the A2A Python SDK.
"""

import asyncio
import json
import logging
import uvicorn
from pathlib import Path
from string import Template

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks.database_task_store import DatabaseTaskStore
from a2a.types import AgentCard
from sqlalchemy.ext.asyncio import create_async_engine

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
            agent_card_template = f.read()
        
        # Use Template for safe variable substitution
        template = Template(agent_card_template)
        agent_card_json = template.safe_substitute(A2A_BASE_URL=config.A2A_BASE_URL)
        agent_card_data = json.loads(agent_card_json)
        
        # Convert JSON to AgentCard object
        # The A2A SDK should handle this conversion automatically
        agent_card = AgentCard.model_validate(agent_card_data)
        
        logger.info(f"Loaded agent card: {agent_card.name}")
        return agent_card
        
    except Exception as e:
        logger.error(f"Error loading agent card: {e}")
        raise


async def create_app() -> A2AStarletteApplication:
    """
    Create and configure the A2A Starlette application.
    
    Returns:
        Configured A2AStarletteApplication instance
    """
    try:
        # Load agent card
        agent_card = load_agent_card()
        
        # Ensure data directory exists
        data_dir = Path(config.DATA_DIR)
        data_dir.mkdir(exist_ok=True)
        
        # Create SQLite database engine
        db_path = data_dir / config.TASK_STORE_DB
        engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}")
        
        # Create database task store
        task_store = DatabaseTaskStore(
            engine=engine,
            create_table=True,
            table_name="tasks"
        )
        
        # Initialize the database schema
        await task_store.initialize()
        
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
        logger.info(f"Database task store initialized at: {db_path}")
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
        
        # Create async function to initialize app
        async def init_app():
            return await create_app()
        
        # Create the application
        app = asyncio.run(init_app())
        
        # Build the Starlette app
        starlette_app = app.build()
        
        # Log startup information
        logger.info(f"Starting {config.AGENT_NAME} v{config.AGENT_VERSION}")
        logger.info(f"Server will run on http://{config.HOST}:{config.PORT}")
        logger.info(f"Agent card available at: {config.A2A_BASE_URL}/.well-known/agent-card.json")
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
