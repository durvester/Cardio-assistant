#!/usr/bin/env python3
"""
Main test runner for Walter Reed Cardiology Agent.

Orchestrates all test categories and generates comprehensive reports.
"""

import asyncio
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import pytest
import yaml
import json
from datetime import datetime
import httpx

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))


class AgentTestRunner:
    """Orchestrates all agent tests with reporting."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = {}
        self.token_usage = {}
        self.test_start_time = None
        self.test_end_time = None
    
    async def check_server_health(self) -> bool:
        """Check if the agent server is running."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Try to get agent card
                response = await client.get(f"{self.base_url}/.well-known/agent-card.json")
                return response.status_code == 200
        except:
            return False
    
    def load_test_scenarios(self) -> Dict[str, Any]:
        """Load test scenarios from YAML."""
        scenarios_path = Path(__file__).parent / "fixtures" / "referral_scenarios.yaml"
        if scenarios_path.exists():
            with open(scenarios_path, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    async def run_behavior_tests(self) -> Dict[str, Any]:
        """Run all behavior tests."""
        print("\n" + "="*60)
        print("RUNNING BEHAVIOR TESTS")
        print("="*60)
        
        test_modules = [
            "tests.behavior.test_guardrails",
            "tests.behavior.test_workflow_order",
            "tests.behavior.test_state_markers",
            "tests.behavior.test_scheduling"
        ]
        
        results = {}
        for module in test_modules:
            print(f"\n📋 Testing: {module.split('.')[-1]}")
            result = pytest.main([
                f"{module.replace('.', '/')}.py",
                "-v",
                "--tb=short",
                "--capture=no"
            ])
            results[module] = {
                "passed": result == 0,
                "exit_code": result
            }
        
        return results
    
    async def run_tool_tests(self) -> Dict[str, Any]:
        """Run tool verification tests."""
        print("\n" + "="*60)
        print("RUNNING TOOL VERIFICATION TESTS")
        print("="*60)
        
        test_modules = [
            "tests.tools.test_provider_verification"
        ]
        
        results = {}
        for module in test_modules:
            print(f"\n🔧 Testing: {module.split('.')[-1]}")
            result = pytest.main([
                f"{module.replace('.', '/')}.py",
                "-v",
                "--tb=short",
                "--capture=no"
            ])
            results[module] = {
                "passed": result == 0,
                "exit_code": result
            }
        
        return results
    
    async def run_scenario_tests(self) -> Dict[str, Any]:
        """Run predefined scenarios from fixtures."""
        print("\n" + "="*60)
        print("RUNNING SCENARIO TESTS")
        print("="*60)
        
        scenarios = self.load_test_scenarios()
        results = {}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for category, scenario_list in scenarios.items():
                print(f"\n📚 Category: {category}")
                category_results = []
                
                for scenario in scenario_list:
                    if isinstance(scenario, dict):
                        result = await self.run_single_scenario(client, scenario)
                        category_results.append(result)
                        
                        # Print result
                        status = "✅" if result["passed"] else "❌"
                        print(f"  {status} {scenario.get('scenario', 'unknown')}: {result.get('reason', '')}")
                
                results[category] = category_results
        
        return results
    
    async def run_single_scenario(
        self, 
        client: httpx.AsyncClient,
        scenario: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run a single test scenario."""
        import uuid
        
        task_id = None
        context_id = None
        messages_sent = 0
        
        try:
            for message in scenario.get("messages", []):
                # Prepare message
                message_data = {
                    "role": "user",
                    "parts": [{"kind": "text", "text": message}],
                    "messageId": str(uuid.uuid4()),
                    "kind": "message"
                }
                
                if task_id and context_id:
                    message_data["taskId"] = task_id
                    message_data["contextId"] = context_id
                
                # Send message
                request_data = {
                    "jsonrpc": "2.0",
                    "method": "message/send",
                    "id": str(uuid.uuid4()),
                    "params": {
                        "message": message_data,
                        "configuration": {"blocking": True}
                    }
                }
                
                response = await client.post(self.base_url, json=request_data)
                response_data = response.json()
                
                # Extract IDs on first message
                if not task_id:
                    result = response_data.get("result", {})
                    task_id = result.get("id")
                    context_id = result.get("contextId")
                
                messages_sent += 1
                
                # Check if we've reached expected outcome
                agent_text = self.extract_agent_text(response_data)
                expected_outcome = scenario.get("expected_outcome")
                
                if expected_outcome and expected_outcome in agent_text:
                    # Check for expected content
                    expected_content = scenario.get("expected_content", [])
                    for content in expected_content:
                        if content.lower() not in agent_text.lower():
                            return {
                                "passed": False,
                                "scenario": scenario.get("scenario"),
                                "reason": f"Missing expected content: {content}"
                            }
                    
                    return {
                        "passed": True,
                        "scenario": scenario.get("scenario"),
                        "reason": "Completed successfully",
                        "turns": messages_sent
                    }
            
            # If we've sent all messages without reaching outcome
            return {
                "passed": False,
                "scenario": scenario.get("scenario"),
                "reason": f"Did not reach expected outcome: {scenario.get('expected_outcome')}"
            }
            
        except Exception as e:
            return {
                "passed": False,
                "scenario": scenario.get("scenario"),
                "reason": f"Error: {str(e)}"
            }
    
    def extract_agent_text(self, response_data: Dict[str, Any]) -> str:
        """Extract agent text from response."""
        result = response_data.get("result", {})
        status_msg = result.get("status", {}).get("message", {})
        if status_msg and status_msg.get("parts"):
            return status_msg["parts"][0].get("text", "")
        return ""
    
    async def run_all_tests(self):
        """Run all test categories."""
        self.test_start_time = datetime.now()
        
        # Check server health first
        print("\n🏥 Checking server health...")
        if not await self.check_server_health():
            print("❌ ERROR: Agent server is not running at", self.base_url)
            print("Please start the server with: python __main__.py")
            return
        print("✅ Server is healthy")
        
        # Run test categories
        self.results["behavior"] = await self.run_behavior_tests()
        self.results["tools"] = await self.run_tool_tests()
        self.results["scenarios"] = await self.run_scenario_tests()
        
        self.test_end_time = datetime.now()
        
        # Generate final report
        self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive test report."""
        print("\n" + "="*80)
        print("COMPREHENSIVE TEST REPORT")
        print("="*80)
        
        # Time stats
        if self.test_start_time and self.test_end_time:
            duration = (self.test_end_time - self.test_start_time).total_seconds()
            print(f"\n⏱️  Test Duration: {duration:.2f} seconds")
        
        # Category summaries
        print("\n📊 Test Results by Category:")
        print("-" * 40)
        
        # Behavior tests
        if "behavior" in self.results:
            behavior_passed = sum(1 for r in self.results["behavior"].values() if r["passed"])
            behavior_total = len(self.results["behavior"])
            print(f"Behavior Tests: {behavior_passed}/{behavior_total} passed")
            for module, result in self.results["behavior"].items():
                status = "✅" if result["passed"] else "❌"
                print(f"  {status} {module.split('.')[-1]}")
        
        # Tool tests
        if "tools" in self.results:
            tools_passed = sum(1 for r in self.results["tools"].values() if r["passed"])
            tools_total = len(self.results["tools"])
            print(f"\nTool Tests: {tools_passed}/{tools_total} passed")
            for module, result in self.results["tools"].items():
                status = "✅" if result["passed"] else "❌"
                print(f"  {status} {module.split('.')[-1]}")
        
        # Scenario tests
        if "scenarios" in self.results:
            print(f"\nScenario Tests:")
            for category, scenarios in self.results["scenarios"].items():
                if scenarios:
                    passed = sum(1 for s in scenarios if s.get("passed"))
                    total = len(scenarios)
                    print(f"  {category}: {passed}/{total} passed")
        
        # Critical failures
        print("\n⚠️  Critical Issues:")
        print("-" * 40)
        critical_found = False
        
        # Check for emergency handling failures
        if "scenarios" in self.results:
            failure_scenarios = self.results["scenarios"].get("failure_scenarios", [])
            for scenario in failure_scenarios:
                if not scenario.get("passed") and "emergency" in scenario.get("scenario", "").lower():
                    print(f"  ❌ CRITICAL: Emergency handling failed - {scenario.get('reason')}")
                    critical_found = True
        
        if not critical_found:
            print("  ✅ No critical issues found")
        
        # Overall assessment
        print("\n🎯 Overall Assessment:")
        print("-" * 40)
        
        total_tests = 0
        passed_tests = 0
        
        # Count all tests
        for category, results in self.results.items():
            if category in ["behavior", "tools"]:
                for result in results.values():
                    total_tests += 1
                    if result["passed"]:
                        passed_tests += 1
            elif category == "scenarios":
                for scenario_list in results.values():
                    for scenario in scenario_list:
                        total_tests += 1
                        if scenario.get("passed"):
                            passed_tests += 1
        
        if total_tests > 0:
            success_rate = (passed_tests / total_tests) * 100
            print(f"Total: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
            
            if success_rate >= 90:
                print("✅ Status: EXCELLENT - Ready for production")
            elif success_rate >= 75:
                print("⚠️  Status: GOOD - Minor fixes needed")
            elif success_rate >= 60:
                print("⚠️  Status: FAIR - Several issues to address")
            else:
                print("❌ Status: NEEDS WORK - Significant issues detected")
        
        # Recommendations
        print("\n💡 Recommendations:")
        print("-" * 40)
        
        if success_rate < 90:
            print("1. Review failed tests and fix critical issues")
            print("2. Ensure emergency handling works correctly")
            print("3. Verify provider tool integration")
            print("4. Test conversation flow thoroughly")
        else:
            print("1. Consider adding more edge case tests")
            print("2. Monitor token usage in production")
            print("3. Add performance benchmarks")
        
        # Save report to file
        self.save_report()
    
    def save_report(self):
        """Save test report to file."""
        report_path = Path(__file__).parent / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "duration": (self.test_end_time - self.test_start_time).total_seconds() if self.test_start_time else 0,
            "results": self.results
        }
        
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"\n📄 Report saved to: {report_path}")


async def main():
    """Main entry point."""
    runner = AgentTestRunner()
    await runner.run_all_tests()


if __name__ == "__main__":
    print("🚀 Walter Reed Cardiology Agent - Comprehensive Test Suite")
    print("="*60)
    asyncio.run(main())