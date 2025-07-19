#!/usr/bin/env python3
"""
Setup Checker for WordPress Content Generator

This script checks if all necessary packages are installed and environment
variables are properly configured. It also tests connections to external
services like Supabase and OpenAI.

Usage:
    python check_setup.py [--verbose] [--fix]
    
Options:
    --verbose    Show detailed information about each check
    --fix        Attempt to fix common issues (install missing packages)
"""

import argparse
import importlib
import os
import subprocess
import sys
from typing import Dict, List, Tuple, Optional

# Define colors for terminal output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
ENDC = "\033[0m"
BOLD = "\033[1m"

# Required packages (from requirements.txt)
REQUIRED_PACKAGES = [
    "supabase",
    "openai",
    "pydantic",
    "python-dotenv",
    "fastapi",
    "uvicorn",
    "pytest",
    "requests",
    "python-slugify",
    "tenacity",
    "tiktoken",
]

# Required environment variables
REQUIRED_ENV_VARS = {
    "SUPABASE_URL": "URL for your Supabase project",
    "SUPABASE_KEY": "Anon key for your Supabase project",
    "OPENAI_API_KEY": "API key for OpenAI",
}

# Optional environment variables
OPTIONAL_ENV_VARS = {
    "POCKETFLOW_API_URL": "URL for Pocketflow API",
    "POCKETFLOW_API_KEY": "API key for Pocketflow",
    "WP_API_URL": "WordPress REST API URL",
    "WP_USERNAME": "WordPress username",
    "WP_APP_PASSWORD": "WordPress application password",
    "PEXELS_API_KEY": "API key for Pexels image service",
    "UNSPLASH_API_KEY": "API key for Unsplash image service",
}


def print_status(message: str, status: str, verbose: bool = False, details: str = None):
    """
    Print a status message with color coding.
    
    Args:
        message: The message to print
        status: "OK", "WARNING", "ERROR", or "INFO"
        verbose: Whether to show detailed information
        details: Additional details to show if verbose is True
    """
    status_color = {
        "OK": GREEN,
        "WARNING": YELLOW,
        "ERROR": RED,
        "INFO": BLUE
    }.get(status, "")
    
    print(f"{message:<50} [{status_color}{status}{ENDC}]")
    
    if verbose and details:
        print(f"  {details}")


def check_python_version() -> bool:
    """
    Check if the Python version is compatible.
    
    Returns:
        bool: True if the Python version is compatible, False otherwise
    """
    major, minor, _ = sys.version_info
    
    if major >= 3 and minor >= 10:
        print_status("Python version", "OK", details=f"Python {major}.{minor}")
        return True
    else:
        print_status("Python version", "ERROR", details=f"Python {major}.{minor} (need 3.10+)")
        return False


def check_packages() -> Tuple[List[str], List[str]]:
    """
    Check if all required packages are installed.
    
    Returns:
        Tuple of (installed_packages, missing_packages)
    """
    installed = []
    missing = []
    
    for package in REQUIRED_PACKAGES:
        try:
            importlib.import_module(package.replace("-", "_"))
            installed.append(package)
        except ImportError:
            missing.append(package)
    
    return installed, missing


def check_env_vars() -> Tuple[List[str], List[str], List[str]]:
    """
    Check if all required environment variables are set.
    
    Returns:
        Tuple of (set_vars, missing_vars, optional_vars_set)
    """
    # Try to load .env file if it exists
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # dotenv might not be installed yet
    
    set_vars = []
    missing_vars = []
    optional_vars_set = []
    
    # Check required vars
    for var in REQUIRED_ENV_VARS:
        if os.environ.get(var):
            set_vars.append(var)
        else:
            missing_vars.append(var)
    
    # Check optional vars
    for var in OPTIONAL_ENV_VARS:
        if os.environ.get(var):
            optional_vars_set.append(var)
    
    return set_vars, missing_vars, optional_vars_set


def check_supabase_connection() -> bool:
    """
    Check if we can connect to Supabase.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    if not os.environ.get("SUPABASE_URL") or not os.environ.get("SUPABASE_KEY"):
        print_status("Supabase connection", "SKIPPED", details="Missing credentials")
        return False
    
    try:
        from supabase import create_client
        
        supabase = create_client(
            os.environ.get("SUPABASE_URL"),
            os.environ.get("SUPABASE_KEY")
        )
        
        # Try a simple query
        response = supabase.table("strategic_plans").select("count", count="exact").execute()
        
        print_status("Supabase connection", "OK", details=f"Connected, found {response.count} strategic plans")
        return True
    except Exception as e:
        print_status("Supabase connection", "ERROR", details=str(e))
        return False


def check_openai_connection() -> bool:
    """
    Check if we can connect to OpenAI API.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    if not os.environ.get("OPENAI_API_KEY"):
        print_status("OpenAI connection", "SKIPPED", details="Missing API key")
        return False
    
    try:
        import openai
        
        client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        # Try a simple completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Connection successful' in 5 words or less."}
            ],
            max_tokens=10
        )
        
        print_status("OpenAI connection", "OK", details=f"Response: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print_status("OpenAI connection", "ERROR", details=str(e))
        return False


def check_file_structure() -> Tuple[List[str], List[str]]:
    """
    Check if the expected file structure exists.
    
    Returns:
        Tuple of (existing_files, missing_files)
    """
    expected_files = [
        "agents/shared/schemas.py",
        "agents/shared/utils.py",
        "agents/seo-agent/index.py",
        "run_agent.py",
        "orchestrator.py",
        "requirements.txt",
        ".env.example",
        "supabase_schema.sql"
    ]
    
    existing = []
    missing = []
    
    for file_path in expected_files:
        if os.path.exists(file_path):
            existing.append(file_path)
        else:
            missing.append(file_path)
    
    return existing, missing


def install_missing_packages(packages: List[str]) -> bool:
    """
    Install missing packages using pip.
    
    Args:
        packages: List of packages to install
        
    Returns:
        bool: True if installation was successful, False otherwise
    """
    if not packages:
        return True
    
    print(f"\n{BLUE}Installing missing packages: {', '.join(packages)}{ENDC}")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + packages)
        return True
    except subprocess.CalledProcessError as e:
        print(f"{RED}Failed to install packages: {e}{ENDC}")
        return False


def create_env_file() -> bool:
    """
    Create a .env file from .env.example if it doesn't exist.
    
    Returns:
        bool: True if file was created or already exists, False otherwise
    """
    if os.path.exists(".env"):
        return True
    
    if not os.path.exists(".env.example"):
        print(f"{RED}Cannot create .env file: .env.example not found{ENDC}")
        return False
    
    try:
        with open(".env.example", "r") as example_file:
            example_content = example_file.read()
        
        with open(".env", "w") as env_file:
            env_file.write(example_content)
        
        print(f"{GREEN}Created .env file from .env.example{ENDC}")
        print(f"{YELLOW}Please edit .env file and add your credentials{ENDC}")
        return True
    except Exception as e:
        print(f"{RED}Failed to create .env file: {e}{ENDC}")
        return False


def main():
    """Main function to run all checks."""
    parser = argparse.ArgumentParser(description="Check setup for WordPress Content Generator")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed information")
    parser.add_argument("--fix", "-f", action="store_true", help="Try to fix common issues")
    args = parser.parse_args()
    
    print(f"\n{BOLD}WordPress Content Generator - Setup Check{ENDC}")
    print("=" * 60)
    
    # Check Python version
    python_ok = check_python_version()
    
    # Check packages
    installed_packages, missing_packages = check_packages()
    
    if installed_packages:
        print_status(f"Required packages ({len(installed_packages)})", "OK", 
                    args.verbose, ", ".join(installed_packages))
    
    if missing_packages:
        print_status(f"Missing packages ({len(missing_packages)})", "ERROR", 
                    True, ", ".join(missing_packages))
        
        if args.fix:
            install_missing_packages(missing_packages)
    
    # Check environment variables
    set_vars, missing_vars, optional_vars_set = check_env_vars()
    
    if set_vars:
        print_status(f"Required environment variables ({len(set_vars)})", "OK", 
                    args.verbose, ", ".join(set_vars))
    
    if missing_vars:
        print_status(f"Missing environment variables ({len(missing_vars)})", "ERROR", 
                    True, ", ".join(missing_vars))
        
        if args.fix:
            create_env_file()
    
    if optional_vars_set:
        print_status(f"Optional environment variables ({len(optional_vars_set)})", "OK", 
                    args.verbose, ", ".join(optional_vars_set))
    
    # Check file structure
    existing_files, missing_files = check_file_structure()
    
    if existing_files:
        print_status(f"Required files ({len(existing_files)})", "OK", 
                    args.verbose, ", ".join(existing_files))
    
    if missing_files:
        print_status(f"Missing files ({len(missing_files)})", "WARNING", 
                    True, ", ".join(missing_files))
    
    # Check connections only if required packages are installed
    if "supabase" in installed_packages and "SUPABASE_URL" in set_vars:
        check_supabase_connection()
    
    if "openai" in installed_packages and "OPENAI_API_KEY" in set_vars:
        check_openai_connection()
    
    # Summary
    print("\n" + "=" * 60)
    
    all_ok = (not missing_packages and not missing_vars and python_ok)
    
    if all_ok:
        print(f"\n{GREEN}✅ All checks passed! The system is ready to use.{ENDC}")
        print("\nTo run the orchestrator:")
        print("  python orchestrator.py --mode=continuous")
        print("\nTo run an individual agent:")
        print("  python run_agent.py seo-agent agents/seo-agent/test_input.json")
    else:
        print(f"\n{YELLOW}⚠️ Some checks failed. Please fix the issues above.{ENDC}")
        
        if missing_packages:
            print(f"\nInstall missing packages:")
            print(f"  pip install {' '.join(missing_packages)}")
        
        if missing_vars:
            print(f"\nSet required environment variables in .env file:")
            for var in missing_vars:
                print(f"  {var}={REQUIRED_ENV_VARS[var]}")
    
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
