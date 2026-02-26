#!/usr/bin/env python3
"""Data Quality Checker for fubon-cli.

This script validates the quality and structure of real data returned by fubon-cli commands.
It checks:
- Data completeness
- Field types and formats
- Value ranges and constraints
- Consistency across commands
"""

import json
import subprocess
from datetime import datetime
from typing import Any, Dict, List, Optional


class DataQualityChecker:
    """Validate data quality from fubon-cli commands."""

    def __init__(self):
        """Initialize the data quality checker."""
        self.issues: List[Dict[str, Any]] = []
        self.checks_passed = 0
        self.checks_failed = 0

    def run_command(self, command: str) -> Optional[Dict]:
        """Execute command and return parsed JSON output."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.stdout:
                return json.loads(result.stdout)
        except Exception as e:
            print(f"❌ Command failed: {command}\n   Error: {e}")
        return None

    def check_field_exists(self, data: Dict, field: str, context: str) -> bool:
        """Check if field exists in data."""
        if field not in data:
            self.issues.append({
                "type": "missing_field",
                "field": field,
                "context": context,
                "severity": "high"
            })
            self.checks_failed += 1
            return False
        self.checks_passed += 1
        return True

    def check_field_type(
        self, data: Dict, field: str, expected_type: type, context: str
    ) -> bool:
        """Check if field has correct type."""
        if field not in data:
            return False
        if not isinstance(data[field], expected_type):
            self.issues.append({
                "type": "type_mismatch",
                "field": field,
                "expected": expected_type.__name__,
                "actual": type(data[field]).__name__,
                "context": context,
                "severity": "medium"
            })
            self.checks_failed += 1
            return False
        self.checks_passed += 1
        return True

    def check_numeric_range(
        self, data: Dict, field: str, min_val: float, max_val: float, context: str
    ) -> bool:
        """Check if numeric value is within expected range."""
        if field not in data or not isinstance(data[field], (int, float)):
            return False
        value = data[field]
        if not (min_val <= value <= max_val):
            self.issues.append({
                "type": "out_of_range",
                "field": field,
                "value": value,
                "expected_range": f"{min_val}-{max_val}",
                "context": context,
                "severity": "low"
            })
            self.checks_failed += 1
            return False
        self.checks_passed += 1
        return True

    def check_string_format(
        self, data: Dict, field: str, pattern: str, context: str
    ) -> bool:
        """Check if string matches expected pattern."""
        import re
        if field not in data or not isinstance(data[field], str):
            return False
        if not re.match(pattern, data[field]):
            self.issues.append({
                "type": "format_mismatch",
                "field": field,
                "value": data[field],
                "expected_pattern": pattern,
                "context": context,
                "severity": "low"
            })
            self.checks_failed += 1
            return False
        self.checks_passed += 1
        return True

    def validate_quote_data(self, symbol: str = "2330") -> None:
        """Validate stock quote data quality."""
        print(f"\n🔍 Validating Quote Data for {symbol}...")
        data = self.run_command(f"fubon market quote {symbol}")

        if not data:
            print("❌ Failed to get quote data")
            return

        context = f"market quote {symbol}"

        # Check essential fields
        self.check_field_exists(data, "success", context)

        if data.get("success"):
            # If API returns data in a nested structure
            quote_data = data.get("data", data)

            # Common quote fields
            essential_fields = ["symbol", "price", "volume"]
            for field in essential_fields:
                if self.check_field_exists(quote_data, field, context):
                    # Validate symbol format (4 digits)
                    if field == "symbol":
                        self.check_string_format(
                            quote_data, field, r"^\d{4}$", context
                        )
                    # Validate price is positive
                    elif field == "price" and isinstance(quote_data.get(field), (int, float)):
                        value = quote_data[field]
                        if value > 0:
                            self.checks_passed += 1
                        else:
                            self.issues.append({
                                "type": "invalid_value",
                                "field": field,
                                "value": value,
                                "context": context,
                                "severity": "high"
                            })
                            self.checks_failed += 1

            print("✓ Quote data validation complete")
        else:
            error = data.get("error", "Unknown error")
            print(f"⚠️  Quote returned error: {error}")

    def validate_orders_data(self) -> None:
        """Validate orders data structure."""
        print("\n🔍 Validating Orders Data...")
        data = self.run_command("fubon stock orders")

        if not data:
            print("❌ Failed to get orders data")
            return

        context = "stock orders"

        if isinstance(data, list):
            if len(data) == 0:
                print("ℹ️  No active orders (this is normal)")
            else:
                print(f"ℹ️  Found {len(data)} orders")
                # Check first order structure
                if len(data) > 0:
                    order = data[0]
                    order_fields = ["order_no", "symbol", "quantity", "price"]
                    for field in order_fields:
                        if field in order:
                            self.checks_passed += 1
        elif isinstance(data, dict):
            self.check_field_exists(data, "success", context)
            if data.get("data"):
                orders = data["data"]
                print(f"ℹ️  Found {len(orders)} orders")

        print("✓ Orders data validation complete")

    def validate_inventory_data(self) -> None:
        """Validate inventory/portfolio data."""
        print("\n🔍 Validating Inventory Data...")
        data = self.run_command("fubon account inventory")

        if not data:
            print("❌ Failed to get inventory data")
            return

        context = "account inventory"

        if isinstance(data, dict):
            self.check_field_exists(data, "success", context)

            if data.get("data"):
                inventory = data["data"]
                if isinstance(inventory, list):
                    print(f"ℹ️  Found {len(inventory)} positions")
                    if len(inventory) > 0:
                        # Check first position structure
                        position = inventory[0]
                        position_fields = ["symbol", "quantity"]
                        for field in position_fields:
                            if field in position:
                                self.checks_passed += 1

        print("✓ Inventory data validation complete")

    def validate_candles_data(self, symbol: str = "2330") -> None:
        """Validate candlestick/K-line data."""
        print(f"\n🔍 Validating Candles Data for {symbol}...")
        data = self.run_command(f"fubon market candles {symbol} --timeframe 5")

        if not data:
            print("❌ Failed to get candles data")
            return

        context = f"market candles {symbol}"

        if isinstance(data, dict):
            self.check_field_exists(data, "success", context)

            if data.get("data"):
                candles = data["data"]
                if isinstance(candles, list) and len(candles) > 0:
                    print(f"ℹ️  Found {len(candles)} candles")
                    # Check first candle structure
                    candle = candles[0]
                    candle_fields = ["open", "high", "low", "close", "volume"]
                    for field in candle_fields:
                        self.check_field_exists(candle, field, context)
                        # Validate OHLC relationships
                    if all(f in candle for f in ["open", "high", "low", "close"]):
                        open_price, high_price, low_price, close_price = (
                            candle["open"], candle["high"], candle["low"], candle["close"]
                        )
                        if high_price >= max(open_price, close_price) and low_price <= min(open_price, close_price):
                            self.checks_passed += 1
                        else:
                            self.issues.append({
                                "type": "invalid_ohlc",
                                "values": f"O:{open_price} H:{high_price} L:{low_price} C:{close_price}",
                                "context": context,
                                "severity": "high"
                            })
                            self.checks_failed += 1

        print("✓ Candles data validation complete")

    def generate_report(self) -> None:
        """Generate data quality report."""
        print("\n" + "=" * 60)
        print("📊 Data Quality Report")
        print("=" * 60)

        total_checks = self.checks_passed + self.checks_failed
        if total_checks > 0:
            quality_score = (self.checks_passed / total_checks) * 100
        else:
            quality_score = 0

        print(f"\nTotal Checks:    {total_checks}")
        print(f"✓ Passed:        {self.checks_passed}")
        print(f"✗ Failed:        {self.checks_failed}")
        print(f"Quality Score:   {quality_score:.1f}%")

        if self.issues:
            print("\n⚠️  Issues Found:\n")
            # Group by severity
            high = [i for i in self.issues if i["severity"] == "high"]
            medium = [i for i in self.issues if i["severity"] == "medium"]
            low = [i for i in self.issues if i["severity"] == "low"]

            if high:
                print(f"🔴 High Severity ({len(high)}):")
                for issue in high[:5]:  # Show first 5
                    print(f"   - {issue['type']}: {issue.get('field', 'N/A')} in {issue['context']}")

            if medium:
                print(f"\n🟡 Medium Severity ({len(medium)}):")
                for issue in medium[:5]:
                    print(f"   - {issue['type']}: {issue.get('field', 'N/A')} in {issue['context']}")

            if low:
                print(f"\n🟢 Low Severity ({len(low)}):")
                for issue in low[:3]:
                    print(f"   - {issue['type']}: {issue.get('field', 'N/A')} in {issue['context']}")

            # Save detailed report
            report_path = f"data_quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump({
                    "summary": {
                        "total_checks": total_checks,
                        "passed": self.checks_passed,
                        "failed": self.checks_failed,
                        "quality_score": quality_score,
                        "timestamp": datetime.now().isoformat()
                    },
                    "issues": self.issues
                }, f, indent=2, ensure_ascii=False)
            print(f"\n📄 Detailed report saved: {report_path}")
        else:
            print("\n✨ No data quality issues found!")

    def run_all_checks(self) -> None:
        """Run all data quality checks."""
        print("🔬 Starting Data Quality Checks...")
        print("=" * 60)

        try:
            self.validate_quote_data("2330")
            self.validate_candles_data("2330")
            self.validate_orders_data()
            self.validate_inventory_data()
        except Exception as e:
            print(f"\n❌ Error during validation: {e}")
        finally:
            self.generate_report()


def main():
    """Run the data quality validation."""
    checker = DataQualityChecker()
    checker.run_all_checks()

    # Exit with code 1 if quality score is below 80%
    total = checker.checks_passed + checker.checks_failed
    if total > 0:
        score = (checker.checks_passed / total) * 100
        if score < 80:
            exit(1)
    exit(0)


if __name__ == "__main__":
    main()
