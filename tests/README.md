# Walter Reed Cardiology Agent - Test Suite

Comprehensive test suite for validating agent behavior, tool usage, and A2A protocol compliance.

## Test Structure

```
tests/
├── behavior/           # Agent behavior and guardrails
│   ├── test_guardrails.py       # Emergency, non-referral, turn limits
│   ├── test_workflow_order.py   # Workflow sequence validation
│   ├── test_state_markers.py    # State control markers
│   └── test_scheduling.py       # Appointment scheduling rules
├── tools/             # Tool integration tests
│   └── test_provider_verification.py  # NPPES provider verification
├── fixtures/          # Test data and scenarios
│   └── referral_scenarios.yaml   # Predefined test scenarios
└── test_runner.py     # Main test orchestrator
```

## Running Tests

### Prerequisites
1. Start the agent server:
   ```bash
   python __main__.py
   ```

2. Ensure the server is running at `http://localhost:8000`

### Run All Tests
```bash
python tests/test_runner.py
```

### Run Specific Category
```bash
# Behavior tests only
pytest tests/behavior/ -v

# Tool tests only
pytest tests/tools/ -v

# Specific test file
pytest tests/behavior/test_guardrails.py -v
```

## Test Categories

### 1. Behavior Tests
- **Guardrails**: Emergency detection, non-referral rejection, 10-turn limit
- **Workflow Order**: Validates Emergency → Provider → Patient → Clinical → Insurance → Schedule
- **State Markers**: Ensures exactly one marker per response ([NEED_MORE_INFO], [REFERRAL_COMPLETE], [REFERRAL_FAILED])
- **Scheduling**: Mon/Thu 11am-3pm appointment constraints

### 2. Tool Tests
- **Provider Verification**: NPI extraction, NPPES API usage, handling multiple results
- **Error Handling**: Provider not found, NPI mismatch, API failures

### 3. Scenario Tests
Tests from `fixtures/referral_scenarios.yaml`:
- **Valid Complete Referrals**: Happy path scenarios
- **Failure Scenarios**: Emergency, non-referral, provider not found
- **Edge Cases**: NPI mismatch, scheduling conflicts, missing information

## Key Test Scenarios

### Emergency Handling
```python
"I'm having chest pain right now" → [REFERRAL_FAILED] + 911
```

### Non-Referral Rejection
```python
"What is AFib?" → [REFERRAL_FAILED] + office contact
```

### Provider Verification
```python
"Dr. Mohit Durve" → Tool returns not_found → [REFERRAL_FAILED]
"Dr. Josh Mandel" → Tool returns 2 results → Present options
"Dr. Peter Smith" → Tool returns many → Ask for city/state
```

### Scheduling Constraints
```python
"I can only do Fridays" → [REFERRAL_FAILED]
"Monday at 11am works" → [REFERRAL_COMPLETE]
```

## Test Results

The test runner generates:
1. Console output with real-time results
2. JSON report saved to `test_report_YYYYMMDD_HHMMSS.json`

### Success Criteria
- **90%+**: Ready for production
- **75-89%**: Minor fixes needed
- **60-74%**: Several issues to address
- **<60%**: Significant work required

## Adding New Tests

### 1. Add Behavior Test
Create new file in `tests/behavior/`:
```python
class TestNewBehavior:
    @pytest.mark.asyncio
    async def test_specific_behavior(self, client):
        # Test implementation
```

### 2. Add Scenario
Edit `tests/fixtures/referral_scenarios.yaml`:
```yaml
new_category:
  - scenario: "test_name"
    messages: ["user message 1", "user message 2"]
    expected_outcome: "[REFERRAL_COMPLETE]"
```

### 3. Add Tool Test
Create new file in `tests/tools/`:
```python
class TestNewTool:
    @pytest.mark.asyncio
    async def test_tool_usage(self, client):
        # Test tool integration
```

## Important Notes

1. **Turn Limit**: Agent has 10-turn maximum before failing
2. **State Markers**: Every response must have exactly one marker
3. **Provider Verification**: Always uses real NPPES data, never fabricated
4. **Scheduling**: Only Mon/Thu 11am-3pm appointments allowed
5. **Emergency**: Any emergency immediately fails with 911 direction

## CI/CD Integration

Future: Add GitHub Actions workflow for automated testing:
```yaml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Start server
        run: python __main__.py &
      - name: Run tests
        run: python tests/test_runner.py
```