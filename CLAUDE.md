# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based A2A (Agent-to-Agent) compliant cardiology referral agent for Dr. Walter Reed's clinic. The agent handles new patient cardiology referrals through intelligent conversations, multi-turn interactions, and automated referral processing using the Claude API.

## Development Commands

### Core Development Commands
```bash
# Install dependencies
pip install -e .

# Run the agent server
python __main__.py

# Run with development mode
python -m walter_reed_cardiology_agent

# Run tests
python -m pytest test_a2a_agent.py -v

# Run specific test categories
python -m pytest test_a2a_agent.py::test_basic_functionality -v
python -m pytest test_a2a_agent.py::test_multi_turn_conversation -v
```

### Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Set up environment variables (create .env file)
echo "ANTHROPIC_API_KEY=your_key_here" > .env
echo "HOST=localhost" >> .env
echo "PORT=8000" >> .env
```

## Architecture Overview

### Core Components

**A2A Protocol Implementation:**
- `__main__.py` - Server entry point and Starlette app setup
- `agent_executor.py` - A2A protocol bridge (AgentExecutor implementation)
- `agent.py` - Core business logic with Claude API integration
- `config.py` - Configuration management with environment variables
- `agentcard.json` - A2A agent card definition

**Key Architecture Patterns:**
- Follows A2A Python SDK patterns with TaskUpdater and EventQueue
- Implements both Phase 1 (single-turn) and Phase 2 (multi-turn) conversation modes
- Uses LLM-driven state transitions with special markers: `[NEED_MORE_INFO]`, `[REFERRAL_COMPLETE]`, `[REFERRAL_FAILED]`
- Supports conversation history preservation across multiple interactions

### Agent Behavior Modes

**Phase 1 Mode (Single-turn):**
- Used for complete referral requests with most required information
- Claude responds once and marks task as completed
- Maintains backward compatibility

**Phase 2 Mode (Multi-turn):**
- Default mode for new conversations and incomplete referrals
- Maintains conversation context across interactions
- Uses intelligent state management via TaskUpdater
- Collects referral information progressively

### Data Flow

1. HTTP request → A2AStarletteApplication → DefaultRequestHandler
2. RequestHandler → CardiologyAgentExecutor.execute()
3. AgentExecutor → CardiologyAgent.process_message()
4. CardiologyAgent → Claude API → Response with state markers
5. AgentExecutor extracts state → TaskUpdater → EventQueue → Client

## Development Practices

### Configuration Management
- All settings in `config.py` using environment variables
- Required: `ANTHROPIC_API_KEY`
- Optional: `HOST`, `PORT`, `CLAUDE_MODEL`
- Agent card at `agentcard.json`

### Testing Strategy
- Comprehensive test suite in `test_a2a_agent.py`
- Tests both Phase 1 and Phase 2 behaviors
- Real-world referral scenarios
- 100% test success rate maintained

### Message Processing Logic
```python
# Phase detection in agent_executor.py:
if conversation_history or context.current_task or not is_likely_complete_referral:
    # Phase 2: Multi-turn mode
    response_text = await cardiology_agent.process_message(message_text, history_to_pass)
else:
    # Phase 1: Single-turn mode  
    response_text = await cardiology_agent.process_message(message_text)
```

### State Control
The LLM controls conversation state through special markers:
- `[NEED_MORE_INFO]` → TaskState.input_required
- `[REFERRAL_COMPLETE]` → TaskState.completed  
- `[REFERRAL_FAILED]` → TaskState.failed

## Domain-Specific Context

### Medical Specialization
- **Scope:** New patient cardiology referrals only
- **Provider:** Dr. Walter Reed, Manhattan clinic
- **Schedule:** Monday/Thursday 11 AM-3 PM appointments
- **Insurance:** United Healthcare, Aetna, Cigna, BCBS, Kaiser only

### Required Referral Information
1. Patient identifiers (name, DOB, MRN)
2. Referring provider verification via NPPES
3. Clinical information (symptoms, tests, medications)
4. Insurance validation
5. Appointment scheduling

### Business Rules
- Emergency cases → immediate triage to urgent care
- Provider verification required via NPPES API
- Insurance pre-authorization checking
- Professional medical communication standards
- No medical advice or diagnosis provision

## Project Structure

```
├── __main__.py              # Server entry point
├── agent_executor.py        # A2A protocol bridge  
├── agent.py                 # Core agent logic with Claude API
├── config.py                # Configuration management
├── agentcard.json          # A2A agent card
├── pyproject.toml          # Python project configuration
├── test_a2a_agent.py       # Comprehensive test suite
├── roadmap.md              # Development roadmap (Phase 2 complete)
└── documents/              # Specifications and requirements
    ├── A2A_specification.md # A2A protocol documentation
    ├── agent_requirements.md # Functional requirements
    └── implementation_guidance.md
```

## Key Implementation Details

### TaskUpdater Pattern Usage
```python
# Proper A2A SDK pattern in agent_executor.py
updater = TaskUpdater(event_queue, task.id, task.context_id)
await updater.update_status(TaskState.input_required, agent_message, final=True)
```

### Claude API Integration
- Model: `claude-3-5-sonnet-20241022` (configurable)
- Multi-turn conversation support with context preservation
- Dynamic system prompt generation based on conversation state
- Intelligent referral progress analysis

### A2A Protocol Compliance
- Implements required methods: `message/send`, `tasks/get`, `tasks/cancel`
- Agent card served at `/.well-known/agent-card.json`
- JSON-RPC 2.0 over HTTP transport
- Proper task lifecycle management
- Professional error handling and responses

## Development Status

**Current Phase:** Phase 2 Complete (100% test success)
**Next Phase:** Phase 3 - First tool integration
**Completion:** Multi-turn conversations, state management, context preservation
**Test Coverage:** 10/10 comprehensive scenarios passing