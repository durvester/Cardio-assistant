# A2A + LLM Agent Requirements - Complete Guide

## What is A2A?
A2A (Agent-to-Agent) is a protocol that lets AI agents have structured conversations. Unlike simple API calls, A2A enables back-and-forth negotiations, file exchanges, and complex multi-step workflows between agents.

## Core A2A Protocol Requirements

### 1. Agent Discovery
**MUST: Serve an Agent Card at `/.well-known/agent-card.json`**
```json
{
  "protocolVersion": "0.3.0",
  "name": "Your Agent Name",
  "description": "What your agent does",
  "url": "https://your-domain.com/a2a/v1", 
  "preferredTransport": "JSONRPC",
  "capabilities": {"streaming": true},
  "skills": [{"id": "your-skill", "name": "Skill Name", "description": "..."}]
}
```

### 2. Required JSON-RPC Methods
**MUST implement these 4 endpoints:**

- **`message/send`** - Sends a message to an agent to initiate a new interaction or to continue an existing one. This method is suitable for synchronous request/response interactions or when client-side polling (using tasks/get) is acceptable for monitoring longer-running tasks. A task which has reached a terminal state (completed, canceled, rejected, or failed) can't be restarted. Sending a message to such a task will result in an error
- **`message/stream`** - Sends a message to an agent to initiate/continue a task AND subscribes the client to real-time updates for that task via Server-Sent Events (SSE). This method requires the server to have AgentCard.capabilities.streaming: true. Just like message/send, a task which has reached a terminal state (completed, canceled, rejected, or failed) can't be restarted. Sending a message to such a task will result in an error.  
- **`tasks/get`** - Retrieves the current state (including status, artifacts, and optionally history) of a previously initiated task. This is typically used for polling the status of a task initiated with message/send, or for fetching the final state of a task after being notified via a push notification or after an SSE stream has ended.
- **`tasks/cancel`** - Requests the cancellation of an ongoing task. The server will attempt to cancel the task, but success is not guaranteed (e.g., the task might have already completed or failed, or cancellation might not be supported at its current stage).
- **`tasks/resubscribe`** - Allows a client to reconnect to an SSE stream for an ongoing task after a previous connection (from message/stream or an earlier tasks/resubscribe) was interrupted.


### 3. Task Lifecycle Management
**Every conversation is a "task" with these states:**

```
submitted → working → input-required ⟷ working → completed/failed/canceled
```

**Key Rules:**
- Each task gets unique ID
- Tasks only move forward (no backwards transitions)
- Maintain full message history for each task
- Support multi-turn conversations via `input-required` state
- Provide contextId

### 4. Streaming Support (SSE)
**MUST support Server-Sent Events when client sends:**
```http
Accept: text/event-stream
```

**Stream format:**
```
data: {"jsonrpc":"2.0","id":"req1","result":{"kind":"task","status":{"state":"working"}}}

data: {"jsonrpc":"2.0","id":"req1","result":{"kind":"message","role":"agent","parts":[{"kind":"text","text":"Processing..."}]}}

data: {"jsonrpc":"2.0","id":"req1","result":{"kind":"status-update","status":{"state":"completed"},"final":true}}
```

### 5. Message Handling
**Support message parts:**
- **Text parts**: `{"kind": "text", "text": "Hello"}`
- **File parts**: `{"kind": "file", "file": {"name": "doc.pdf", "mimeType": "application/pdf", "bytes": "base64data"}}`

---

## LLM Integration Patterns
- We will use Claude API from Anthropic as the LLM provider and the model will be Claude Sonnet 4

### The LLM's Role in A2A
The LLM acts as your **conversation engine** while A2A provides the **communication structure**:

- **A2A handles**: Protocol compliance, task management, streaming, file handling
- **LLM handles**: Understanding requests, making decisions, generating responses, using tools
- **You handle**: Business logic, external API calls, data validation

### Integration Architecture

```
A2A Client Request → A2A Server → Agent Executor → LLM + Tools → Business Logic
                                        ↓
A2A Client ← Streaming Response ← Task Manager ← LLM Response ← Results
```

### LLM Integration Best Practices

#### 1. System Prompt Design
Structure your system prompt for A2A conversations:

```python
system_prompt = """
You are a professional agent handling [specific domain] requests via structured conversations.

CONVERSATION RULES:
- You're having a back-and-forth conversation, not just answering single questions  
- Ask follow-up questions to gather missing information
- Use tools to verify information and perform actions
- Be conversational but focused on your specific domain

TASK COMPLETION:
- Only complete the task when you have ALL required information
- Use input-required state when you need more information from the user
- Generate appropriate documents/artifacts when completing tasks

YOUR SPECIFIC ROLE: [domain-specific instructions]
"""
```

#### 2. Tool Integration Pattern
Connect LLM function calling to your business logic:

```python
# Define tools for the LLM
tools = [
    {
        "name": "verify_provider",
        "description": "Verify healthcare provider using NPPES API",
        "input_schema": {
            "type": "object", 
            "properties": {
                "first_name": {"type": "string"},
                "last_name": {"type": "string"}
            }
        }
    }
]

# In your agent executor
async def execute_tool(tool_name, args):
    if tool_name == "verify_provider":
        return await verify_provider_with_nppes(**args)
    # ... other tools
```

#### 3. Conversation State Management
Track conversation state for multi-turn interactions:

```python
class ConversationState:
    def __init__(self):
        self.requirements_met = {
            "provider_verified": False,
            "insurance_confirmed": False,
            "clinical_data_complete": False
        }
        self.collected_data = {}
        self.missing_items = []
    
    def is_ready_to_complete(self):
        return all(self.requirements_met.values())
```

#### 4. Streaming LLM Responses to A2A
Bridge LLM streaming to A2A format:

```python
async def stream_llm_to_a2a(llm_stream, task_updater):
    tool_calls = []
    
    async for chunk in llm_stream:
        if chunk.type == "text":
            # Stream text immediately to client
            await task_updater.add_message_part(
                TextPart(text=chunk.content)
            )
        elif chunk.type == "tool_use":
            tool_calls.append(chunk)
    
    # Execute tools after streaming text
    for tool_call in tool_calls:
        result = await execute_tool(tool_call.name, tool_call.input)
        await task_updater.add_message_part(
            TextPart(text=f"Tool result: {result}")
        )
```

### Multi-turn Conversation Flow

#### Pattern 1: Information Gathering
```python
async def handle_referral_request(context, task_updater):
    # Set task to working
    await task_updater.update_status(TaskStatus(state=TaskState.WORKING))
    
    # Process with LLM
    response = await llm.process(context.messages, tools=business_tools)
    
    # Check if we have everything needed
    if not conversation_state.is_ready_to_complete():
        # Need more information
        await task_updater.update_status(TaskStatus(state=TaskState.INPUT_REQUIRED))
        await stream_response(response, task_updater)
    else:
        # Complete the task
        await generate_final_documents(task_updater)
        await task_updater.update_status(TaskStatus(state=TaskState.COMPLETED))
```

#### Pattern 2: Progressive Disclosure
Let the LLM decide what information to request next:

```python
# In system prompt:
"""
INFORMATION GATHERING STRATEGY:
1. First verify the referring provider
2. Then confirm patient insurance  
3. Then gather clinical information
4. Ask for missing documentation
5. Only when everything is complete, schedule appointment and generate documents

Always explain what information you still need and why.
"""
```

### File Handling with LLMs

#### Processing Incoming Files
```python
async def handle_file_attachment(file_part):
    if file_part.file.mime_type == "application/pdf":
        # Extract text for LLM processing
        text_content = extract_pdf_text(file_part.file.bytes)
        
        # Send to LLM for analysis
        analysis = await llm.analyze_document(text_content, document_type="medical_report")
        
        return analysis
```

#### Generating File Artifacts
```python
async def create_confirmation_document(appointment_details):
    # Use LLM to generate document
    document_content = await llm.generate_document(
        template="appointment_confirmation",
        data=appointment_details
    )
    
    # Add as task artifact
    await task_updater.update_artifact(
        TaskArtifactUpdateEvent(
            artifact={
                "type": "document",
                "content": document_content,
                "mime_type": "text/markdown", 
                "name": "appointment_confirmation.md"
            }
        )
    )
```

## Complete Implementation Strategy

### Phase 1: Basic A2A Compliance
1. Set up HTTP server with JSON-RPC support
2. Implement required methods (message/send, message/stream, tasks/get, tasks/cancel, tasks/resubscribe)
3. Add agent card endpoint
4. Test with simple echo responses

### Phase 2: LLM Integration  
1. Add LLM client
2. Implement basic conversation flow
3. Add streaming support (LLM → SSE)
4. Add conversation state management
5. Test multi-turn conversations

### Phase 3: Business Logic
1. Define domain-specific tools
2. Implement file processing
3. Add document generation

### Phase 4: Production Ready
1. Error handling and recovery
2. Logging and monitoring
3. Security and validation
4. Performance optimization

## Common Pitfalls to Avoid

1. **Don't make the LLM handle A2A protocol details** - That's your job
2. **Don't complete tasks too early** - Use input-required state liberally
3. **Don't lose conversation context** - Always maintain full message history and context so that it can be provided to the LLM
4. **Don't block on LLM calls** - Use streaming for responsive UX
5. **Don't forget file handling** - Many business workflows involve documents

## Testing Strategy
Use A2A inspector or a lightweight A2A client

## Summary

Building an A2A + LLM agent requires three layers:

1. **A2A Protocol Layer**: Handle discovery, task management, streaming, file exchange
2. **LLM Integration Layer**: Convert between A2A format and LLM APIs, manage conversation flow  
3. **Business Logic Layer**: Domain-specific tools, validation, external APIs

The key insight: A2A provides the conversation structure while the LLM provides the intelligence. Your job is to connect them seamlessly and add domain-specific business logic.