========================
CODE SNIPPETS
========================
TITLE: Run Example
DESCRIPTION: Executes a sample script included with the Python A2A library to demonstrate its functionality. This command helps verify that the installation is working and that examples can be run.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/__wiki__/Installation.md#_snippet_5

LANGUAGE: bash
CODE:
```
python -m examples.getting_started.hello_a2a
```

----------------------------------------

TITLE: Install A2A Streaming Dependencies
DESCRIPTION: Installs core A2A library and additional packages required for UI and distributed streaming examples.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/examples/streaming/README.md#_snippet_0

LANGUAGE: bash
CODE:
```
pip install python-a2a

pip install colorama tqdm flask

pip install aiohttp tqdm
```

----------------------------------------

TITLE: Simple Client Example
DESCRIPTION: Shows how to connect to any A2A-compatible agent, send requests, and handle responses. This example is part of the beginner-level getting started guide.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/examples/README.md#_snippet_1

LANGUAGE: python
CODE:
```
# Code for getting_started/simple_client.py not provided in input text.
```

----------------------------------------

TITLE: Simple Server Example
DESCRIPTION: Guides users on creating their own basic A2A server, serving as a foundational example for building your first agent. It's included in the beginner section.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/examples/README.md#_snippet_2

LANGUAGE: python
CODE:
```
# Code for getting_started/simple_server.py not provided in input text.
```

----------------------------------------

TITLE: Test Installation from TestPyPI (Bash)
DESCRIPTION: Creates a new virtual environment, activates it, installs the package from TestPyPI, and then imports it to verify the installation and check the version number. This confirms the package is correctly published and installable.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/PUBLICATION_GUIDE.md#_snippet_6

LANGUAGE: bash
CODE:
```
# Create a test environment
uv venv create --fresh .test-venv
source .test-venv/bin/activate

# Install from TestPyPI
uv pip install --index-url https://test.pypi.org/simple/ --no-deps python-a2a

# Test import
python -c "import python_a2a; print(python_a2a.__version__)"
```

----------------------------------------

TITLE: Install Python A2A Library
DESCRIPTION: Installs the python-a2a library using pip. This is the initial step required to begin developing A2A agents and clients.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/__wiki__/Quickstart.md#_snippet_0

LANGUAGE: bash
CODE:
```
pip install python-a2a
```

----------------------------------------

TITLE: Basic and Recommended Installation
DESCRIPTION: Installs the core Python A2A library. The recommended method uses UV for improved performance and dependency management. Both commands achieve the installation of the base package.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/__wiki__/Installation.md#_snippet_0

LANGUAGE: bash
CODE:
```
pip install python-a2a
```

LANGUAGE: bash
CODE:
```
uv install python-a2a
```

----------------------------------------

TITLE: Agent Discovery and Registry Setup
DESCRIPTION: Provides a comprehensive example of setting up an agent registry and registering an agent with it. It also shows how to use a discovery client to find registered agents in the network.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/README_es.md#_snippet_7

LANGUAGE: python
CODE:
```
from python_a2a import AgentCard, A2AServer, run_server
from python_a2a.discovery import AgentRegistry, run_registry, enable_discovery, DiscoveryClient
import threading
import time

# Create a registry server
registry = AgentRegistry(
    name="A2A Registry Server",
    description="Central registry for agent discovery"
)

# Run the registry in a background thread
registry_port = 8000
thread = threading.Thread(
    target=lambda: run_registry(registry, host="0.0.0.0", port=registry_port),
    daemon=True
)
thread.start()
time.sleep(1)  # Let the registry start

# Create a sample agent
agent_card = AgentCard(
    name="Weather Agent",
    description="Provides weather information",
    url="http://localhost:8001",
    version="1.0.0",
    capabilities={
        "weather_forecasting": True,
        "google_a2a_compatible": True  # Enable Google A2A compatibility
    }
)
agent = A2AServer(agent_card=agent_card)

# Enable discovery - this registers with the registry
registry_url = f"http://localhost:{registry_port}"
discovery_client = enable_discovery(agent, registry_url=registry_url)

# Run the agent in a separate thread
agent_thread = threading.Thread(
    target=lambda: run_server(agent, host="0.0.0.0", port=8001),
    daemon=True
)
agent_thread.start()
time.sleep(1)  # Let the agent start

# Create a discovery client for discovering agents
client = DiscoveryClient(agent_card=None)  # No agent card needed for discovery only
client.add_registry(registry_url)

# Discover all agents
agents = client.discover()
print(f"Discovered {len(agents)} agents:")
for agent in agents:
    print(f"- {agent.name} at {agent.url}")
    print(f"  Capabilities: {agent.capabilities}")
```

----------------------------------------

TITLE: Install python-a2a
DESCRIPTION: Instructions for installing the python-a2a library. LangChain is automatically included as a dependency, simplifying setup.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/README_es.md#_snippet_4

LANGUAGE: bash
CODE:
```
pip install python-a2a
# LangChain is included automatically
```

----------------------------------------

TITLE: Install Python A2A with All Dependencies - Bash
DESCRIPTION: Installs the `python-a2a` package along with all available optional dependencies defined by the `[all]` extra. This command ensures you have all feature-specific requirements installed.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/docs/installation.rst#_snippet_6

LANGUAGE: bash
CODE:
```
pip install "python-a2a[all]"
```

----------------------------------------

TITLE: Install Python A2A Base Package
DESCRIPTION: Installs the core python-a2a package with minimal dependencies, primarily the 'requests' library. This is the standard way to get the basic functionality of the library.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/docs/installation.rst#_snippet_0

LANGUAGE: bash
CODE:
```
pip install python-a2a
```

----------------------------------------

TITLE: Perform Python A2A Development Install - Bash
DESCRIPTION: Executes a sequence of commands to clone the repository, change directory, and install the library in editable mode with development dependencies using pip. This setup is specifically for contributors or those wishing to run tests against the source code.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/docs/installation.rst#_snippet_7

LANGUAGE: bash
CODE:
```
git clone https://github.com/themanojdesai/python-a2a.git
```

LANGUAGE: bash
CODE:
```
cd python-a2a
```

LANGUAGE: bash
CODE:
```
pip install -e ".[dev]"
```

----------------------------------------

TITLE: Complete Installation
DESCRIPTION: Installs the Python A2A library along with all available optional dependencies. This is useful for users who want to leverage the full range of features without manually selecting each component.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/__wiki__/Installation.md#_snippet_2

LANGUAGE: bash
CODE:
```
pip install "python-a2a[all]"
```

----------------------------------------

TITLE: Python: Simple Client Example
DESCRIPTION: A basic client example demonstrating how to connect to A2A agents. This is a starting point for frontend developers to interact with A2A services.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/examples/README.md#_snippet_34

LANGUAGE: python
CODE:
```
# getting_started/simple_client.py
# Simple client example
# Connect to A2A agents
```

----------------------------------------

TITLE: Setup and Use Agent Discovery and Registry
DESCRIPTION: Provides a complete example of setting up an agent registry server, running it in a background thread, creating an agent, enabling its discovery by registering it with the registry, and using a discovery client to find registered agents. This showcases the core components for building a discoverable agent ecosystem.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/README_fr.md#_snippet_8

LANGUAGE: python
CODE:
```
from python_a2a import AgentCard, A2AServer, run_server
from python_a2a.discovery import AgentRegistry, run_registry, enable_discovery, DiscoveryClient
import threading
import time

# Créer un serveur de registre
registry = AgentRegistry(
    name="A2A Registry Server",
    description="Registre central pour la découverte d'agents"
)

# Démarrer le registre dans un thread d'arrière-plan
registry_port = 8000
thread = threading.Thread(
    target=lambda: run_registry(registry, host="0.0.0.0", port=registry_port),
    daemon=True
)
thread.start()
time.sleep(1)  # Permettre au registre de démarrer

# Créer un agent d'exemple
agent_card = AgentCard(
    name="Weather Agent",
    description="Provides weather information",
    url="http://localhost:8001",
    version="1.0.0",
    capabilities={
        "weather_forecasting": True,
        "google_a2a_compatible": True  # Activer la compatibilité A2A de Google
    }
)
agent = A2AServer(agent_card=agent_card)

# Activer la découverte - cela enregistre l'agent dans le registre
registry_url = f"http://localhost:{registry_port}"
discovery_client = enable_discovery(agent, registry_url=registry_url)

# Démarrer l'agent dans un thread séparé
agent_thread = threading.Thread(
    target=lambda: run_server(agent, host="0.0.0.0", port=8001),
    daemon=True
)
agent_thread.start()
time.sleep(1)  # Permettre à l'agent de démarrer

# Créer un client de découverte pour trouver des agents
client = DiscoveryClient(agent_card=None)  # Aucune carte d'agent nécessaire pour la découverte seule
client.add_registry(registry_url)

# Découvrir tous les agents
agents = client.discover()
print(f"{len(agents)} agents découverts:")
for agent in agents:
    print(f"- {agent.name} à {agent.url}")
    print(f"  Capacités: {agent.capabilities}")
```

----------------------------------------

TITLE: Setup Python A2A for Development
DESCRIPTION: Clone the repository and set up a development environment using UV. This includes creating a virtual environment and installing the package in editable mode with development dependencies.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/README.md#_snippet_1

LANGUAGE: bash
CODE:
```
# Clone the repository
git clone https://github.com/themanojdesai/python-a2a.git
cd python-a2a

# Create a virtual environment and install development dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

----------------------------------------

TITLE: Development Installation
DESCRIPTION: Sets up the Python A2A library for development purposes. This involves cloning the repository, creating a virtual environment using UV, and installing the library in editable mode with development dependencies.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/__wiki__/Installation.md#_snippet_3

LANGUAGE: bash
CODE:
```
git clone https://github.com/themanojdesai/python-a2a.git
cd python-a2a
uv venv
uv install -e ".[dev]"
```

----------------------------------------

TITLE: Install and Start Agent Flow
DESCRIPTION: Installs the python-a2a package and starts the Agent Flow UI. The UI provides a visual editor for building and managing agent workflows.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/python_a2a/agent_flow/README.md#_snippet_0

LANGUAGE: bash
CODE:
```
# Install python-a2a
pip install python-a2a

# Or install in development mode
pip install -e .

# Start the Agent Flow UI
a2a ui
```

----------------------------------------

TITLE: Bash: Python A2A Installation Commands
DESCRIPTION: Provides common installation commands for the Python A2A library using pip. This includes installing the base package, server extras, LLM integrations, MCP support, and all dependencies.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/examples/README.md#_snippet_45

LANGUAGE: bash
CODE:
```
# For basic examples
pip install python-a2a

# For server examples
pip install "python-a2a[server]"

# For LLM integration
pip install "python-a2a[openai]" "python-a2a[anthropic]" "python-a2a[bedrock]"

# For MCP (tool) support
pip install "python-a2a[mcp]"

# For everything
pip install "python-a2a[all]"
```

----------------------------------------

TITLE: Development Setup for Python A2A
DESCRIPTION: Steps to clone the repository, create a virtual environment, install development dependencies, and prepare a branch for contributions. This process ensures a consistent development environment.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/CONTRIBUTING.md#_snippet_0

LANGUAGE: bash
CODE:
```
git clone git@github.com:YOUR_USERNAME/python-a2a.git
cd python-a2a
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
git checkout -b name-of-your-bugfix-or-feature
```

----------------------------------------

TITLE: Run A2A Streaming Examples
DESCRIPTION: Demonstrates how to execute individual A2A streaming example scripts from the command line.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/examples/streaming/README.md#_snippet_1

LANGUAGE: bash
CODE:
```
python 01_basic_streaming.py

python 05_streaming_ui_integration.py

python 06_distributed_streaming.py
```

----------------------------------------

TITLE: Troubleshooting Installation
DESCRIPTION: Provides common commands to resolve installation issues. This includes upgrading pip, creating and activating a virtual environment, and checking for dependency conflicts.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/__wiki__/Installation.md#_snippet_6

LANGUAGE: bash
CODE:
```
pip install --upgrade pip
```

LANGUAGE: bash
CODE:
```
python -m venv venv && source venv/bin/activate
```

LANGUAGE: bash
CODE:
```
pip check
```

----------------------------------------

TITLE: Build Documentation (Bash)
DESCRIPTION: Navigates to the docs directory, installs documentation dependencies, and builds the HTML documentation. This step ensures that all documentation is up-to-date and correctly rendered.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/PUBLICATION_GUIDE.md#_snippet_1

LANGUAGE: bash
CODE:
```
cd docs
uv pip install -r requirements.txt
make html
```

----------------------------------------

TITLE: Create LangChain Agent with Tools and Convert to A2A Server
DESCRIPTION: Demonstrates creating a LangChain agent with custom and standard tools (calculator, search, Wikipedia), converting it to an A2A server, and enabling streaming. It includes LLM setup, prompt creation, agent execution, and A2A server configuration with an AgentCard.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/docs/examples/langchain_agents.rst#_snippet_0

LANGUAGE: python
CODE:
```
#!/usr/bin/env python
"""
LangChain Agent with Tools Example

This example demonstrates how to create a LangChain agent with various tools
and convert it to an A2A server with streaming support.
"""
# Import required components
from python_a2a import run_server, AgentCard, AgentSkill, A2AClient
from python_a2a.langchain import to_a2a_server

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.tools import DuckDuckGoSearchRun, WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import BaseTool

# Step 1: Create a custom calculator tool
class CalculatorTool(BaseTool):
    name = "calculator"
    description = "Useful for performing mathematical calculations."
    
    def _run(self, query: str) -> str:
        """Calculate the result of a mathematical expression."""
        try:
            return str(eval(query))
        except Exception as e:
            return f"Error evaluating expression: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        """Run calculator asynchronously."""
        return self._run(query)

# Step 2: Create all tools
wikipedia_tool = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
search_tool = DuckDuckGoSearchRun()
calculator_tool = CalculatorTool()

tools = [calculator_tool, wikipedia_tool, search_tool]

# Step 3: Create the LLM and agent
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0,
    streaming=True  # Enable streaming
)

# Create prompt - agent_scratchpad is required for the agent to track tool usage
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant with tools."),
    ("human", "{input}"),
    ("ai", "{agent_scratchpad}")
])

# Create agent and executor
agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True
)

# Step 4: Convert to A2A server
a2a_server = to_a2a_server(agent_executor)

# Step 5: Add agent card for better API discovery
a2a_server.agent_card = AgentCard(
    name="Research Assistant",
    description="An assistant with research capabilities",
    url="http://localhost:5000",
    version="1.0.0",
    skills=[
        AgentSkill(
            name="Web Research",
            description="Find information on the internet",
            examples=["What is quantum computing?"]
        ),
        AgentSkill(
            name="Calculations",
            description="Perform mathematical calculations",
            examples=["Calculate 15% of 67.50"]
        )
    ],
    capabilities={"streaming": True}
)

# Step 6: Run the server
run_server(a2a_server, host="0.0.0.0", port=5000)

```

----------------------------------------

TITLE: Setup Virtual Environment and Install Dependencies
DESCRIPTION: Creates a Python virtual environment, activates it, and installs the project's development dependencies using pip.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/docs/contributing.rst#_snippet_1

LANGUAGE: bash
CODE:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

----------------------------------------

TITLE: Install Publishing Tools (Bash)
DESCRIPTION: Installs necessary tools for building and publishing Python packages using uv and pip. Requires PyPI repository permissions.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/PUBLICATION_GUIDE.md#_snippet_0

LANGUAGE: bash
CODE:
```
uv pip install build twine
```

----------------------------------------

TITLE: Component-Specific Installation
DESCRIPTION: Installs Python A2A with optional components using pip extras. This allows users to install only the necessary features, such as server support, LLM provider integrations (OpenAI, Anthropic, Bedrock), or protocol/framework support (MCP, LangChain).

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/__wiki__/Installation.md#_snippet_1

LANGUAGE: bash
CODE:
```
pip install "python-a2a[server]"
```

LANGUAGE: bash
CODE:
```
pip install "python-a2a[openai]"
```

LANGUAGE: bash
CODE:
```
pip install "python-a2a[anthropic]"
```

LANGUAGE: bash
CODE:
```
pip install "python-a2a[bedrock]"
```

LANGUAGE: bash
CODE:
```
pip install "python-a2a[mcp]"
```

LANGUAGE: bash
CODE:
```
pip install "python-a2a[langchain]"
```

----------------------------------------

TITLE: Running Examples with Bash
DESCRIPTION: Provides instructions on how to execute the provided examples. It involves navigating to the specific example directory and running the Python script using the bash command line.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/__wiki__/Examples.md#_snippet_11

LANGUAGE: bash
CODE:
```
# Example:
cd examples/getting_started
python hello_a2a.py
```

----------------------------------------

TITLE: Install Python A2A with Optional Dependencies
DESCRIPTION: Installs python-a2a with specific optional features by including extras in the pip command. This allows users to install only the dependencies needed for particular integrations, such as server support, OpenAI, Anthropic, AWS Bedrock, or MCP.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/docs/installation.rst#_snippet_1

LANGUAGE: bash
CODE:
```
pip install "python-a2a[server]"
```

LANGUAGE: bash
CODE:
```
pip install "python-a2a[openai]"
```

LANGUAGE: bash
CODE:
```
pip install "python-a2a[anthropic]"
```

LANGUAGE: bash
CODE:
```
pip install "python-a2a[bedrock]"
```

LANGUAGE: bash
CODE:
```
pip install "python-a2a[mcp]"
```

LANGUAGE: bash
CODE:
```
pip install "python-a2a[all]"
```

----------------------------------------

TITLE: Install Python A2A with MCP Support - Bash
DESCRIPTION: Installs `python-a2a` and the required dependencies for Model Context Protocol (MCP) support. This installation is done via pip using the `[mcp]` extra.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/docs/installation.rst#_snippet_5

LANGUAGE: bash
CODE:
```
pip install "python-a2a[mcp]"
```

----------------------------------------

TITLE: Dockerfile for Python A2A with UV
DESCRIPTION: A Dockerfile example demonstrating how to set up a Python 3.9 environment, install UV, and then install python-a2a with all optional dependencies. It configures the PATH and sets the working directory for application deployment.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/docs/uv-installation.rst#_snippet_11

LANGUAGE: dockerfile
CODE:
```
FROM python:3.9-slim

# Install UV
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Set environment variables
ENV PATH="/root/.cargo/bin:${PATH}"

# Install Python A2A
WORKDIR /app
COPY . .
RUN uv pip install ".[all]"

# Run your application
CMD ["python", "your_app.py"]
```

----------------------------------------

TITLE: Install Python A2A with AWS Bedrock - Bash
DESCRIPTION: Installs `python-a2a` including the optional dependencies for AWS Bedrock integration. This installation uses pip with the `[bedrock]` extra.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/docs/installation.rst#_snippet_4

LANGUAGE: bash
CODE:
```
pip install "python-a2a[bedrock]"
```

----------------------------------------

TITLE: Connect Python A2A Client to Agent
DESCRIPTION: Shows how to instantiate an `A2AClient` to connect to a running A2A agent. It covers viewing agent information and sending queries to the agent.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/docs/quickstart.rst#_snippet_1

LANGUAGE: python
CODE:
```
from python_a2a import A2AClient

# Create a client connected to an A2A-compatible agent
client = A2AClient("http://localhost:5000")

# View agent information
print(f"Connected to: {client.agent_card.name}")
print(f"Description: {client.agent_card.description}")
print(f"Skills: {[skill.name for skill in client.agent_card.skills]}")

# Ask a question
response = client.ask("What's the weather in Paris?")
print(f"Response: {response}")
```

----------------------------------------

TITLE: Install Python A2A for Development
DESCRIPTION: Installs the python-a2a package in editable mode along with development dependencies. This is recommended for contributors or users who need to run tests or modify the library's source code.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/docs/installation.rst#_snippet_2

LANGUAGE: bash
CODE:
```
git clone https://github.com/themanojdesai/python-a2a.git
cd python-a2a
pip install -e ".[dev]"
```

----------------------------------------

TITLE: Create and Run Registry Server with Sample Agent (Python)
DESCRIPTION: Demonstrates setting up a registry server in a separate thread and running a sample agent that registers with it. It covers agent initialization with `AgentCard` and server execution using `run_server`.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/docs/examples/agent_discovery.rst#_snippet_0

LANGUAGE: python
CODE:
```
from python_a2a import AgentCard, A2AServer, run_server, Message, TextContent, MessageRole
from python_a2a.discovery import AgentRegistry, run_registry, enable_discovery
import threading

# Create a simple agent that will register with the registry
class SampleAgent(A2AServer):
    """A sample agent that registers with the registry."""
    
    def __init__(self, name: str, description: str, url: str):
        """Initialize the sample agent."""
        agent_card = AgentCard(
            name=name,
            description=description,
            url=url,
            version="1.0.0",
            capabilities={
                "streaming": False,
                "pushNotifications": False,
                "stateTransitionHistory": False,
                "google_a2a_compatible": True,
                "parts_array_format": True
            }
        )
        super().__init__(agent_card=agent_card)
    
    def handle_message(self, message: Message) -> Message:
        """Handle incoming messages."""
        return Message(
            content=TextContent(
                text=f"Hello from {self.agent_card.name}! I received: {message.content.text}"
            ),
            role=MessageRole.AGENT,
            parent_message_id=message.message_id,
            conversation_id=message.conversation_id
        )

# Start a registry server in a separate thread
registry_port = 8000
registry_thread = threading.Thread(
    target=lambda: run_registry(
        AgentRegistry(name="A2A Registry Server"),
        host="0.0.0.0", 
        port=registry_port
    ),
    daemon=True
)
registry_thread.start()

# Create and run an agent that registers with the registry
agent = SampleAgent(
    name="Sample Agent",
    description="Sample agent that demonstrates discovery",
    url="http://localhost:8001"
)

# Enable discovery - this registers the agent with the registry
registry_url = f"http://localhost:{registry_port}"
discovery_client = enable_discovery(agent, registry_url=registry_url)

# Run the agent
run_server(agent, host="0.0.0.0", port=8001)
```

----------------------------------------

TITLE: Python: Basic Streaming Example
DESCRIPTION: Illustrates the fundamental implementation of streaming responses in A2A. This example is a starting point for understanding real-time data flow.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/examples/README.md#_snippet_38

LANGUAGE: python
CODE:
```
# streaming/01_basic_streaming.py
# Basic streaming example
# Implement streaming responses
```

----------------------------------------

TITLE: Setup Development Environment with UV
DESCRIPTION: Steps to create a virtual environment and install development dependencies using the UV package manager. This ensures a consistent and isolated development setup.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/__wiki__/Contributing.md#_snippet_1

LANGUAGE: bash
CODE:
```
uv venv
uv install -e ".[dev]"
```

----------------------------------------

TITLE: Connect and Interact with A2A Client in Python
DESCRIPTION: This example shows how to create an A2A client to connect to a running A2A agent. It demonstrates fetching agent information like name, description, and skills, and then sending messages to the agent to get responses.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/docs/examples/simple.rst#_snippet_1

LANGUAGE: python
CODE:
```
from python_a2a import A2AClient

# Create a client
client = A2AClient("http://localhost:5000")

# Print agent information
print(f"Connected to: {client.agent_card.name}")
print(f"Description: {client.agent_card.description}")
print(f"Skills: {[skill.name for skill in client.agent_card.skills]}")

# Send a greeting
response = client.ask("Hello there! My name is Alice.")
print(f"Response: {response}")

# Send another message
response = client.ask("What can you do?")
print(f"Response: {response}")
```

----------------------------------------

TITLE: Setting up Agent Discovery and Registry (Python)
DESCRIPTION: Demonstrates how to create and run an `AgentRegistry` server for agent discovery. It shows starting the registry in a background thread and includes necessary imports for discovery components.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/README.md#_snippet_30

LANGUAGE: python
CODE:
```
from python_a2a import AgentCard, A2AServer, run_server
from python_a2a.discovery import AgentRegistry, run_registry, enable_discovery, DiscoveryClient
import threading
import time

# Create a registry server
registry = AgentRegistry(
    name="A2A Registry Server",
    description="Central registry for agent discovery"
)

# Run the registry in a background thread
registry_port = 8000
thread = threading.Thread(
    target=lambda: run_registry(registry, host="0.0.0.0", port=registry_port),
    daemon=True
)
thread.start()
time.sleep(1)  # Let the registry start
```

----------------------------------------

TITLE: Run Weather Agent
DESCRIPTION: Executes the Python script to start the A2A weather agent. The agent will be available at http://localhost:5000 for querying weather information.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/__wiki__/Quickstart.md#_snippet_5

LANGUAGE: bash
CODE:
```
python weather_agent.py
```

----------------------------------------

TITLE: Discover Agents from Registry (Python)
DESCRIPTION: Shows how to use `DiscoveryClient` to connect to a registry, discover available agents, and filter them based on capabilities. Requires a running registry server.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/docs/examples/agent_discovery.rst#_snippet_1

LANGUAGE: python
CODE:
```
from python_a2a.discovery import DiscoveryClient, AgentRegistry

# Create a discovery client (without registering)
discovery_client = DiscoveryClient(agent_card=None)  # You can also pass your own agent card
discovery_client.add_registry("http://localhost:8000")

# Discover all agents
agents = discovery_client.discover()

for agent in agents:
    print(f"Found agent: {agent.name} at {agent.url}")
    print(f"Capabilities: {agent.capabilities}")
    
# You can also filter agents by capabilities
weather_agents = [agent for agent in agents 
                 if agent.capabilities.get("weather_forecasting")]

for agent in weather_agents:
    print(f"Found weather agent: {agent.name} at {agent.url}")
```

----------------------------------------

TITLE: Verify Python A2A Installation - Python
DESCRIPTION: Executes Python code to import the `python_a2a` library and print its version attribute. This is a standard method to confirm successful installation and check the installed package version from the command line or within a script.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/docs/installation.rst#_snippet_8

LANGUAGE: python
CODE:
```
import python_a2a
print(python_a2a.__version__)
```

----------------------------------------

TITLE: Verify Installation
DESCRIPTION: Checks if the Python A2A library has been installed correctly by importing it and printing its version number. This is a simple verification step to ensure the package is accessible in the Python environment.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/__wiki__/Installation.md#_snippet_4

LANGUAGE: python
CODE:
```
import python_a2a

# Should print the current version
print(python_a2a.__version__)
```

----------------------------------------

TITLE: Verify Python A2A Installation
DESCRIPTION: Verifies that the python-a2a library has been installed correctly by importing it and printing its version number. This confirms that the package is accessible in the Python environment.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/docs/installation.rst#_snippet_3

LANGUAGE: python
CODE:
```
import python_a2a
print(python_a2a.__version__)
```

----------------------------------------

TITLE: Setup Development Environment with Pip
DESCRIPTION: Alternative steps to create a virtual environment and install development dependencies using Python's built-in venv and pip. Includes instructions for activating the environment on different operating systems.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/__wiki__/Contributing.md#_snippet_2

LANGUAGE: bash
CODE:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

----------------------------------------

TITLE: Langchain Agent Executor Setup
DESCRIPTION: This snippet shows how to configure a Langchain AgentExecutor, incorporating chat history and memory into the prompt and executor setup. It utilizes ChatPromptTemplate and MessagesPlaceholder for managing conversational context.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/docs/examples/langchain_agents.rst#_snippet_9

LANGUAGE: python
CODE:
```
       return_messages=True
       )
       
       # Include memory in the prompt
       prompt = ChatPromptTemplate.from_messages([
           ("system", "System prompt"),
           MessagesPlaceholder(variable_name="chat_history"),
           ("human", "{input}")
       ])
       
       # Add memory to agent executor
       agent_executor = AgentExecutor(
           agent=agent,
           tools=tools,
           memory=memory
       )
```

----------------------------------------

TITLE: GitHubMCPServer Example
DESCRIPTION: Demonstrates the correct usage of GitHubMCPServer with context management and error handling for fetching authenticated user details. Includes a comparison with an incomplete example.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/DOCUMENTATION.md#_snippet_3

LANGUAGE: python
CODE:
```
from python_a2a.mcp.providers import GitHubMCPServer

async def github_example():
    """Complete example with error handling and context management."""
    async with GitHubMCPServer(token="your-token") as github:
        try:
            user = await github.get_authenticated_user()
            print(f"Authenticated as: {user['login']}")
        except Exception as e:
            print(f"Error: {e}")

# Bad: Incomplete example without context
# github = GitHubMCPServer()
# user = github.get_user()  # Missing token, no error handling
```

----------------------------------------

TITLE: Start Agent Flow UI with Options
DESCRIPTION: Starts the Agent Flow UI server, allowing customization of the port, host, storage directory, and browser behavior.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/python_a2a/agent_flow/README.md#_snippet_1

LANGUAGE: bash
CODE:
```
a2a ui --port 8080 --host localhost --storage-dir ./workflows --no-browser --debug
```

----------------------------------------

TITLE: Basic MCP Server and Client Example
DESCRIPTION: A complete example demonstrating the setup of a simple MCP server using FastMCP for basic arithmetic operations and a corresponding client script to interact with these tools.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/__wiki__/MCP-Integration.md#_snippet_3

LANGUAGE: python
CODE:
```
# Create the MCP server (calculator_mcp.py)
from python_a2a.mcp import FastMCP
from python_a2a import run_server

calculator = FastMCP(name="Calculator MCP")

@calculator.tool()
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b

@calculator.tool()
def subtract(a: float, b: float) -> float:
    """Subtract b from a."""
    return a - b

if __name__ == "__main__":
    run_server(calculator, port=8000)
```

LANGUAGE: python
CODE:
```
# Create an MCP client (calculator_client.py)
from python_a2a.mcp import MCPClient

client = MCPClient("http://localhost:8000")

# Call the add tool
result = client.call_tool("add", {"a": 10, "b": 5})
print(f"10 + 5 = {result}")

# Call the subtract tool
result = client.call_tool("subtract", {"a": 10, "b": 5})
print(f"10 - 5 = {result}")
```

----------------------------------------

TITLE: Development Setup with UV
DESCRIPTION: Sets up the python-a2a project in development mode using UV. This includes cloning the repository, creating a virtual environment, and installing the package in editable mode with development dependencies.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/docs/uv-installation.rst#_snippet_9

LANGUAGE: bash
CODE:
```
git clone https://github.com/themanojdesai/python-a2a.git
cd python-a2a

uv venv create .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"

# Run tests
uv pip run pytest
```

----------------------------------------

TITLE: Run Combined Agent Example
DESCRIPTION: This Python code snippet demonstrates how to execute a combined agent. It includes a delay to allow servers to start and then iterates through a list of questions, printing the question and the agent's answer. This showcases a typical workflow for interacting with an agent.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/__wiki__/LangChain-Integration.md#_snippet_13

LANGUAGE: python
CODE:
```
# 8. Run the combined agent
if __name__ == "__main__":
    # Wait for servers to start
    import time
    time.sleep(2)
    
    # Ask questions that require different tools
    questions = [
        "What's the weather like in Tokyo?",
        "What is 125 + 37?",
        "What is 200 - 45?",
        "Calculate the square root of 144"
    ]
    
    for question in questions:
        print(f"\nQuestion: {question}")
        result = agent.run(question)
        print(f"Answer: {result}")
```

----------------------------------------

TITLE: Python: Simple Server Example
DESCRIPTION: An example for building your own A2A agent server. This snippet is a foundational example for backend developers to understand the core protocol.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/examples/README.md#_snippet_35

LANGUAGE: python
CODE:
```
# getting_started/simple_server.py
# Simple server example
# Build your own agent
```

----------------------------------------

TITLE: Install python-a2a Library
DESCRIPTION: Instructions to install the `python-a2a` library using pip. LangChain is automatically included as a dependency, so no separate installation is needed for LangChain components.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/README.md#_snippet_13

LANGUAGE: bash
CODE:
```
pip install python-a2a
# That's it! LangChain is included automatically
```

----------------------------------------

TITLE: GitHub MCP Provider - Production Examples
DESCRIPTION: Provides comprehensive examples of using the GitHub MCP Provider for various operations like repository management, issue tracking, and file manipulation. It demonstrates production-ready usage with specific API calls.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/README.md#_snippet_22

LANGUAGE: python
CODE:
```
from python_a2a.mcp.providers import GitHubMCPServer

# Production-ready GitHub operations
async with GitHubMCPServer(token="ghp_your_token") as github:
    # Repository management
    repo = await github.create_repository("my-project", "A new project")
    branches = await github.list_branches("owner", "repo")
    
    # Issue tracking
    issues = await github.list_issues("owner", "repo", state="open")
    issue = await github.create_issue("owner", "repo", "Bug Report", "Description")
    
    # Pull request workflow
    pr = await github.create_pull_request(
        "owner", "repo", "Feature: Add new API", "feature", "main"
    )
    
    # File operations
    content = await github.get_file_contents("owner", "repo", "README.md")
    await github.create_or_update_file(
        "owner", "repo", "docs/api.md", "# API Documentation", "Add API docs"
    )
```

----------------------------------------

TITLE: Makefile Commands for Python A2A
DESCRIPTION: Common development tasks for python-a2a managed via a Makefile, utilizing UV for installations and testing. Includes setup, testing, formatting, and linting.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/docs/uv-installation.rst#_snippet_12

LANGUAGE: bash
CODE:
```
# Set up development environment
make setup

# Run tests
make test

# Format code
make format

# Lint code
make lint
```

----------------------------------------

TITLE: Python A2A Decorators for Agent/Skill Creation
DESCRIPTION: Explains the use of `@agent` and `@skill` decorators for defining A2A agents and their capabilities. This example shows a calculator agent with an 'Add' skill.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/docs/quickstart.rst#_snippet_3

LANGUAGE: python
CODE:
```
from python_a2a import agent, skill, A2AServer, run_server
from python_a2a import TaskStatus, TaskState

@agent(
    name="Calculator",
    description="Performs calculations",
    version="1.0.0"
)
class CalculatorAgent(A2AServer):
    
    @skill(
        name="Add",
        description="Add two numbers",
        tags=["math", "addition"]
    )
    def add(self, a, b):
        """
        Add two numbers together.
        
        Examples:
            "What is 5 + 3?"
            "Add 10 and 20"
        """
        return float(a) + float(b)
    
    def handle_task(self, task):
        # Implementation details...
        pass

# Run the server
if __name__ == "__main__":
    calculator = CalculatorAgent()
    run_server(calculator, port=5000)
```

----------------------------------------

TITLE: Python: Basic Workflow Example
DESCRIPTION: Demonstrates the creation of basic agent workflows. This example provides a foundation for orchestrating sequences of agent actions.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/examples/README.md#_snippet_43

LANGUAGE: python
CODE:
```
# agent_network/basic_workflow.py
# Basic workflow example
# Create agent workflows
```

----------------------------------------

TITLE: Run LangChain Agent Server
DESCRIPTION: Command to set the OpenAI API key and run the Python script for the LangChain agent server.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/docs/examples/langchain_agents.rst#_snippet_1

LANGUAGE: bash
CODE:
```
export OPENAI_API_KEY=your_api_key
python langchain_agent_with_tools.py
```

----------------------------------------

TITLE: Browserbase MCP Provider - Production Examples
DESCRIPTION: Showcases production-ready browser automation and web scraping capabilities using the Browserbase MCP Provider. Examples cover navigation, taking screenshots, interacting with elements, and extracting text content.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/README.md#_snippet_23

LANGUAGE: python
CODE:
```
from python_a2a.mcp.providers import BrowserbaseMCPServer

# Production-ready browser automation
async with BrowserbaseMCPServer(
    api_key="your-api-key",
    project_id="your-project"
) as browser:
    # Navigation and interaction
    await browser.navigate("https://example.com")
    
    # Take screenshots and snapshots
    screenshot = await browser.take_screenshot()
    snapshot = await browser.create_snapshot()
    
    # Element interactions (requires snapshot refs)
    await browser.click_element("Submit button", "ref_from_snapshot")
    await browser.type_text("Email input", "ref_from_snapshot", "user@example.com")
    
    # Data extraction
    title = await browser.get_text("h1")
    page_content = await browser.get_text("body")
```

----------------------------------------

TITLE: OpenAI Agent Example
DESCRIPTION: Demonstrates how to create GPT-powered agents by connecting to OpenAI. This example showcases AI-powered agent integration with A2A.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/examples/README.md#_snippet_14

LANGUAGE: python
CODE:
```
# Code for ai_powered_agents/openai_agent.py not provided in input text.
```

----------------------------------------

TITLE: Running Example Validation Commands
DESCRIPTION: Provides bash commands to execute the example validation script. It covers running all examples, filtering by category, skipping slow tests, enabling concurrency, and enabling verbose output for debugging.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/examples/README.md#_snippet_46

LANGUAGE: bash
CODE:
```
python validate_all_examples.py
```

LANGUAGE: bash
CODE:
```
python validate_all_examples.py --category streaming
```

LANGUAGE: bash
CODE:
```
python validate_all_examples.py --skip-slow
```

LANGUAGE: bash
CODE:
```
python validate_all_examples.py --concurrent 3
```

LANGUAGE: bash
CODE:
```
python validate_all_examples.py --verbose
```

----------------------------------------

TITLE: Run Streaming Client
DESCRIPTION: Executes the Python script to demonstrate streaming responses from an A2A agent. This client connects to the agent and prints chunks of data as they are received.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/__wiki__/Quickstart.md#_snippet_8

LANGUAGE: bash
CODE:
```
python streaming_client.py
```

----------------------------------------

TITLE: Setting up Python A2A Agent Discovery and Registration
DESCRIPTION: This comprehensive example shows how to initialize and run an `AgentRegistry` server in a background thread, create an `A2AServer` with an `AgentCard`, enable discovery to register the agent with the registry, run the agent server, and finally use a `DiscoveryClient` to find registered agents.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/README_es.md#_snippet_10

LANGUAGE: python
CODE:
```
from python_a2a import AgentCard, A2AServer, run_server
from python_a2a.discovery import AgentRegistry, run_registry, enable_discovery, DiscoveryClient
import threading
import time

# Create a registry server
registry = AgentRegistry(
    name="A2A Registry Server",
    description="Central registry for agent discovery"
)

# Run the registry in a background thread
registry_port = 8000
thread = threading.Thread(
    target=lambda: run_registry(registry, host="0.0.0.0", port=registry_port),
    daemon=True
)
thread.start()
time.sleep(1)  # Let the registry start

# Create a sample agent
agent_card = AgentCard(
    name="Weather Agent",
    description="Provides weather information",
    url="http://localhost:8001",
    version="1.0.0",
    capabilities={
        "weather_forecasting": True,
        "google_a2a_compatible": True  # Enable Google A2A compatibility
    }
)
agent = A2AServer(agent_card=agent_card)

# Enable discovery - this registers with the registry
registry_url = f"http://localhost:{registry_port}"
discovery_client = enable_discovery(agent, registry_url=registry_url)

# Run the agent in a separate thread
agent_thread = threading.Thread(
    target=lambda: run_server(agent, host="0.0.0.0", port=8001),
    daemon=True
)
agent_thread.start()
time.sleep(1)  # Let the agent start

# Create a discovery client for discovering agents
client = DiscoveryClient(agent_card=None)  # No agent card needed for discovery only
client.add_registry(registry_url)

# Discover all agents
agents = client.discover()
print(f"Discovered {len(agents)} agents:")
for agent in agents:
    print(f"- {agent.name} at {agent.url}")
    print(f"  Capabilities: {agent.capabilities}")
```

----------------------------------------

TITLE: Run A2A Server and Connect Client
DESCRIPTION: Shows the conceptual setup for running an A2A agent as a server and connecting to it with a client. It uses `run_server` to start the agent and `A2AClient` to establish a connection to the server's endpoint.

SOURCE: https://github.com/themanojdesai/python-a2a/blob/main/notebooks/01_basic_agent_conversation.ipynb#_snippet_14

LANGUAGE: python
CODE:
```
# Run the server (in a separate process)
run_server(echo_agent, host="0.0.0.0", port=5000)

# Connect with a client
client = A2AClient("http://localhost:5000/a2a")

# Send a message
response = client.send_message(test_message)
```