========================
CODE SNIPPETS
========================
TITLE: Python Quickstart Tutorial
DESCRIPTION: This snippet refers to a Python Quickstart Tutorial, likely demonstrating how to get started with the A2A protocol using Python. It is a community contribution.

SOURCE: https://a2a-protocol.org/latest/community

LANGUAGE: Python
CODE:
```
# Placeholder for Python Quickstart Tutorial code
# This would typically involve setting up an agent, defining its capabilities,
# and demonstrating communication with other agents using the A2A protocol.

# Example structure:
# from a2a import Agent
# 
# agent = Agent(name="MyAgent", capabilities=["task_executor"])
# agent.start()
# 
# # Code to interact with other agents would follow...
```

----------------------------------------

TITLE: Python A2A Server Quickstart
DESCRIPTION: This snippet provides a foundational example of setting up and running an A2A server using the Python SDK. It covers the essential steps for creating a basic agent that can receive and process tasks.

SOURCE: https://a2a-protocol.org/latest/tutorials/python/1-introduction

LANGUAGE: Python
CODE:
```
from a2a.server import A2AServer

# Define your agent's skills and logic here
class EchoAgent:
    def echo(self, message: str) -> str:
        return f"Echo: {message}"

# Initialize the A2A server
server = A2AServer(agent=EchoAgent())

# Start the server (this would typically be in a main execution block)
# server.start()
print("A2A Server initialized. Ready to start.")
```

----------------------------------------

TITLE: A2A Tutorial: Python Setup
DESCRIPTION: This Python code snippet demonstrates the initial setup for interacting with the A2A protocol, likely involving importing necessary libraries and configuring agent connections. It serves as a starting point for developing A2A-compliant applications in Python.

SOURCE: https://a2a-protocol.org/latest/topics/what-is-a2a

LANGUAGE: python
CODE:
```
from a2a.client import A2AClient

# Initialize the client
client = A2AClient(base_url="http://localhost:8000")

```

----------------------------------------

TITLE: Install A2A Python SDK and Dependencies
DESCRIPTION: Installs the necessary Python dependencies, including the A2A SDK, using pip. This command should be run within an activated virtual environment.

SOURCE: https://a2a-protocol.org/latest/tutorials/python/2-setup

LANGUAGE: Shell
CODE:
```
pip install -e .[dev]
```

----------------------------------------

TITLE: Verify A2A SDK Installation
DESCRIPTION: Verifies that the A2A Python SDK has been installed correctly by attempting to import the `a2a` package and printing a success message. This is done within a Python interpreter.

SOURCE: https://a2a-protocol.org/latest/tutorials/python/2-setup

LANGUAGE: Python
CODE:
```
import a2a; print('A2A SDK imported successfully')
```

----------------------------------------

TITLE: A2A Tutorial: Python Start Server
DESCRIPTION: This Python code demonstrates how to start an A2A server, making the agent discoverable and ready to receive requests. It typically involves running an ASGI or WSGI application that hosts the agent's functionalities.

SOURCE: https://a2a-protocol.org/latest/topics/what-is-a2a

LANGUAGE: python
CODE:
```
from a2a.server import A2AServer
from your_agent_module import agent # Assuming 'agent' is defined in your_agent_module

server = A2AServer(agent=agent)

if __name__ == "__main__":
    server.run(port=8000)

```

----------------------------------------

TITLE: Go Example
DESCRIPTION: This snippet provides an example of using the A2A protocol with the Go programming language. It demonstrates the cross-language compatibility and implementation in Go.

SOURCE: https://a2a-protocol.org/latest/community

LANGUAGE: Go
CODE:
```
// Placeholder for Go example code
// This would involve using a Go library for A2A to create and manage agents.

// Example structure:
// package main
// 
// import (
// 	"fmt"
// 	"github.com/a2a/go-sdk"
// )
// 
// func main() {
// 	agent, err := sdk.NewAgent("MyGoAgent")
// 	if err != nil {
// 		panic(err)
// 	}
// 	agent.Start()
// 	fmt.Println("Go agent started")
// 	// Code to interact with other agents would follow...
// }
```

----------------------------------------

TITLE: Python Agent2Agent (A2A) Protocol Tutorial
DESCRIPTION: This section provides a tutorial for using the Agent2Agent (A2A) Protocol in Python. It covers setup, defining agent skills and cards, using the agent executor, starting and interacting with the server, and handling streaming and multi-turn conversations.

SOURCE: https://a2a-protocol.org/latest/topics/a2a-and-mcp

LANGUAGE: Python
CODE:
```
# This is a placeholder for actual Python code examples from the tutorial.
# The tutorial covers setup, Agent Skills & Agent Card, Agent Executor,
# Start Server, Interact with Server, and Streaming & Multiturn.

# Example of a hypothetical Agent Card structure:
# agent_card = {
#     "name": "Billing Inquiry Agent",
#     "description": "Handles complex billing inquiries.",
#     "skills": [
#         "process_billing_dispute",
#         "check_account_balance"
#     ],
#     "communication_modes": ["text", "structured_data"]
# }

# Example of a hypothetical interaction:
# response = agent_client.send_message("Hello, I have a billing issue.")
# print(response.text)

```

----------------------------------------

TITLE: Start LangGraph Agent Server
DESCRIPTION: This command initiates the LangGraph agent server, which typically runs on http://localhost:10000. This server facilitates the A2A protocol interactions for the LangGraph example.

SOURCE: https://a2a-protocol.org/latest/tutorials/python/7-streaming-and-multiturn

LANGUAGE: Python
CODE:
```
python
```

----------------------------------------

TITLE: A2A Protocol Tutorial (Python)
DESCRIPTION: This section provides a tutorial for the Agent2Agent (A2A) Protocol using Python. It covers introduction, setup, agent skills, agent card, agent executor, starting and interacting with the server, streaming, and multiturn operations.

SOURCE: https://a2a-protocol.org/latest/partners

LANGUAGE: Python
CODE:
```
This section contains a tutorial for the Agent2Agent (A2A) Protocol using Python. It covers:
- Introduction
- Setup
- Agent Skills & Agent Card
- Agent Executor
- Start Server
- Interact with Server
- Streaming & Multiturn
- Next Steps
```

----------------------------------------

TITLE: Start A2A Server with Python SDK
DESCRIPTION: Demonstrates how to set up and run an A2A-compliant HTTP server using the A2A Python SDK. It utilizes the A2AStarletteApplication class, built on Starlette, and is intended to be run with an ASGI server such as Uvicorn.

SOURCE: https://a2a-protocol.org/latest/tutorials/python/5-start-server

LANGUAGE: python
CODE:
```
from a2a_protocol.starlette.app import A2AStarletteApplication
import uvicorn

# Assuming you have your agent setup (e.g., Agent Card, Agent Executor)
# app = A2AStarletteApplication(agent_executor=your_agent_executor)

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)

```

----------------------------------------

TITLE: Clone A2A Repository
DESCRIPTION: Clones the A2A Samples repository from GitHub using Git. This is a prerequisite for setting up the development environment.

SOURCE: https://a2a-protocol.org/latest/tutorials/python/2-setup

LANGUAGE: Shell
CODE:
```
git clone https://github.com/a2aproject/A2A-Samples.git
cd A2A-Samples
```

----------------------------------------

TITLE: Run Helloworld Server Command
DESCRIPTION: This command initiates the Helloworld server from the terminal. It assumes the user is in the `a2a-samples` directory and has their virtual environment activated.

SOURCE: https://a2a-protocol.org/latest/tutorials/python/5-start-server

LANGUAGE: Shell
CODE:
```
python
```

----------------------------------------

TITLE: Example Streaming Response Output (One Chunk)
DESCRIPTION: Shows an example of the expected JSON output for a single chunk of a streaming message response from the A2A protocol.

SOURCE: https://a2a-protocol.org/latest/tutorials/python/6-interact-with-server

LANGUAGE: JSON
CODE:
```
{"jsonrpc":"2.0","id":"zzzzzzzz","result":{"type":"message","role":"agent","parts":[{"type":"text","text":"Hello World"}],"messageId":"wwwwwwww","final":true}}
```

----------------------------------------

TITLE: A2A Extension Activation Response Example
DESCRIPTION: An example HTTP response indicating a successful extension activation. The response includes a 200 OK status and the 'X-A2A-Extensions' header confirming the activated extension. The body contains a JSON-RPC response.

SOURCE: https://a2a-protocol.org/latest/topics/extensions

LANGUAGE: HTTP
CODE:
```
HTTP/1.1 200 OK
Content-Type: application/json
X-A2A-Extensions: https://example.com/ext/konami-code/v1
Content-Length: 338

{
"jsonrpc":"2.0",
"id":"1",
"result":{
"kind":"message",
"messageId":"2",
"role":"agent",
"parts":[{"kind":"text","text":"That's a bingo!"}],
}
}
```

----------------------------------------

TITLE: A2A Extension Activation Request Example
DESCRIPTION: An example HTTP POST request demonstrating how a client can activate an extension by including the 'X-A2A-Extensions' header. The request body is a JSON-RPC payload specifying a message and metadata for the 'konami-code' extension.

SOURCE: https://a2a-protocol.org/latest/topics/extensions

LANGUAGE: HTTP
CODE:
```
POST /agents/eightball HTTP/1.1
Host: example.com
Content-Type: application/json
X-A2A-Extensions: https://example.com/ext/konami-code/v1
Content-Length: 519

{
"jsonrpc":"2.0",
"method":"message/send",
"id":"1",
"params":{
"message":{
"kind":"message",
"messageId":"1",
"role":"user",
"parts":[{"kind":"text","text":"Oh magic 8-ball, will it rain today?"}]
},
"metadata":{
"https://example.com/ext/konami-code/v1/code":"motherlode",
}
}
}
```

----------------------------------------

TITLE: Create and Activate Python Virtual Environment (venv)
DESCRIPTION: Demonstrates how to create and activate a Python virtual environment using the standard `venv` module. This isolates project dependencies.

SOURCE: https://a2a-protocol.org/latest/tutorials/python/2-setup

LANGUAGE: Shell
CODE:
```
python3 -m venv .venv
source .venv/bin/activate
```

LANGUAGE: Shell
CODE:
```
python -m venv .venv
.venv\Scripts\activate
```

----------------------------------------

TITLE: Python A2A Client Interaction
DESCRIPTION: This snippet demonstrates how to interact with a running A2A server using the Python SDK. It shows how to send a task to the agent and receive a response, illustrating the client-server communication flow.

SOURCE: https://a2a-protocol.org/latest/tutorials/python/1-introduction

LANGUAGE: Python
CODE:
```
from a2a.client import A2AClient

# Assuming the server is running on localhost:8000
client = A2AClient(base_url="http://localhost:8000")

async def send_message():
    try:
        response = await client.send_task(agent_id="echo_agent", task_name="echo", message="Hello A2A!")
        print(f"Received response: {response}")
    except Exception as e:
        print(f"Error interacting with server: {e}")

# To run this, you would typically use an async event loop:
# import asyncio
# asyncio.run(send_message())
print("A2A Client initialized. Ready to send tasks.")
```

----------------------------------------

TITLE: Example Non-Streaming Response Output
DESCRIPTION: Provides an example of the expected JSON output for a non-streaming message response from the A2A protocol.

SOURCE: https://a2a-protocol.org/latest/tutorials/python/6-interact-with-server

LANGUAGE: JSON
CODE:
```
{"jsonrpc":"2.0","id":"xxxxxxxx","result":{"type":"message","role":"agent","parts":[{"type":"text","text":"Hello World"}],"messageId":"yyyyyyyy"}}
```

----------------------------------------

TITLE: Example Push Notification Payload (Comprehensive)
DESCRIPTION: An example of a more comprehensive push notification payload that might include additional details about the task update.

SOURCE: https://a2a-protocol.org/latest/topics/streaming-and-async

LANGUAGE: json
CODE:
```
{
  "taskId": "task-123",
  "state": "input-required",
  "message": {
    "content": "Please provide additional input."
  },
  "artifacts": [
    {
      "mimeType": "application/json",
      "uri": "/artifacts/artifact-abc"
    }
  ]
}
```

----------------------------------------

TITLE: AgentSkill Configuration
DESCRIPTION: Details the configuration for an AgentSkill, including its description, examples, ID, input/output modes, model configuration, name, security, and tags.

SOURCE: https://a2a-protocol.org/latest/sdk/python/api/a2a

LANGUAGE: Python
CODE:
```
class AgentSkill:
    description: str
    examples: Any
    id: str
    input_modes: Any
    model_config: Any
    name: str
    output_modes: Any
    security: Any
    tags: Any
```

----------------------------------------

TITLE: Initialize and Run Helloworld Server
DESCRIPTION: This Python script sets up and runs the Helloworld A2A server. It defines agent skills, public and extended agent cards, a request handler, and the main Starlette application. The server is then launched using uvicorn.

SOURCE: https://a2a-protocol.org/latest/tutorials/python/5-start-server

LANGUAGE: Python
CODE:
```
import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from agent_executor import (
    HelloWorldAgentExecutor,  # type: ignore[import-untyped]
)


if __name__ == '__main__':
    skill = AgentSkill(
        id='hello_world',
        name='Returns hello world',
        description='just returns hello world',
        tags=['hello world'],
        examples=['hi', 'hello world'],
    )

    extended_skill = AgentSkill(
        id='super_hello_world',
        name='Returns a SUPER Hello World',
        description='A more enthusiastic greeting, only for authenticated users.',
        tags=['hello world', 'super', 'extended'],
        examples=['super hi', 'give me a super hello'],
    )

    # This will be the public-facing agent card
    public_agent_card = AgentCard(
        name='Hello World Agent',
        description='Just a hello world agent',
        url='http://localhost:9999/',
        version='1.0.0',
        default_input_modes=['text'],
        default_output_modes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],  # Only the basic skill for the public card
        supports_authenticated_extended_card=True,
    )

    # This will be the authenticated extended agent card
    # It includes the additional 'extended_skill'
    specific_extended_agent_card = public_agent_card.model_copy(
        update={
            'name': 'Hello World Agent - Extended Edition',  # Different name for clarity
            'description': 'The full-featured hello world agent for authenticated users.',
            'version': '1.0.1',  # Could even be a different version
            # Capabilities and other fields like url, default_input_modes, default_output_modes,
            # supports_authenticated_extended_card are inherited from public_agent_card unless specified here.
            'skills': [
                skill,
                extended_skill,
            ],  # Both skills for the extended card
        }
    )

    request_handler = DefaultRequestHandler(
        agent_executor=HelloWorldAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=public_agent_card,
        http_handler=request_handler,
        extended_agent_card=specific_extended_agent_card,
    )

    uvicorn.run(server.build(), host='0.0.0.0', port=9999)

```

----------------------------------------

TITLE: PydanticAI Example
DESCRIPTION: This snippet refers to an example using PydanticAI, a library that integrates Pydantic data validation with AI models. It likely shows how to build A2A agents that leverage Pydantic for structured data handling.

SOURCE: https://a2a-protocol.org/latest/community

LANGUAGE: Python
CODE:
```
# Placeholder for PydanticAI example code
# This would involve defining Pydantic models for agent communication
# and using them within A2A agents.

# Example structure:
# from pydantic import BaseModel
# from a2a import Agent
# 
# class TaskRequest(BaseModel):
#     task_description: str
#     parameters: dict
# 
# class TaskResponse(BaseModel):
#     result: str
#     status: str
# 
# agent = Agent(name="PydanticAgent", capabilities=["process_task"])
# agent.register_capability("process_task", lambda req: TaskResponse(result="Processed", status="success"))
# agent.start()
```

----------------------------------------

TITLE: Manage Credentials with CredentialService
DESCRIPTION: Provides examples of retrieving credentials using the CredentialService. This is crucial for secure authentication and authorization in agent communications.

SOURCE: https://a2a-protocol.org/latest/sdk/python/api/a2a

LANGUAGE: python
CODE:
```
credentials = CredentialService.get_credentials()
```

----------------------------------------

TITLE: AG2 + MCP Example
DESCRIPTION: This snippet relates to an example combining AG2 (likely another agent framework or version) with MCP (Multi-communication Protocol), showcasing interoperability between different agent communication standards.

SOURCE: https://a2a-protocol.org/latest/community

LANGUAGE: Python
CODE:
```
# Placeholder for AG2 + MCP example code
# This would demonstrate how agents using AG2 can communicate with agents
# using MCP, likely through an A2A intermediary or adapter.

# Example structure:
# from a2a import Agent
# from mcp import MCPClient
# 
# # Agent using A2A
# agent_a2a = Agent(name="AgentA", capabilities=["communicate"])
# 
# # Agent using MCP
# mcp_client = MCPClient(server_address="mcp_server")
# 
# # Code to bridge communication between agent_a2a and mcp_client...
```

----------------------------------------

TITLE: Set up Gemini API Key Environment Variable
DESCRIPTION: This snippet shows how to create a .env file to store your Gemini API key, which is required for the LangGraph example to authenticate with the Gemini model. Ensure you replace the placeholder with your actual API key.

SOURCE: https://a2a-protocol.org/latest/tutorials/python/7-streaming-and-multiturn

LANGUAGE: Shell
CODE:
```
echo"GOOGLE_API_KEY=YOUR_API_KEY_HERE"
```

----------------------------------------

TITLE: Python Tutorial for A2A Protocol
DESCRIPTION: A step-by-step tutorial on using the A2A protocol with Python. It covers setting up the environment, understanding agent skills and cards, implementing an agent executor, starting and interacting with the server, and handling streaming and multi-turn conversations.

SOURCE: https://a2a-protocol.org/latest/specification

LANGUAGE: Python
CODE:
```
# This section describes a tutorial for Python, but no actual code examples are provided in the input text.
# The tutorial covers Introduction, Setup, Agent Skills & Agent Card, Agent Executor, Start Server, Interact with Server, Streaming & Multiturn, and Next Steps.
```

----------------------------------------

TITLE: A2A Tutorial: Python Streaming & Multiturn
DESCRIPTION: This Python example covers handling streaming responses and multi-turn conversations within the A2A protocol. It demonstrates how agents can send back multiple messages over time or engage in back-and-forth interactions.

SOURCE: https://a2a-protocol.org/latest/topics/what-is-a2a

LANGUAGE: python
CODE:
```
from a2a.client import A2AClient

client = A2AClient(base_url="http://localhost:8000")

# Example for streaming response
for chunk in client.stream_skill(
    skill_name="long_running_task",
    params={"input": "process data"}
):
    print(chunk)

# Example for multi-turn interaction (simplified)
conversation_id = client.start_conversation(skill_name="chat")
response1 = client.send_message(conversation_id, message="Hello")
response2 = client.send_message(conversation_id, message="How are you?")

```

----------------------------------------

TITLE: Example Push Notification Payload (Minimal)
DESCRIPTION: An example of a minimal push notification payload sent by the A2A Server to the client's webhook, containing the Task ID and its new state.

SOURCE: https://a2a-protocol.org/latest/topics/streaming-and-async

LANGUAGE: json
CODE:
```
{
  "taskId": "task-123",
  "state": "completed"
}
```

----------------------------------------

TITLE: AgentCard Example with Extension
DESCRIPTION: This JSON object demonstrates an AgentCard configuration that includes an extension declaration. It specifies the extension's URI, a description, whether it's required, and custom parameters.

SOURCE: https://a2a-protocol.org/latest/topics/extensions

LANGUAGE: json
CODE:
```
{
"name":"Magic 8-ball",
"description":"An agent that can tell your future... maybe.",
"version":"0.1.0",
"url":"https://example.com/agents/eightball",
"capabilities":{
"streaming":true,
"extensions":[
{
"uri":"https://example.com/ext/konami-code/v1",
"description":"Provide cheat codes to unlock new fortunes",
"required":false,
"params":{
"hints":[
"When your sims need extra cash fast",
"You might deny it, but we've seen the evidence of those cows."
]
}
}
]
},
"defaultInputModes":["text/plain"],
"defaultOutputModes":["text/plain"],
"skills":[
{
"id":"fortune",
"name":"Fortune teller",
"description":"Seek advice from the mystical magic 8-ball",
"tags":["mystical","untrustworthy"]
}
]
}

```

----------------------------------------

TITLE: A2A Tutorial: Python Agent Skills & Agent Card
DESCRIPTION: This Python example illustrates how to define agent skills and an Agent Card within the A2A framework. The Agent Card advertises the agent's capabilities, enabling discovery by other agents. Skills define the specific functions the agent can perform.

SOURCE: https://a2a-protocol.org/latest/topics/what-is-a2a

LANGUAGE: python
CODE:
```
from a2a.agent import Agent, Skill
from a2a.card import AgentCard

class FlightBookingSkill(Skill):
    def execute(self, destination, date):
        # Logic for booking flights
        return f"Flight booked to {destination} on {date}"

agent_card = AgentCard(
    name="Flight Booker",
    description="Books flights to any destination.",
    skills=["book_flight"]
)

agent = Agent(agent_card=agent_card, skills={"book_flight": FlightBookingSkill()})

```

----------------------------------------

TITLE: Manage Credentials in InMemoryContextCredentialStore
DESCRIPTION: Illustrates the usage of InMemoryContextCredentialStore for managing credentials in memory. This includes methods for getting and setting credentials within the agent's context.

SOURCE: https://a2a-protocol.org/latest/sdk/python/api/a2a

LANGUAGE: python
CODE:
```
store = InMemoryContextCredentialStore()
credentials = store.get_credentials()
store.set_credentials(credentials)
```

----------------------------------------

TITLE: Find and Get Requested Extensions by URI
DESCRIPTION: Explains how to find extensions using their URIs and retrieve requested extensions within the a2a.extensions.common module.

SOURCE: https://a2a-protocol.org/latest/sdk/python/api/a2a

LANGUAGE: python
CODE:
```
extension = find_extension_by_uri(uri)
requested = get_requested_extensions()
```

----------------------------------------

TITLE: Python: A2A Server Setup with LangGraph
DESCRIPTION: Sets up an A2A server using Starlette and LangGraph, integrating a currency agent with LLM capabilities and managing task state with an in-memory store. It configures the request handler and runs the server using uvicorn.

SOURCE: https://a2a-protocol.org/latest/tutorials/python/7-streaming-and-multiturn

LANGUAGE: Python
CODE:
```
import httpx
import uvicorn

from a2a.server.starlette import A2AStarletteApplication
from a2a.server.starlette.handlers import DefaultRequestHandler
from a2a.stores.task import InMemoryTaskStore
from a2a.stores.push_notification_config import InMemoryPushNotificationConfigStore
from a2a.senders.push_notification import BasePushNotificationSender

# Assuming CurrencyAgentExecutor and agent_card are defined elsewhere
# from .agent_executor import CurrencyAgentExecutor
# from .agent_card import agent_card

httpx_client = httpx.AsyncClient()
push_config_store = InMemoryPushNotificationConfigStore()
push_sender = BasePushNotificationSender(httpx_client=httpx_client,
                config_store=push_config_store)
request_handler = DefaultRequestHandler(
    agent_executor=CurrencyAgentExecutor(),
    task_store=InMemoryTaskStore(),
    push_config_store=push_config_store,
    push_sender= push_sender
)
server = A2AStarletteApplication(
    agent_card=agent_card,
    http_handler=request_handler
)

host = "0.0.0.0"
port = 8000

uvicorn.run(server.build(), host=host, port=port)
```

----------------------------------------

TITLE: Define a Simple Agent Skill in Python
DESCRIPTION: This Python code defines a basic Agent Skill for the Helloworld agent. It includes essential attributes like ID, name, description, tags, and examples, specifying the agent's core functionality.

SOURCE: https://a2a-protocol.org/latest/tutorials/python/3-agent-skills-and-card

LANGUAGE: python
CODE:
```
skill = AgentSkill(
    id='hello_world',
    name='Returns hello world',
    description='just returns hello world',
    tags=['hello world'],
    examples=['hi', 'hello world'],
)
```

----------------------------------------

TITLE: Get Task (JSON-RPC)
DESCRIPTION: Handles the 'tasks/get' JSON-RPC method to retrieve task details. It takes a GetTaskRequest and returns a GetTaskResponse.

SOURCE: https://a2a-protocol.org/latest/sdk/python/api/a2a.server

LANGUAGE: Python
CODE:
```
async def on_get_task(_request :GetTaskRequest_, _context :ServerCallContext|None=None_) -> GetTaskResponse:
    """
    Handles the ‘tasks/get’ JSON-RPC method. 

    Parameters: 
        
      * **request** – The incoming GetTaskRequest object.
      * **context** – Context provided by the server.

    Returns: 
        A GetTaskResponse object containing the Task or a JSON-RPC error.
    """
    pass
```

----------------------------------------

TITLE: Get Task (REST)
DESCRIPTION: Retrieves the current state of a task via REST API using a GET request. Parameters include task ID and optional history length.

SOURCE: https://a2a-protocol.org/latest/specification

LANGUAGE: REST
CODE:
```
GET /v1/tasks/{id}?historyLength={historyLength}

// Response is Task
```

----------------------------------------

TITLE: REST Handler for Task Push Notification Get
DESCRIPTION: Handles the 'tasks/pushNotificationConfig/get' REST method by mapping it to the appropriate request handler. Returns a dictionary containing the configuration.

SOURCE: https://a2a-protocol.org/latest/sdk/python/api/a2a.server

LANGUAGE: Python
CODE:
```
async def get_push_notification(_request :Any_, _context :ServerCallContext_) -> dict[str,Any]:
    """
    Handles the ‘tasks/pushNotificationConfig/get’ REST method. 

    Parameters: 
        
      * **request** – The incoming Request object.
      * **context** – Context provided by the server.


    Returns: 
        A dict containing the config 
    """
    pass
```

----------------------------------------

TITLE: A2A Protocol: Get Task Structures
DESCRIPTION: Defines the data structures for retrieving a task in the A2A protocol, including request, response, and success response models with their respective fields.

SOURCE: https://a2a-protocol.org/latest/sdk/python/api/index

LANGUAGE: Python
CODE:
```
class GetTaskRequest:
    id: str
    jsonrpc: str
    method: str
    model_config: dict
    params: dict

class GetTaskResponse:
    model_config: dict
    root: any

class GetTaskSuccessResponse:
    id: str
```

----------------------------------------

TITLE: HTTP GET Request for Public Agent Card
DESCRIPTION: Demonstrates how a client fetches a public Agent Card by making an HTTP GET request to a specific well-known endpoint. This card contains information about the agent's capabilities, including support for authenticated extended cards.

SOURCE: https://a2a-protocol.org/latest/specification

LANGUAGE: http
CODE:
```
GET https://example.com/.well-known/agent-card.json
```

----------------------------------------

TITLE: Define Agent Skill
DESCRIPTION: Represents a distinct capability or function that an agent can perform, including its description, examples, and input/output modes.

SOURCE: https://a2a-protocol.org/latest/sdk/python/api/a2a

LANGUAGE: Python
CODE:
```
class AgentSkill(_*_ , _description :str_, _examples :list[str]|None=None_, _id :str_, _inputModes :list[str]|None=None_, _name :str_, _outputModes :list[str]|None=None_, _security :list[dict[str,list[str]]]|None=None_, _tags :list[str]_):
    """Represents a distinct capability or function that an agent can perform."""
    description_: str_
    """A detailed description of the skill, intended to help clients or users understand its purpose and functionality."""
    examples_: list[str]|None_
    """Example prompts or scenarios that this skill can handle. Provides a hint to the client on how to use the skill."""
    id_: str_
    """A unique identifier for the agent’s skill."""
    input_modes_: list[str]|None_
    """The set of supported input MIME types for this skill, overriding the agent’s defaults."""
    model_config: ClassVar[ConfigDict]__={'alias_generator': <function to_camel_custom>, 'serialize_by_alias': True, 'validate_by_alias': True, 'validate_by_name': True}_
    """Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict]."""
    name_: str_
    """A human-readable name for the skill."""
    output_modes_: list[str]|None_
    """The set of supported output MIME types for this skill, overriding the agent’s defaults."""
    security_: list[dict[str,list[str]]]|None_
    """Security schemes necessary for the agent to leverage this skill. As in the overall AgentCard.security, this list represents a logical OR of security requirement objects. Each object is a set of security schemes that must be used together (a logical AND)."""
    tags_: list[str]_
    """A set of keywords describing the skill’s capabilities."""
```

----------------------------------------

TITLE: Create and Register Clients with ClientFactory
DESCRIPTION: Demonstrates how to use the ClientFactory to create and register client instances. This is essential for establishing connections and managing agent interactions within the A2A protocol.

SOURCE: https://a2a-protocol.org/latest/sdk/python/api/a2a

LANGUAGE: python
CODE:
```
client = ClientFactory.create()
ClientFactory.register(client)
```

----------------------------------------

TITLE: Initiate Flight Booking Request (message/send)
DESCRIPTION: Client sends an initial message to book a flight using the 'message/send' method. This starts the interaction and provides the first piece of information to the agent.

SOURCE: https://a2a-protocol.org/latest/specification

LANGUAGE: json
CODE:
```
{
"jsonrpc":"2.0",
"id":"req-003",
"method":"message/send",
"params":{
"message":{
"role":"user",
"parts":[{"kind":"text","text":"I'd like to book a flight."}]
},
"messageId":"c53ba666-3f97-433c-a87b-6084276babe2"
}
}
```

----------------------------------------

TITLE: Get Message Text
DESCRIPTION: Provides a function to retrieve the text content of a message.

SOURCE: https://a2a-protocol.org/latest/sdk/python/api/a2a

LANGUAGE: python
CODE:
```
message_text = get_message_text(message)
```

----------------------------------------

TITLE: Get Task - Python
DESCRIPTION: Retrieves information about a specific task. This method is fundamental for monitoring task progress and is implemented across different transports.

SOURCE: https://a2a-protocol.org/latest/sdk/python/api/a2a.client

LANGUAGE: Python
CODE:
```
get_task()
```

----------------------------------------

TITLE: Handle Get Task
DESCRIPTION: Handles the 'v1/tasks/{id}' REST method to retrieve a specific Task object. It takes a request and context, returning the Task object.

SOURCE: https://a2a-protocol.org/latest/sdk/python/api/a2a.server

LANGUAGE: Python
CODE:
```
async def on_get_task(_request :Any_, _context :ServerCallContext_) -> dict[str,Any]:
    """
    Handles the ‘v1/tasks/{id}’ REST method. 

    Parameters: 
        
      * **request** – The incoming Request object.
      * **context** – Context provided by the server.


    Returns: 
        
A Task object containing the Task. 
```

----------------------------------------

TITLE: Get Task Callback Configuration - Python
DESCRIPTION: Retrieves the current push notification configuration for a task. This allows clients to inspect or manage existing callback settings.

SOURCE: https://a2a-protocol.org/latest/sdk/python/api/a2a.client

LANGUAGE: Python
CODE:
```
get_task_callback()
```

----------------------------------------

TITLE: Abstract Method: Get Task
DESCRIPTION: Abstract method to handle the 'tasks/get' method, retrieving the state and history of a specific task. It takes task query parameters and server context, returning the Task object or None.

SOURCE: https://a2a-protocol.org/latest/sdk/python/api/a2a.server

LANGUAGE: Python
CODE:
```
async def async_on_get_task(_params :TaskQueryParams_, _context :ServerCallContext|None=None_) -> Task|None:
    """
    Handles the ‘tasks/get’ method.
    Retrieves the state and history of a specific task. 

    Parameters: 
        
      * **params** – Parameters specifying the task ID and optionally history length.
      * **context** – Context provided by the server.


    Returns: 
        
    The Task object if found, otherwise None. 
```

----------------------------------------

TITLE: Abstract Method: Get Push Notification Config
DESCRIPTION: Abstract method to handle the 'tasks/pushNotificationConfig/get' method, retrieving the push notification configuration for a task. It requires task ID parameters and server context, returning the TaskPushNotificationConfig.

SOURCE: https://a2a-protocol.org/latest/sdk/python/api/a2a.server

LANGUAGE: Python
CODE:
```
async def async_on_get_task_push_notification_config(_params :TaskIdParams|GetTaskPushNotificationConfigParams_, _context :ServerCallContext|None=None_) -> TaskPushNotificationConfig:
    """
    Handles the ‘tasks/pushNotificationConfig/get’ method.
    Retrieves the current push notification configuration for a task. 

    Parameters: 
        
      * **params** – Parameters including the task ID.
      * **context** – Context provided by the server.


    Returns: 
        
    The TaskPushNotificationConfig for the task. 
```

----------------------------------------

TITLE: Initialize A2A Client with Agent Card
DESCRIPTION: Demonstrates how to initialize the A2A client by fetching the Agent Card and setting up the resolver. It uses httpx for asynchronous HTTP requests.

SOURCE: https://a2a-protocol.org/latest/tutorials/python/6-interact-with-server

LANGUAGE: Python
CODE:
```
base_url = 'http://localhost:9999'

async with httpx.AsyncClient() as httpx_client:
    # Initialize A2ACardResolver
    resolver = A2ACardResolver(
        httpx_client=httpx_client,
        base_url=base_url,
        # agent_card_path uses default, extended_agent_card_path also uses default
    )
```

----------------------------------------

TITLE: DefaultRequestHandler Methods for Task Management
DESCRIPTION: Provides default implementations for A2A JSON-RPC methods related to task management. This includes cancelling, getting, and managing push notification configurations for tasks. It requires specific stores and notifiers to be configured for certain operations.

SOURCE: https://a2a-protocol.org/latest/sdk/python/api/a2a.server

LANGUAGE: Python
CODE:
```
class DefaultRequestHandler(RequestHandler):
    async def on_cancel_task(_params :TaskIdParams_, _context :ServerCallContext|None=None_) → Task|None:
        """Default handler for ‘tasks/cancel’. Attempts to cancel the task managed by the AgentExecutor."""
        pass

    async def on_get_task(_params :TaskQueryParams_, _context :ServerCallContext|None=None_) → Task|None:
        """Default handler for ‘tasks/get’. """
        pass

    async def on_set_task_push_notification_config(_params :TaskPushNotificationConfig_, _context :ServerCallContext|None=None_) → TaskPushNotificationConfig:
        """Default handler for ‘tasks/pushNotificationConfig/set’. Requires a PushNotifier to be configured."""
        pass

    async def on_delete_task_push_notification_config(_params :DeleteTaskPushNotificationConfigParams_, _context :ServerCallContext|None=None_) → None:
        """Default handler for ‘tasks/pushNotificationConfig/delete’. Requires a PushConfigStore to be configured."""
        pass

    async def on_get_task_push_notification_config(_params :TaskIdParams|GetTaskPushNotificationConfigParams_, _context :ServerCallContext|None=None_) → TaskPushNotificationConfig:
        """Default handler for ‘tasks/pushNotificationConfig/get’. Requires a PushConfigStore to be configured."""
        pass

    async def on_list_task_push_notification_config(_params :ListTaskPushNotificationConfigParams_, _context :ServerCallContext|None=None_) → list[TaskPushNotificationConfig]:
        """Default handler for ‘tasks/pushNotificationConfig/list’. Requires a PushConfigStore to be configured."""
        pass
```

----------------------------------------

TITLE: Get Task (gRPC)
DESCRIPTION: Retrieves the current state of a task using gRPC. Accepts task name and history length, returning the Task object.

SOURCE: https://a2a-protocol.org/latest/specification

LANGUAGE: gRPC
CODE:
```
message GetTaskRequest {
  // name=tasks/{id}
  string name;
  int32 history_length;
}

// Response is Task
```

----------------------------------------

TITLE: Autogen Sample Server
DESCRIPTION: This snippet refers to a sample server implementation using Autogen, a framework for developing LLM applications with multiple agents. It demonstrates how to set up an A2A-compatible server with Autogen.

SOURCE: https://a2a-protocol.org/latest/community

LANGUAGE: Python
CODE:
```
# Placeholder for Autogen sample server code
# This would involve setting up an Autogen configuration and potentially
# exposing it as an A2A-compatible service.

# Example structure:
# from autogen import UserProxyAgent, AssistantAgent, config_list_from_json
# 
# config_list = config_list_from_json("OAI_CONFIG_LIST")
# 
# user_proxy = UserProxyAgent("user_proxy", code_execution_config={"work_dir": "coding"}, llm_config={"config_list": config_list, "seed": 42})
# assistant = AssistantAgent("assistant", llm_config={"config_list": config_list, "seed": 42})
# 
# # Code to expose this setup as an A2A server would follow...
```

----------------------------------------

TITLE: A2A Push Notification Setup (Client Request)
DESCRIPTION: Client initiates a long-running task and configures push notifications for completion. This involves sending a message with a `pushNotificationConfig` including the webhook URL and authentication token.

SOURCE: https://a2a-protocol.org/latest/specification

LANGUAGE: json
CODE:
```
{
"jsonrpc":"2.0",
"id":"req-005",
"method":"message/send",
"params":{
"message":{
"role":"user",
"parts":[
{
"kind":"text",
"text":"Generate the Q1 sales report. This usually takes a while. Notify me when it's ready."
}
],
"messageId":"6dbc13b5-bd57-4c2b-b503-24e381b6c8d6"
},
"configuration":{
"pushNotificationConfig":{
"url":"https://client.example.com/webhook/a2a-notifications",
"token":"secure-client-token-for-task-aaa",
"authentication":{
"schemes":["Bearer"]
}
}
}
}
}
```

----------------------------------------

TITLE: Create Task Object
DESCRIPTION: Demonstrates the creation of a task object.

SOURCE: https://a2a-protocol.org/latest/sdk/python/api/a2a

LANGUAGE: python
CODE:
```
task = create_task_obj()
```

----------------------------------------

TITLE: Handle Get Task Request
DESCRIPTION: Handles the ‘tasks/get’ JSON-RPC method for retrieving task details. It takes a GetTaskRequest and returns a GetTaskResponse or a JSON-RPC error.

SOURCE: https://a2a-protocol.org/latest/sdk/python/api/a2a.server

LANGUAGE: Python
CODE:
```
async def on_get_task(self, _request: GetTaskRequest, _context: ServerCallContext | None = None) -> GetTaskResponse:
    """Handles the ‘tasks/get’ JSON-RPC method.

    Parameters:
        request – The incoming GetTaskRequest object.
        context – Context provided by the server.

    Returns:
        A GetTaskResponse object containing the Task or a JSON-RPC error.
    """
    pass
```

----------------------------------------

TITLE: AgentSkill Object
DESCRIPTION: Represents a distinct capability or function that an agent can perform. It includes an ID, name, description, tags, example prompts, supported input/output modes, and security schemes.

SOURCE: https://a2a-protocol.org/latest/specification

LANGUAGE: TypeScript
CODE:
```
/**
 * Represents a distinct capability or function that an agent can perform.
 */
export interface AgentSkill {
  /** A unique identifier for the agent's skill. */
  id: string;
  /** A human-readable name for the skill. */
  name: string;
  /**
   * A detailed description of the skill, intended to help clients or users
   * understand its purpose and functionality.
   */
  description: string;
  /**
   * A set of keywords describing the skill's capabilities.
   *
   * @TJS-examples [["cooking", "customer support", "billing"]]
   */
  tags: string[];
  /**
   * Example prompts or scenarios that this skill can handle. Provides a hint to
   * the client on how to use the skill.
   *
   * @TJS-examples [["I need a recipe for bread"]]
   */
  examples?: string[];
  /**
   * The set of supported input MIME types for this skill, overriding the agent's defaults.
   */
  inputModes?: string[];
  /**
   * The set of supported output MIME types for this skill, overriding the agent's defaults.
   */
  outputModes?: string[];
  /**
   * Security schemes necessary for the agent to leverage this skill.
   * As in the overall AgentCard.security, this list represents a logical OR of security
   * requirement objects. Each object is a set of security schemes that must be used together
   * (a logical AND).
   *
   * @TJS-examples [[{"google": ["oidc"]}]]
   */
  security?: { [scheme: string]: string[] }[];
}
```

----------------------------------------

TITLE: Server-Sent Events (SSE) - Artifact Update Event
DESCRIPTION: An example of a Server-Sent Event (SSE) for TaskArtifactUpdateEvent, indicating new or updated artifact chunks. This is used in streaming interactions.

SOURCE: https://a2a-protocol.org/latest/topics/key-concepts

LANGUAGE: sse
CODE:
```
event: TaskArtifactUpdateEvent
data: {"taskId": "task_12345", "artifactId": "art_xyz789", "partIndex": 0, "part": {"type": "TextPart", "content": "Processing data..."}}


```

----------------------------------------

TITLE: Get Starlette Routes for A2A
DESCRIPTION: Retrieves a list of Starlette Route objects designed to handle A2A protocol requests, including agent card and JSON-RPC endpoints.

SOURCE: https://a2a-protocol.org/latest/sdk/python/api/a2a.server.apps

LANGUAGE: Python
CODE:
```
def routes(_agent_card_url :str='/.well-known/agent-card.json'_, _rpc_url :str='/'_, _extended_agent_card_url :str='/agent/authenticatedExtendedCard'_) → list[Any]:
    """Returns the Starlette Routes for handling A2A requests."""
    pass
```

----------------------------------------

TITLE: Run A2A Test Client (Python)
DESCRIPTION: This command executes the Python test client script from the 'a2a-samples' directory to interact with the A2A server. It demonstrates fetching the Agent Card and sending messages.

SOURCE: https://a2a-protocol.org/latest/tutorials/python/6-interact-with-server

LANGUAGE: python
CODE:
```
python test_client.py
```

----------------------------------------

TITLE: Get Card Information - Python
DESCRIPTION: Retrieves card information, likely related to a specific task or entity. This functionality is present in multiple transport implementations.

SOURCE: https://a2a-protocol.org/latest/sdk/python/api/a2a.client

LANGUAGE: Python
CODE:
```
get_card()
```

----------------------------------------

TITLE: A2A Protocol: Get Task Push Notification Config Structures
DESCRIPTION: Defines the data structures for retrieving task push notification configurations in the A2A protocol, including parameters, request, response, and success response models.

SOURCE: https://a2a-protocol.org/latest/sdk/python/api/index

LANGUAGE: Python
CODE:
```
class GetTaskPushNotificationConfigParams:
    id: str
    metadata: dict
    model_config: dict
    push_notification_config_id: str

class GetTaskPushNotificationConfigRequest:
    id: str
    jsonrpc: str
    method: str
    model_config: dict
    params: GetTaskPushNotificationConfigParams

class GetTaskPushNotificationConfigResponse:
    model_config: dict
    root: any

class GetTaskPushNotificationConfigSuccessResponse:
    id: str
    jsonrpc: str
    model_config: dict
    result: any
```

----------------------------------------

TITLE: A2A REST Transport: Get Agent Card
DESCRIPTION: Retrieves the agent's card information using the REST transport. Optionally accepts a ClientCallContext.

SOURCE: https://a2a-protocol.org/latest/sdk/python/api/a2a.client

LANGUAGE: Python
CODE:
```
async def get_card(_*_ , _context :ClientCallContext|None=None_) → AgentCard:
    """Retrieves the agent’s card."""
    pass
```

----------------------------------------

TITLE: Python Tutorial for A2A Protocol
DESCRIPTION: This section provides a tutorial on using the A2A Protocol with Python. It likely covers setting up an agent, making requests, and handling responses within the Python ecosystem.

SOURCE: https://a2a-protocol.org/latest/specification

LANGUAGE: Python
CODE:
```
print("Tutorial (Python) section content would be here.")
```

----------------------------------------

TITLE: A2A REST Transport: Get Task
DESCRIPTION: Retrieves the current state and history of a specific task via the REST transport. Requires TaskQueryParams and optionally accepts a ClientCallContext.

SOURCE: https://a2a-protocol.org/latest/sdk/python/api/a2a.client

LANGUAGE: Python
CODE:
```
async def get_task(_request :TaskQueryParams_, _*_ , _context :ClientCallContext|None=None_) → Task:
    """Retrieves the current state and history of a specific task."""
    pass
```

----------------------------------------

TITLE: A2A Get Task RPC
DESCRIPTION: Shows the RPC method used by a client to retrieve the complete, updated Task object after receiving a push notification.

SOURCE: https://a2a-protocol.org/latest/topics/streaming-and-async

LANGUAGE: json
CODE:
```
{
  "method": "tasks/get",
  "params": {
    "taskId": "task-123"
  }
}
```

----------------------------------------

TITLE: A2A Protocol: Get Authenticated Extended Card Structures
DESCRIPTION: Defines the data structures for retrieving an authenticated extended card in the A2A protocol, including request, response, and success response models.

SOURCE: https://a2a-protocol.org/latest/sdk/python/api/index

LANGUAGE: Python
CODE:
```
class GetAuthenticatedExtendedCardRequest:
    id: str
    jsonrpc: str
    method: str
    model_config: dict

class GetAuthenticatedExtendedCardResponse:
    model_config: dict
    root: any

class GetAuthenticatedExtendedCardSuccessResponse:
    id: str
    jsonrpc: str
    model_config: dict
    result: any
```

----------------------------------------

TITLE: Python: Get Task Push Notification Configuration
DESCRIPTION: Abstract method to handle the 'tasks/pushNotificationConfig/get' JSON-RPC request. It retrieves the current push notification configuration for a task using task parameters and server context.

SOURCE: https://a2a-protocol.org/latest/sdk/python/api/a2a.server

LANGUAGE: Python
CODE:
```
async_on_get_task_push_notification_config(_params :TaskIdParams|GetTaskPushNotificationConfigParams_, _context :ServerCallContext|None=None_) → TaskPushNotificationConfig
```

----------------------------------------

TITLE: RESTHandler: Get Push Notification Configuration
DESCRIPTION: Handles the ‘tasks/pushNotificationConfig/get’ REST method. It takes an incoming Request object and server context, returning a dictionary containing the configuration.

SOURCE: https://a2a-protocol.org/latest/sdk/python/api/a2a.server

LANGUAGE: Python
CODE:
```
async def get_push_notification(self, request: Any, context: ServerCallContext) -> dict[str, Any]:
    """Handles the ‘tasks/pushNotificationConfig/get’ REST method."""
    pass
```

----------------------------------------

TITLE: Client Authentication Credential Transmission
DESCRIPTION: Illustrates how clients transmit authentication credentials to A2A servers via HTTP headers. This includes examples for Bearer tokens and API keys.

SOURCE: https://a2a-protocol.org/latest/specification

LANGUAGE: HTTP Headers
CODE:
```
Authorization: Bearer <token>
X-API-Key: <value>
```

----------------------------------------

TITLE: Create Minimal Agent Card
DESCRIPTION: Demonstrates the creation of a minimal agent card, which represents a basic agent profile.

SOURCE: https://a2a-protocol.org/latest/sdk/python/api/a2a

LANGUAGE: python
CODE:
```
agent_card = minimal_agent_card()
```

----------------------------------------

TITLE: GetTaskPushNotificationConfigRequest Model
DESCRIPTION: Defines the structure for a JSON-RPC request to get a task's push notification configuration. It includes fields for the request ID, JSON-RPC version, method name, and parameters specific to the request.

SOURCE: https://a2a-protocol.org/latest/sdk/python/api/a2a

LANGUAGE: python
CODE:
```
class GetTaskPushNotificationConfigRequest(_*_ , _id :str|int_, _jsonrpc :Literal['2.0']='2.0'_, _method :Literal['tasks/pushNotificationConfig/get']='tasks/pushNotificationConfig/get'_, _params :TaskIdParams|GetTaskPushNotificationConfigParams_){
    """
    Represents a JSON-RPC request for the tasks/pushNotificationConfig/get method.
    """
    id_: str|int
    jsonrpc: Literal['2.0']
    method: Literal['tasks/pushNotificationConfig/get']
    params: TaskIdParams|GetTaskPushNotificationConfigParams
    model_config: ClassVar[ConfigDict]__={'alias_generator': <function to_camel_custom>, 'serialize_by_alias': True, 'validate_by_alias': True, 'validate_by_name': True}_
```