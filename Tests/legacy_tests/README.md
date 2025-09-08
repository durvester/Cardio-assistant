# Legacy Test Files - Archive

This directory contains the previous test implementation that has been replaced by the comprehensive focused test suite in the `tests/` directory.

## Archived Files

### `test_a2a_agent.py` (889 lines)
**Status:** Replaced by focused test suites  
**Issues:** Monolithic, too long, mixed concerns  
**Replacement:** Functionality distributed across:
- `tests/test_a2a_protocol.py` - A2A protocol compliance
- `tests/test_agent_behavior.py` - Agent behavior validation  
- `tests/test_provider_verification.py` - Provider verification
- `tests/test_security.py` - Security testing
- `tests/test_failure_scenarios.py` - Error handling
- `tests/test_edge_cases.py` - Edge case testing

### `test_provider_verification_balanced.py` (242 lines)
**Status:** Consolidated into focused suite  
**Replacement:** `tests/test_provider_verification.py`  
**Improvements:** Enhanced coverage, better organization, anti-hallucination tests

### `test_provider_verification_focused.py` (167 lines)  
**Status:** Consolidated into focused suite  
**Replacement:** `tests/test_provider_verification.py`  
**Improvements:** Systematic provider scenario testing

### `test_npi_validation.py` (135 lines)
**Status:** Consolidated into focused suite  
**Replacement:** `tests/test_provider_verification.py` (TestNPIValidation class)  
**Improvements:** Enhanced NPI validation testing, boundary condition coverage

## Migration Benefits

### Before (Legacy)
- ❌ Monolithic 889-line test file
- ❌ Mixed concerns in single file
- ❌ Difficult to maintain and debug
- ❌ Slow execution due to size
- ❌ Unclear test organization

### After (New Suite)
- ✅ 6 focused test suites (~150-300 lines each)
- ✅ Clear separation of concerns
- ✅ Easy to maintain and debug
- ✅ Parallel execution capability
- ✅ Comprehensive coverage with better organization

## Coverage Mapping

| Legacy Test Coverage | New Test Suite Location |
|---------------------|------------------------|
| Basic functionality | `test_a2a_protocol.py` |
| History preservation | `test_a2a_protocol.py` |
| Task continuation | `test_a2a_protocol.py` |
| State management | `test_agent_behavior.py` |
| Complete workflows | `test_agent_behavior.py` |
| Provider verification scenarios | `test_provider_verification.py` |
| Context awareness | `test_agent_behavior.py` |
| JSON-RPC compliance | `test_a2a_protocol.py` |
| Security validation | `test_security.py` |
| Error handling | `test_failure_scenarios.py` |
| Edge cases | `test_edge_cases.py` |

## Usage Notes

**⚠️ These files are archived and should not be used for active testing.**

The new test suite provides:
- **Better Coverage:** More comprehensive test scenarios
- **Better Organization:** Focused test suites by concern
- **Better Maintainability:** Smaller, focused files
- **Better Performance:** Can run suites in parallel
- **Better Debugging:** Issues isolated to specific areas
- **Better Reporting:** Suite-level success/failure tracking

## Migration Date
**Date:** September 2025  
**Reason:** Replaced monolithic tests with focused, comprehensive test suite  
**Migration by:** Claude Code comprehensive test restructure

---

For current testing, use the new test suite:
```bash
# Use the new comprehensive test runner
python run_tests.py

# Or run specific focused suites
pytest tests/test_a2a_protocol.py
pytest tests/test_agent_behavior.py
pytest tests/test_provider_verification.py
```