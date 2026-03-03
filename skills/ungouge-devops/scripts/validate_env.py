#!/usr/bin/env python3
"""
Environment validation script for ungouge.ai deployments.

Validates that all required environment variables, secrets, and configurations
are properly set before deployment.

Usage:
    python validate_env.py [environment]

Arguments:
    environment: production | staging | development (default: development)
"""

import os
import sys
from typing import List, Tuple, Dict
import json


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


def check_env_var(name: str, required: bool = True, secret: bool = False) -> Tuple[bool, str]:
    """
    Check if an environment variable is set.
    
    Args:
        name: Environment variable name
        required: Whether the variable is required
        secret: Whether to mask the value in output
        
    Returns:
        Tuple of (is_valid, message)
    """
    value = os.getenv(name)
    
    if value is None or value == "":
        if required:
            return False, f"{Colors.RED}✗{Colors.NC} {name}: NOT SET (required)"
        else:
            return True, f"{Colors.YELLOW}○{Colors.NC} {name}: NOT SET (optional)"
    
    if secret:
        masked = value[:4] + "*" * (len(value) - 8) + value[-4:] if len(value) > 8 else "****"
        return True, f"{Colors.GREEN}✓{Colors.NC} {name}: {masked}"
    else:
        return True, f"{Colors.GREEN}✓{Colors.NC} {name}: {value}"


def validate_backend_env(environment: str) -> bool:
    """Validate backend environment variables."""
    print(f"\n{Colors.BLUE}=== Backend Environment ==={Colors.NC}\n")
    
    required_vars = [
        ("DATABASE_URL", True, True),
        ("JWT_SECRET", True, True),
        ("GEMINI_API_KEY", True, True),
    ]
    
    optional_vars = [
        ("REDIS_URL", False, True),
        ("SENTRY_DSN", False, True),
        ("LOG_LEVEL", False, False),
    ]
    
    all_valid = True
    
    for var_name, required, secret in required_vars:
        is_valid, message = check_env_var(var_name, required, secret)
        print(message)
        if not is_valid:
            all_valid = False
    
    print()
    
    for var_name, required, secret in optional_vars:
        is_valid, message = check_env_var(var_name, required, secret)
        print(message)
    
    return all_valid


def validate_frontend_env(environment: str) -> bool:
    """Validate frontend environment variables."""
    print(f"\n{Colors.BLUE}=== Frontend Environment ==={Colors.NC}\n")
    
    required_vars = [
        ("NEXT_PUBLIC_API_URL", True, False),
    ]
    
    optional_vars = [
        ("NEXT_PUBLIC_STRIPE_KEY", False, True),
        ("NEXT_PUBLIC_GA_ID", False, False),
        ("NEXT_PUBLIC_SENTRY_DSN", False, True),
    ]
    
    all_valid = True
    
    for var_name, required, secret in required_vars:
        is_valid, message = check_env_var(var_name, required, secret)
        print(message)
        if not is_valid:
            all_valid = False
    
    print()
    
    for var_name, required, secret in optional_vars:
        is_valid, message = check_env_var(var_name, required, secret)
        print(message)
    
    return all_valid


def validate_gcp_config() -> bool:
    """Validate Google Cloud Platform configuration."""
    print(f"\n{Colors.BLUE}=== GCP Configuration ==={Colors.NC}\n")
    
    required_vars = [
        ("GCP_PROJECT_ID", True, False),
        ("GCP_REGION", False, False),
    ]
    
    all_valid = True
    
    for var_name, required, secret in required_vars:
        is_valid, message = check_env_var(var_name, required, secret)
        print(message)
        if not is_valid:
            all_valid = False
    
    # Check if gcloud is installed
    print()
    if os.system("which gcloud > /dev/null 2>&1") == 0:
        print(f"{Colors.GREEN}✓{Colors.NC} gcloud CLI: installed")
        
        # Check if authenticated
        result = os.popen("gcloud auth list --filter=status:ACTIVE --format='value(account)' 2>/dev/null").read().strip()
        if result:
            print(f"{Colors.GREEN}✓{Colors.NC} gcloud auth: {result}")
        else:
            print(f"{Colors.RED}✗{Colors.NC} gcloud auth: NOT AUTHENTICATED")
            all_valid = False
    else:
        print(f"{Colors.RED}✗{Colors.NC} gcloud CLI: NOT INSTALLED")
        all_valid = False
    
    return all_valid


def validate_vercel_config() -> bool:
    """Validate Vercel configuration."""
    print(f"\n{Colors.BLUE}=== Vercel Configuration ==={Colors.NC}\n")
    
    required_vars = [
        ("VERCEL_ORG_ID", False, False),
        ("VERCEL_PROJECT_ID", False, False),
        ("VERCEL_TOKEN", False, True),
    ]
    
    all_valid = True
    
    for var_name, required, secret in required_vars:
        is_valid, message = check_env_var(var_name, required, secret)
        print(message)
        if not is_valid and required:
            all_valid = False
    
    # Check if vercel CLI is installed
    print()
    if os.system("which vercel > /dev/null 2>&1") == 0:
        print(f"{Colors.GREEN}✓{Colors.NC} vercel CLI: installed")
    else:
        print(f"{Colors.YELLOW}○{Colors.NC} vercel CLI: NOT INSTALLED (optional)")
    
    return all_valid


def check_file_exists(filepath: str, description: str, required: bool = True) -> bool:
    """Check if a required file exists."""
    if os.path.exists(filepath):
        print(f"{Colors.GREEN}✓{Colors.NC} {description}: {filepath}")
        return True
    else:
        if required:
            print(f"{Colors.RED}✗{Colors.NC} {description}: NOT FOUND at {filepath}")
            return False
        else:
            print(f"{Colors.YELLOW}○{Colors.NC} {description}: NOT FOUND at {filepath} (optional)")
            return True


def validate_files() -> bool:
    """Validate required configuration files."""
    print(f"\n{Colors.BLUE}=== Required Files ==={Colors.NC}\n")
    
    files_to_check = [
        ("backend/Dockerfile", "Backend Dockerfile", True),
        ("backend/requirements.txt", "Backend dependencies", True),
        ("frontend/package.json", "Frontend package.json", True),
        ("frontend/.vercel/project.json", "Vercel config", False),
    ]
    
    all_valid = True
    for filepath, description, required in files_to_check:
        if not check_file_exists(filepath, description, required):
            all_valid = False
    
    return all_valid


def main():
    """Main validation function."""
    environment = sys.argv[1] if len(sys.argv) > 1 else "development"
    
    if environment not in ["production", "staging", "development"]:
        print(f"{Colors.RED}Error: Invalid environment '{environment}'")
        print(f"Must be: production, staging, or development{Colors.NC}")
        sys.exit(1)
    
    print(f"\n{Colors.GREEN}{'=' * 60}")
    print(f"Ungouge Environment Validation")
    print(f"Environment: {environment}")
    print(f"{'=' * 60}{Colors.NC}\n")
    
    results = {
        "Backend": validate_backend_env(environment),
        "Frontend": validate_frontend_env(environment),
        "GCP": validate_gcp_config(),
        "Vercel": validate_vercel_config(),
        "Files": validate_files(),
    }
    
    print(f"\n{Colors.BLUE}=== Summary ==={Colors.NC}\n")
    
    all_passed = True
    for component, passed in results.items():
        status = f"{Colors.GREEN}PASS{Colors.NC}" if passed else f"{Colors.RED}FAIL{Colors.NC}"
        print(f"{component}: {status}")
        if not passed:
            all_passed = False
    
    print()
    
    if all_passed:
        print(f"{Colors.GREEN}✅ All checks passed! Ready for deployment.{Colors.NC}\n")
        sys.exit(0)
    else:
        print(f"{Colors.RED}❌ Some checks failed. Fix issues before deploying.{Colors.NC}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
