#!/usr/bin/env python3
"""
Phase 0 Setup Script
Automated setup for Phase 0: Preparation
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path

def run_command(command, description, cwd=None):
    """Run command and handle results"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=cwd)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False

def setup_python_environment():
    """Setup Python virtual environment"""
    print("\n🐍 Setting up Python environment...")

    # Create virtual environment
    if not run_command("python -m venv .venv", "Creating virtual environment"):
        return False

    # Activate and install requirements
    if os.name == 'nt':  # Windows
        activate_cmd = ".venv\\Scripts\\activate"
        pip_cmd = ".venv\\Scripts\\pip"
    else:  # Unix/Mac
        activate_cmd = ".venv/bin/activate"
        pip_cmd = ".venv/bin/pip"

    # Upgrade pip
    if not run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip"):
        return False

    # Install requirements
    if os.path.exists("requirements.txt"):
        if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing requirements"):
            return False
    else:
        print("⚠️  requirements.txt not found, installing basic packages")
        basic_packages = ["pytest", "black", "flake8", "coverage", "mypy"]
        for package in basic_packages:
            if not run_command(f"{pip_cmd} install {package}", f"Installing {package}"):
                return False

    # Install development dependencies
    dev_packages = ["pytest-cov", "pytest-mock", "pre-commit"]
    for package in dev_packages:
        if not run_command(f"{pip_cmd} install {package}", f"Installing {package}"):
            return False

    return True

def setup_git_infrastructure():
    """Setup Git infrastructure"""
    print("\n📦 Setting up Git infrastructure...")

    # Initialize git if not already initialized
    if not Path(".git").exists():
        if not run_command("git init", "Initializing Git repository"):
            return False

    # Set up git branches
    branches = [
        "feature/data-structure-alignment",
        "feature/cr-signature-migration",
        "feature/system-enhancements"
    ]

    for branch in branches:
        # Check if branch exists
        result = subprocess.run(f"git show-ref --verify --quiet refs/heads/{branch}",
                              shell=True, capture_output=True)
        if result.returncode != 0:
            if not run_command(f"git checkout -b {branch}", f"Creating branch {branch}"):
                return False
            # Switch back to main branch
            run_command("git checkout feature/cr-migration-phase-0", "Switching back to main branch")

    return True

def setup_project_structure():
    """Setup and verify project structure"""
    print("\n📁 Verifying project structure...")

    expected_structure = {
        "apps/cli": ["main.py"],
        "packages/data": ["contracts.py", "loader.py"],
        "packages/core_engine": ["odds_math.py", "consensus.py", "detectors.py"],
        "packages/tools": ["registry.py"],
        "packages/agent": ["agent.py", "prompts.py"],
        "packages/reporting": ["briefing.py"],
        "packages/chat": ["chat.py"],
        "packages/schemas": ["briefing_schema.py"],
        "packages/observability": ["trace.py"],
        "tests": ["test_core.py"],
        "data": ["Betstamp AI Odds Agent - sample_odds_data.json"],
        "tools/migration": ["cr_prefix_migrator.py", "data_structure_transformer.py"],
        "tools/validation": ["cr_compliance_validator.py"],
        "tools/backup": ["backup_manager.py"],
        "scripts": ["validate_betstamp_alignment.py"],
        "plans": ["PHASE_PLAN_0_PREPARATION.md", "PHASE_PLAN_1_DATA_STRUCTURE_ALIGNMENT.md"]
    }

    missing_files = []

    for directory, expected_files in expected_structure.items():
        dir_path = Path(directory)
        if not dir_path.exists():
            print(f"❌ Missing directory: {directory}")
            missing_files.append(f"{directory}/")
            continue

        for file in expected_files:
            file_path = dir_path / file
            if not file_path.exists():
                print(f"❌ Missing file: {file_path}")
                missing_files.append(str(file_path))

    if missing_files:
        print(f"\n⚠️  Missing {len(missing_files)} files/directories")
        return False, missing_files
    else:
        print("✅ All expected files and directories present")
        return True, []

def create_development_workflow():
    """Create development workflow documentation"""
    print("\n📝 Creating development workflow documentation...")

    workflow_content = """# Development Workflow

## Branch Structure
- `feature/cr-migration-phase-0`: Current Phase 0 work
- `feature/data-structure-alignment`: Phase 1 work
- `feature/cr-signature-migration`: Phase 2 work
- `feature/system-enhancements`: Phase 3 work

## Development Process
1. Always work on feature branches
2. Create backup before major changes
3. Run validation tools before committing
4. Use pre-commit hooks for code quality

## Migration Tools
- CR Prefix Migration: `tools/migration/cr_prefix_migrator.py`
- Data Structure Transformation: `tools/migration/data_structure_transformer.py`
- Compliance Validation: `tools/validation/cr_compliance_validator.py`
- Backup Management: `tools/backup/backup_manager.py`

## Testing
- Run tests: `python -m pytest tests/ -v`
- Run coverage: `python -m pytest --cov=packages tests/`
- Run validation: `python scripts/validate_betstamp_alignment.py`

## Code Quality
- Format code: `black packages/ apps/ tests/`
- Lint code: `flake8 packages/ apps/ tests/`
- Type checking: `mypy packages/ apps/`
"""

    workflow_file = Path("docs/DEVELOPMENT_WORKFLOW.md")
    workflow_file.parent.mkdir(exist_ok=True)
    workflow_file.write_text(workflow_content)
    print("✅ Development workflow documentation created")
    return True

def setup_pre_commit_hooks():
    """Setup pre-commit hooks"""
    print("\n🪝 Setting up pre-commit hooks...")

    pre_commit_config = """repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
    -   id: check-added-large-files
    -   id: check-merge-conflict

-   repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
    -   id: black
        language_version: python3

-   repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
    -   id: flake8
        args: [--max-line-length=88, --extend-ignore=E203,W503]

-   repo: local
    hooks:
    -   id: cr-compliance-check
        name: CR Compliance Check
        entry: python tools/validation/cr_compliance_validator.py
        language: system
        files: ^packages/.*\\.py$
        pass_filenames: true
"""

    config_file = Path(".pre-commit-config.yaml")
    config_file.write_text(pre_commit_config)

    # Install pre-commit
    if os.name == 'nt':  # Windows
        pip_cmd = ".venv\\Scripts\\pip"
    else:  # Unix/Mac
        pip_cmd = ".venv/bin/pip"

    if not run_command(f"{pip_cmd} install pre-commit", "Installing pre-commit"):
        return False

    if not run_command("pre-commit install", "Installing pre-commit hooks"):
        return False

    print("✅ Pre-commit hooks setup completed")
    return True

def create_phase_0_validation_script():
    """Create Phase 0 validation script"""
    print("\n✅ Creating Phase 0 validation script...")

    validation_script = """#!/usr/bin/env python3
\"\"\"
Phase 0 Validation Script
Validates that Phase 0 setup is complete and ready for Phase 1
\"\"\"

import os
import sys
import subprocess
from pathlib import Path

def validate_python_environment():
    \"\"\"Validate Python environment\"\"\"
    print("Validating Python environment...")

    # Check virtual environment
    if not Path(".venv").exists():
        print("❌ Virtual environment not found")
        return False

    # Check key packages
    required_packages = ["pytest", "black", "flake8", "coverage"]
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} available")
        except ImportError:
            print(f"❌ {package} not available")
            return False

    return True

def validate_migration_tools():
    \"\"\"Validate migration tools\"\"\"
    print("🔍 Validating migration tools...")

    tools = [
        "tools/migration/cr_prefix_migrator.py",
        "tools/migration/data_structure_transformer.py",
        "tools/validation/cr_compliance_validator.py",
        "tools/backup/backup_manager.py"
    ]

    for tool in tools:
        if Path(tool).exists():
            print(f"✅ {tool} exists")
        else:
            print(f"❌ {tool} missing")
            return False

    return True

def validate_project_structure():
    \"\"\"Validate project structure\"\"\"
    print("🔍 Validating project structure...")

    required_dirs = [
        "apps/cli",
        "packages/data",
        "packages/core_engine",
        "packages/tools",
        "packages/agent",
        "packages/reporting",
        "packages/chat",
        "packages/schemas",
        "packages/observability",
        "tests",
        "data",
        "tools/migration",
        "tools/validation",
        "tools/backup",
        "scripts",
        "plans"
    ]

    for directory in required_dirs:
        if Path(directory).exists():
            print(f"✅ {directory} exists")
        else:
            print(f"❌ {directory} missing")
            return False

    return True

def validate_git_setup():
    \"\"\"Validate Git setup\"\"\"
    print("🔍 Validating Git setup...")

    # Check if git repository
    if not Path(".git").exists():
        print("❌ Git repository not initialized")
        return False

    # Check branches
    required_branches = [
        "feature/cr-migration-phase-0",
        "feature/data-structure-alignment",
        "feature/cr-signature-migration",
        "feature/system-enhancements"
    ]

    for branch in required_branches:
        result = subprocess.run(f"git show-ref --verify --quiet refs/heads/{branch}",
                              shell=True, capture_output=True)
        if result.returncode == 0:
            print(f"✅ Branch {branch} exists")
        else:
            print(f"❌ Branch {branch} missing")
            return False

    return True

def validate_betstamp_alignment():
    \"\"\"Validate Betstamp alignment\"\"\"
    print("🔍 Validating Betstamp alignment...")

    # Run Betstamp validation script
    try:
        result = subprocess.run("python scripts/validate_betstamp_alignment.py",
                              shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Betstamp alignment validation passed")
            return True
        else:
            print("❌ Betstamp alignment validation failed")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Betstamp validation error: {e}")
        return False

def main():
    \"\"\"Main validation function\"\"\"
    print("🚀 Phase 0 Validation")
    print("=" * 50)

    validations = [
        ("Python Environment", validate_python_environment),
        ("Migration Tools", validate_migration_tools),
        ("Project Structure", validate_project_structure),
        ("Git Setup", validate_git_setup),
        ("Betstamp Alignment", validate_betstamp_alignment)
    ]

    results = []

    for name, validator in validations:
        try:
            result = validator()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} validation failed with exception: {e}")
            results.append((name, False))

    # Summary
    print("\\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name}: {status}")

    print(f"\\nOverall: {passed}/{total} validations passed")

    if passed == total:
        print("🎉 Phase 0 is complete and ready for Phase 1!")
        return 0
    else:
        print("❌ Phase 0 has issues that need to be resolved")
        return 1

if __name__ == "__main__":
    sys.exit(main())
"""

    script_file = Path("scripts/validate_phase_0.py")
    script_file.write_text(validation_script)
    print("✅ Phase 0 validation script created")
    return True

def main():
    """Main Phase 0 setup function"""
    print("🚀 Phase 0: Preparation Setup")
    print("=" * 50)
    print(f"Started: {datetime.now().isoformat()}")
    print()

    setup_steps = [
        ("Python Environment Setup", setup_python_environment),
        ("Git Infrastructure Setup", setup_git_infrastructure),
        ("Project Structure Verification", lambda: setup_project_structure()[0]),
        ("Development Workflow Creation", create_development_workflow),
        ("Pre-commit Hooks Setup", setup_pre_commit_hooks),
        ("Phase 0 Validation Script", create_phase_0_validation_script)
    ]

    results = []

    for step_name, step_func in setup_steps:
        print(f"\n📋 {step_name}")
        print("-" * len(step_name))

        try:
            result = step_func()
            results.append((step_name, result))
        except Exception as e:
            print(f"❌ {step_name} failed with exception: {e}")
            results.append((step_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("📊 SETUP SUMMARY")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for step_name, result in results:
        status = "✅ COMPLETED" if result else "❌ FAILED"
        print(f"{step_name}: {status}")

    print(f"\nOverall: {passed}/{total} setup steps completed")

    if passed == total:
        print("\n🎉 Phase 0 setup is complete!")
        print("📝 Next steps:")
        print("   1. Run 'python scripts/validate_phase_0.py' to validate setup")
        print("   2. Review migration tools in tools/ directory")
        print("   3. Begin Phase 1: Data Structure Alignment")
        return 0
    else:
        print(f"\n❌ {total - passed} setup steps failed. Please resolve issues before proceeding.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
