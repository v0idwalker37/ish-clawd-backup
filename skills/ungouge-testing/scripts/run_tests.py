#!/usr/bin/env python3
"""
Test runner for ungouge.ai backend with coverage reporting.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --unit             # Run only unit tests
    python run_tests.py --integration      # Run only integration tests
    python run_tests.py --coverage         # Run with coverage report
    python run_tests.py --verbose          # Verbose output
    python run_tests.py --file test_api.py # Run specific test file
"""

import sys
import subprocess
import argparse
from pathlib import Path
from typing import List


def run_pytest(args: List[str]) -> int:
    """
    Run pytest with the given arguments.
    
    Args:
        args: List of command-line arguments to pass to pytest
        
    Returns:
        Exit code from pytest
    """
    cmd = ["pytest"] + args
    print(f"Running: {' '.join(cmd)}")
    print("-" * 80)
    result = subprocess.run(cmd)
    return result.returncode


def main():
    """Parse arguments and run tests."""
    parser = argparse.ArgumentParser(
        description="Test runner for ungouge.ai backend"
    )
    
    parser.add_argument(
        "--unit",
        action="store_true",
        help="Run only unit tests (fast)"
    )
    
    parser.add_argument(
        "--integration",
        action="store_true",
        help="Run only integration tests"
    )
    
    parser.add_argument(
        "--security",
        action="store_true",
        help="Run only security tests"
    )
    
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage report"
    )
    
    parser.add_argument(
        "--html-coverage",
        action="store_true",
        help="Generate HTML coverage report (implies --coverage)"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--file",
        type=str,
        help="Run specific test file"
    )
    
    parser.add_argument(
        "--failed",
        action="store_true",
        help="Re-run only failed tests from last run"
    )
    
    parser.add_argument(
        "--pdb",
        action="store_true",
        help="Drop into debugger on failure"
    )
    
    parser.add_argument(
        "extra_args",
        nargs=argparse.REMAINDER,
        help="Additional arguments to pass to pytest"
    )
    
    args = parser.parse_args()
    
    # Build pytest command
    pytest_args = []
    
    # Test selection
    if args.unit:
        pytest_args.extend(["-m", "unit"])
    elif args.integration:
        pytest_args.extend(["-m", "integration"])
    elif args.security:
        pytest_args.extend(["-m", "security"])
    
    # Coverage
    if args.coverage or args.html_coverage:
        pytest_args.extend([
            "--cov=app",
            "--cov-report=term-missing",
        ])
        if args.html_coverage:
            pytest_args.append("--cov-report=html")
    
    # Verbosity
    if args.verbose:
        pytest_args.append("-vv")
    else:
        pytest_args.append("-v")
    
    # Show test durations
    pytest_args.append("--durations=10")
    
    # Specific file
    if args.file:
        pytest_args.append(args.file)
    
    # Re-run failed
    if args.failed:
        pytest_args.append("--lf")
    
    # Debugger
    if args.pdb:
        pytest_args.append("--pdb")
    
    # Add any extra arguments
    if args.extra_args:
        pytest_args.extend(args.extra_args)
    
    # Run tests
    exit_code = run_pytest(pytest_args)
    
    # Print summary
    print("\n" + "=" * 80)
    if exit_code == 0:
        print("✅ All tests passed!")
        if args.html_coverage:
            print("\n📊 Coverage report generated at: htmlcov/index.html")
            print("   Open with: open htmlcov/index.html")
    else:
        print("❌ Some tests failed!")
        print("\nTo re-run only failed tests: python run_tests.py --failed")
    print("=" * 80)
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
