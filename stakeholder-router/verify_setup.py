#!/usr/bin/env python3
"""Verify that the Stakeholder Router is properly set up."""

import os
import sys
from pathlib import Path


def check_file(filepath, description):
    """Check if a file exists."""
    path = Path(filepath)
    exists = path.exists()
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {filepath}")
    return exists


def check_directory(dirpath, description):
    """Check if a directory exists."""
    path = Path(dirpath)
    exists = path.is_dir()
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {dirpath}")
    return exists


def check_env_var(var_name, description):
    """Check if environment variable is set."""
    value = os.getenv(var_name)
    is_set = value is not None and len(value) > 0
    status = "✅" if is_set else "⚠️ "
    print(f"{status} {description}: {var_name}")
    return is_set


def main():
    """Run verification checks."""
    print("🎯 Stakeholder Router - Setup Verification")
    print("=" * 50)
    print()

    all_passed = True

    # Check directories
    print("📁 Checking Directory Structure...")
    checks = [
        check_directory("src", "Source directory"),
        check_directory("src/config", "Config directory"),
        check_directory("src/router", "Router directory"),
        check_directory("src/experts", "Experts directory"),
        check_directory("src/utils", "Utils directory"),
        check_directory("tests", "Tests directory"),
        check_directory("examples", "Examples directory"),
    ]
    all_passed = all_passed and all(checks)
    print()

    # Check core files
    print("📄 Checking Core Files...")
    checks = [
        check_file("app.py", "Streamlit app"),
        check_file("requirements.txt", "Requirements file"),
        check_file(".env.example", "Environment template"),
        check_file("setup.sh", "Setup script"),
        check_file("run.sh", "Run script"),
    ]
    all_passed = all_passed and all(checks)
    print()

    # Check source files
    print("🐍 Checking Source Files...")
    checks = [
        check_file("src/config/settings.py", "Settings"),
        check_file("src/router/classifier.py", "Classifier"),
        check_file("src/router/orchestrator.py", "Orchestrator"),
        check_file("src/router/guardrails.py", "Guardrails"),
        check_file("src/experts/base_expert.py", "Base Expert"),
        check_file("src/experts/pricing_expert.py", "Pricing Expert"),
        check_file("src/experts/ux_expert.py", "UX Expert"),
        check_file("src/utils/llm_client.py", "LLM Client"),
        check_file("src/utils/prompts.py", "Prompts"),
    ]
    all_passed = all_passed and all(checks)
    print()

    # Check test files
    print("🧪 Checking Test Files...")
    checks = [
        check_file("tests/test_classifier.py", "Classifier tests"),
        check_file("tests/test_guardrails.py", "Guardrails tests"),
        check_file("tests/test_routing.py", "Routing tests"),
    ]
    all_passed = all_passed and all(checks)
    print()

    # Check examples
    print("📚 Checking Example Files...")
    checks = [
        check_file("examples/test_queries.json", "Test queries"),
        check_file("examples/sabotage_scenarios.json", "Sabotage scenarios"),
    ]
    all_passed = all_passed and all(checks)
    print()

    # Check documentation
    print("📖 Checking Documentation...")
    checks = [
        check_file("README.md", "README"),
        check_file("QUICKSTART.md", "Quick Start Guide"),
        check_file("PROJECT_SUMMARY.md", "Project Summary"),
        check_file("LICENSE", "License"),
    ]
    all_passed = all_passed and all(checks)
    print()

    # Check environment
    print("🔐 Checking Environment...")
    has_dotenv = check_file(".env", "Environment file")
    if has_dotenv:
        # Try to load .env
        try:
            from dotenv import load_dotenv
            load_dotenv()
            check_env_var("ANTHROPIC_API_KEY", "Anthropic API Key")
        except ImportError:
            print("⚠️  python-dotenv not installed (run pip install -r requirements.txt)")
    else:
        print("⚠️  .env file not found (copy from .env.example)")
    print()

    # Try importing modules
    print("🔍 Checking Python Imports...")
    try:
        sys.path.insert(0, str(Path.cwd()))
        from src.config.settings import anthropic_settings, router_settings
        print("✅ Config imports work")
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        all_passed = False

    try:
        from src.router.classifier import RequestClassifier
        print("✅ Classifier imports work")
    except Exception as e:
        print(f"❌ Classifier import failed: {e}")
        all_passed = False

    try:
        from src.router.orchestrator import RoutingOrchestrator
        print("✅ Orchestrator imports work")
    except Exception as e:
        print(f"❌ Orchestrator import failed: {e}")
        all_passed = False

    try:
        from src.experts.pricing_expert import PricingExpert
        from src.experts.ux_expert import UXExpert
        print("✅ Experts import work")
    except Exception as e:
        print(f"❌ Experts import failed: {e}")
        all_passed = False

    print()

    # Summary
    print("=" * 50)
    if all_passed:
        print("✅ All checks passed!")
        print()
        print("Next steps:")
        print("1. Ensure .env file has ANTHROPIC_API_KEY set")
        print("2. Run: streamlit run app.py")
        print("3. Or use: ./run.sh")
        return 0
    else:
        print("❌ Some checks failed")
        print()
        print("Please review the errors above and:")
        print("1. Run ./setup.sh to set up the environment")
        print("2. Ensure all dependencies are installed")
        print("3. Check that you're in the correct directory")
        return 1


if __name__ == "__main__":
    sys.exit(main())
