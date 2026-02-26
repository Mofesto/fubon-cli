#!/usr/bin/env python3
"""Test fubon-cli commands with real data scenarios.

This script validates:
- Command execution and JSON output formatting
- Error handling for various edge cases
- Data structure validation
- Real-world usage scenarios
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class FubonCLITester:
    """Test runner for fubon-cli commands with real data."""

    def __init__(self, test_symbol: str = "2330", verbose: bool = False):
        """Initialize the tester with configuration.

        Args:
            test_symbol: Stock symbol to use for testing
            verbose: Enable verbose output

        """
        self.test_symbol = test_symbol
        self.verbose = verbose
        self.results: List[Dict] = []
        self.colors = {
            "RESET": "\033[0m",
            "RED": "\033[91m",
            "GREEN": "\033[92m",
            "YELLOW": "\033[93m",
            "BLUE": "\033[94m",
            "CYAN": "\033[96m",
        }

    def color_print(self, text: str, color: str = "RESET") -> None:
        """Print colored text to console."""
        if sys.platform == "win32":
            # Enable ANSI colors on Windows
            import os
            os.system("")
        print(f"{self.colors.get(color, '')}{text}{self.colors['RESET']}")

    def print_header(self, message: str) -> None:
        """Print a formatted test section header."""
        print()
        self.color_print("=" * 60, "CYAN")
        self.color_print(message, "CYAN")
        self.color_print("=" * 60, "CYAN")
        print()

    def run_command(self, command: str) -> Tuple[bool, str, str]:
        """Execute a CLI command and return success status, stdout, stderr.

        Args:
            command: Command string to execute

        Returns:
            Tuple of (success, stdout, stderr)

        """
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
            )
            return True, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timeout"
        except Exception as e:
            return False, "", str(e)

    def validate_json(self, output: str) -> Tuple[bool, Optional[Dict]]:
        """Validate if output is valid JSON.

        Args:
            output: Command output string

        Returns:
            Tuple of (is_valid, parsed_json)

        """
        try:
            data = json.loads(output)
            return True, data
        except json.JSONDecodeError:
            return False, None

    def test_command(
        self,
        test_name: str,
        command: str,
        expected_fields: Optional[List[str]] = None,
        allow_error: bool = False,
    ) -> bool:
        """Test a single command and record results.

        Args:
            test_name: Name of the test
            command: Command to execute
            expected_fields: List of expected fields in JSON output
            allow_error: Whether errors are acceptable for this test

        Returns:
            True if test passed, False otherwise

        """
        print(f"Testing: {test_name}...", end=" ")

        success, stdout, stderr = self.run_command(command)

        # Determine if output is valid
        is_valid_json, json_data = self.validate_json(stdout)

        # Check expected fields if JSON is valid
        has_expected_fields = True
        if is_valid_json and expected_fields and json_data:
            if isinstance(json_data, dict):
                has_expected_fields = any(
                    field in json_data for field in expected_fields
                )
            elif isinstance(json_data, list) and len(json_data) > 0:
                has_expected_fields = any(
                    field in json_data[0] for field in expected_fields
                )

        # Determine pass/fail
        passed = success and (is_valid_json or allow_error)

        # Record result
        result = {
            "test_name": test_name,
            "command": command,
            "passed": passed,
            "timestamp": datetime.now().isoformat(),
            "stdout": stdout[:500] if self.verbose else stdout[:100],
            "stderr": stderr[:200] if stderr else "",
            "is_valid_json": is_valid_json,
            "has_expected_fields": has_expected_fields,
        }
        self.results.append(result)

        # Print result
        if passed:
            self.color_print("✓ PASS", "GREEN")
        else:
            self.color_print("✗ FAIL", "RED")
            if stderr:
                print(f"  Error: {stderr[:100]}")

        if self.verbose and stdout:
            print(f"  Output: {stdout[:200]}")

        return passed

    def run_all_tests(self) -> None:
        """Execute all test suites."""
        self.color_print("\n🧪 Fubon CLI Real Data Testing", "CYAN")
        self.color_print("=" * 60, "CYAN")

        # Test Suite 1: Basic CLI Functionality
        self.print_header("Test Suite 1: Basic CLI Functionality")
        self.test_command(
            "CLI Version Check",
            "fubon --version",
            allow_error=True,
        )
        self.test_command(
            "CLI Help",
            "fubon --help",
            allow_error=True,
        )

        # Test Suite 2: Authentication
        self.print_header("Test Suite 2: Authentication Status")
        self.test_command(
            "Login Status Check",
            "fubon login status",
            expected_fields=["success", "logged_in"],
        )

        # Test Suite 3: Market Data Commands
        self.print_header("Test Suite 3: Market Data Commands")
        self.test_command(
            f"Get Stock Quote ({self.test_symbol})",
            f"fubon market quote {self.test_symbol}",
            expected_fields=["symbol", "price", "success"],
        )
        self.test_command(
            f"Get Stock Ticker ({self.test_symbol})",
            f"fubon market ticker {self.test_symbol}",
            expected_fields=["symbol", "success"],
        )
        self.test_command(
            f"Get Stock Candles ({self.test_symbol})",
            f"fubon market candles {self.test_symbol} --timeframe 5",
            expected_fields=["success", "data"],
        )
        self.test_command(
            "Get Market Snapshot (TSE)",
            "fubon market snapshot TSE",
            expected_fields=["success", "data"],
        )

        # Test Suite 4: Account Information
        self.print_header("Test Suite 4: Account Information (Read-only)")
        self.test_command(
            "Get Account Inventory",
            "fubon account inventory",
            expected_fields=["success", "data"],
        )
        self.test_command(
            "Get Unrealized P&L",
            "fubon account unrealized",
            expected_fields=["success"],
        )
        self.test_command(
            "Get Settlement Info",
            "fubon account settlement",
            expected_fields=["success"],
        )

        # Test Suite 5: Order Management (Read-only)
        self.print_header("Test Suite 5: Order Management (Read-only)")
        self.test_command(
            "Query Current Orders",
            "fubon stock orders",
            expected_fields=["success", "data"],
        )

        # Test Suite 6: Edge Cases and Error Handling
        self.print_header("Test Suite 6: Edge Cases and Error Handling")
        self.test_command(
            "Invalid Symbol Handling",
            "fubon market quote INVALID999",
            expected_fields=["success", "error"],
        )
        self.test_command(
            "Help for Stock Commands",
            "fubon stock --help",
            allow_error=True,
        )
        self.test_command(
            "Help for Market Commands",
            "fubon market --help",
            allow_error=True,
        )

    def generate_report(self) -> None:
        """Generate and display test summary report."""
        self.print_header("Test Summary Report")

        total = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        failed = total - passed
        pass_rate = (passed / total * 100) if total > 0 else 0

        print(f"Total Tests:  {total}")
        self.color_print(f"Passed:       {passed}", "GREEN")
        if failed > 0:
            self.color_print(f"Failed:       {failed}", "RED")
        else:
            self.color_print(f"Failed:       {failed}", "GREEN")

        color = "GREEN" if pass_rate >= 80 else "YELLOW" if pass_rate >= 60 else "RED"
        self.color_print(f"Pass Rate:    {pass_rate:.1f}%", color)

        # Save detailed report
        report_path = Path(__file__).parent / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "summary": {
                        "total": total,
                        "passed": passed,
                        "failed": failed,
                        "pass_rate": pass_rate,
                        "timestamp": datetime.now().isoformat(),
                    },
                    "results": self.results,
                },
                f,
                indent=2,
                ensure_ascii=False,
            )

        print(f"\n📄 Detailed results saved to: {report_path}")

        # Show failed tests
        if failed > 0:
            self.color_print("\n❌ Failed Tests Details:", "RED")
            for result in self.results:
                if not result["passed"]:
                    self.color_print(f"  - {result['test_name']}", "RED")
                    if result["stderr"]:
                        print(f"    Error: {result['stderr'][:100]}")

        self.color_print("\n✨ Testing Complete!", "CYAN")


def main():
    """Run the test script."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Test fubon-cli commands with real data"
    )
    parser.add_argument(
        "--symbol",
        default="2330",
        help="Stock symbol to use for testing (default: 2330)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show verbose output",
    )
    args = parser.parse_args()

    tester = FubonCLITester(test_symbol=args.symbol, verbose=args.verbose)
    tester.run_all_tests()
    tester.generate_report()

    # Exit with appropriate code
    failed = sum(1 for r in tester.results if not r["passed"])
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
