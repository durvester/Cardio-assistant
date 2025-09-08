# Walter Reed Cardiology Referral Agent

An A2A (Agent-to-Agent) compliant cardiology referral processing system for Dr. Walter Reed's Manhattan clinic. This intelligent agent handles new patient cardiology referrals through multi-turn conversations, comprehensive clinical validation, and automated appointment scheduling using Claude AI.

## Overview

This system provides a specialized AI agent that:
- **Processes cardiology referrals** with comprehensive clinical validation
- **Verifies referring providers** via NPPES (National Provider Identifier)  
- **Validates insurance coverage** (United Healthcare, Aetna, Cigna, BCBS, Kaiser)
- **Manages multi-turn conversations** for incomplete referral information
- **Schedules appointments** with Dr. Walter Reed (Monday/Thursday 11 AM-3 PM)
- **Maintains A2A protocol compliance** for seamless integration

## Quick Start

### Prerequisites
- Python 3.11+
- Anthropic API key
- Virtual environment (recommended)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/durvester/Cardio-assistant.git
cd Cardio-assistant
```

2. **Set up virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -e .
```

4. **Configure environment variables:**
```bash
# Create .env file
echo "ANTHROPIC_API_KEY=your_anthropic_api_key_here" > .env
echo "HOST=localhost" >> .env
echo "PORT=8000" >> .env
```

### Running the Server

**Start the A2A server:**
```bash
python __main__.py
```

The server will be available at `http://localhost:8000` with the agent card accessible at `/.well-known/agent.json`.

## Testing

Run the comprehensive test suite:
```bash
# All tests
python -m pytest test_a2a_agent.py -v

# Specific test categories
python -m pytest test_a2a_agent.py::test_basic_functionality -v
python -m pytest test_a2a_agent.py::test_multi_turn_conversation -v
```

**Current test coverage:** 100% success rate across 10 comprehensive scenarios.

## Architecture

### Core Components

- **`__main__.py`** - Server entry point and Starlette application setup
- **`agent_executor.py`** - A2A protocol bridge implementing AgentExecutor interface
- **`agent.py`** - Core business logic with Claude API integration
- **`config.py`** - Configuration management with environment variables
- **`.well-known/agent.json`** - A2A agent card definition and capabilities
- **`test_a2a_agent.py`** - Comprehensive test suite

### Agent Behavior Modes

**Phase 1 (Single-turn):**
- Complete referrals with all required information
- Immediate processing and response
- Backward compatibility maintained

**Phase 2 (Multi-turn):**
- Default mode for new conversations
- Progressive information gathering
- Context preservation across interactions
- Intelligent state management

### Data Flow

```
HTTP Request → A2AStarletteApplication → DefaultRequestHandler
     ↓
CardiologyAgentExecutor.execute()
     ↓
CardiologyAgent.process_message() → Claude API
     ↓
State Extraction → TaskUpdater → EventQueue → Client Response
```

## Required Referral Information

The agent collects and validates:

1. **Patient Information**
   - Full name
   - Date of birth
   - Medical record number (MRN)

2. **Referring Provider**
   - Provider name and credentials
   - NPI (National Provider Identifier)
   - Contact information

3. **Clinical Information**
   - Chief complaint/referral reason
   - Relevant symptoms
   - Recent test results (ECG, labs, imaging)
   - Current medications

4. **Insurance Details**
   - Insurance provider (must be supported)
   - Member ID
   - Group number

5. **Scheduling Preferences**
   - Urgency level
   - Preferred appointment times

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | ✅ Yes | - | Anthropic API key for Claude |
| `HOST` | ❌ No | `localhost` | Server host address |
| `PORT` | ❌ No | `8000` | Server port |
| `CLAUDE_MODEL` | ❌ No | `claude-3-5-sonnet-20241022` | Claude model version |
| `AGENT_CARD_PATH` | ❌ No | `.well-known/agent.json` | Path to agent card file |

### Business Rules

- **Scope:** New patient cardiology referrals only
- **Provider:** Dr. Walter Reed, Manhattan clinic  
- **Schedule:** Monday/Thursday, 11 AM-3 PM appointments
- **Insurance:** United Healthcare, Aetna, Cigna, BCBS, Kaiser only
- **Emergency cases:** Immediate triage to urgent care
- **Provider verification:** Required via NPPES API lookup

## A2A Protocol Compliance

This agent implements the A2A specification v0.3.0:

- **JSON-RPC 2.0** transport over HTTP
- **Required endpoints:** `message/send`, `tasks/get`, `tasks/cancel`
- **Agent card** served at `/.well-known/agent.json`  
- **Task lifecycle management** with proper state transitions
- **Professional error handling** with informative responses

### State Management

The agent uses intelligent state markers:
- `[NEED_MORE_INFO]` → TaskState.input_required
- `[REFERRAL_COMPLETE]` → TaskState.completed
- `[REFERRAL_FAILED]` → TaskState.failed

## Development Status

- **Current Phase:** Phase 2 Complete ✅
- **Features:** Multi-turn conversations, state management, context preservation
- **Test Coverage:** 10/10 comprehensive scenarios passing
- **Next Phase:** Phase 3 - Tool integration for NPPES/insurance APIs

## Security & Compliance

- **HIPAA considerations:** No PHI stored persistently
- **API key security:** Environment variable configuration only
- **Professional standards:** Medical communication protocols followed
- **No medical advice:** Agent scope limited to referral processing

## Development

### Project Structure
```
├── __main__.py              # Server entry point
├── agent_executor.py        # A2A protocol bridge  
├── agent.py                 # Core agent logic
├── config.py                # Configuration management
├── .well-known/
│   └── agent.json          # A2A agent card
├── pyproject.toml          # Python project config
├── test_a2a_agent.py       # Test suite
├── tools.py                # Future tool implementations
└── .gitignore              # Git ignore rules
```

### Code Conventions
- **Python 3.11+** with type hints
- **Async/await** patterns throughout
- **A2A SDK** patterns and interfaces
- **Comprehensive testing** with pytest
- **Environment-based** configuration

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Links

- **A2A Specification:** [Agent-to-Agent Protocol](https://www.a2a.ai)
- **Claude API:** [Anthropic Documentation](https://docs.anthropic.com)
- **NPPES API:** [CMS Provider Directory](https://npiregistry.cms.hhs.gov)

---

**Dr. Walter Reed Cardiology Associates**  
*Advancing cardiac care through intelligent automation*