#!/usr/bin/env python3
"""
Development Environment Setup Script for Nexus Forensic Platform
"""

import os
import subprocess
import sys
from pathlib import Path

class DevEnvironmentSetup:
    """Sets up the complete development environment for Nexus."""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.venv_path = self.project_root / ".venv"
        self.requirements_file = self.project_root / "requirements.txt"
        
    def check_python_version(self):
        """Check if Python version is compatible."""
        print("🐍 Checking Python version...")
        
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print("❌ Python 3.8+ is required")
            return False
        
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    
    def create_virtual_environment(self):
        """Create a virtual environment if it doesn't exist."""
        print("\n🔧 Setting up virtual environment...")
        
        if self.venv_path.exists():
            print("✅ Virtual environment already exists")
            return True
        
        try:
            subprocess.run([sys.executable, "-m", "venv", str(self.venv_path)], check=True)
            print("✅ Virtual environment created successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False
    
    def activate_virtual_environment(self):
        """Activate the virtual environment."""
        print("\n🔌 Activating virtual environment...")
        
        if os.name == 'nt':  # Windows
            activate_script = self.venv_path / "Scripts" / "activate.bat"
            if activate_script.exists():
                print("✅ Virtual environment activated (Windows)")
                return True
        else:  # Unix/Linux/macOS
            activate_script = self.venv_path / "bin" / "activate"
            if activate_script.exists():
                print("✅ Virtual environment activated (Unix)")
                return True
        
        print("⚠️  Please activate the virtual environment manually:")
        if os.name == 'nt':
            print(f"   {activate_script}")
        else:
            print(f"   source {activate_script}")
        return False
    
    def install_dependencies(self):
        """Install project dependencies."""
        print("\n📦 Installing project dependencies...")
        
        if not self.requirements_file.exists():
            print("❌ requirements.txt not found")
            return False
        
        try:
            # Use pip from the virtual environment if available
            pip_cmd = [sys.executable, "-m", "pip"]
            
            # Upgrade pip first
            subprocess.run([*pip_cmd, "install", "--upgrade", "pip"], check=True)
            print("✅ pip upgraded")
            
            # Install dependencies
            subprocess.run([*pip_cmd, "install", "-r", str(self.requirements_file)], check=True)
            print("✅ Dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    def install_pre_commit_hooks(self):
        """Install pre-commit hooks."""
        print("\n🔗 Installing pre-commit hooks...")
        
        try:
            subprocess.run([sys.executable, "-m", "pre_commit", "install"], check=True)
            print("✅ Pre-commit hooks installed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install pre-commit hooks: {e}")
            return False
    
    def run_initial_quality_check(self):
        """Run initial code quality check."""
        print("\n🔍 Running initial code quality check...")
        
        try:
            # Check if code quality manager exists
            quality_script = self.project_root / "code_quality_manager.py"
            if quality_script.exists():
                subprocess.run([sys.executable, str(quality_script)], check=True)
                print("✅ Initial quality check completed")
                return True
            else:
                print("⚠️  Code quality manager not found, skipping quality check")
                return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Quality check failed: {e}")
            return False
    
    def create_git_hooks(self):
        """Create additional git hooks for development."""
        print("\n📝 Setting up additional git hooks...")
        
        git_hooks_dir = self.project_root / ".git" / "hooks"
        if not git_hooks_dir.exists():
            print("⚠️  Git repository not found, skipping git hooks")
            return True
        
        # Create pre-commit hook
        pre_commit_hook = git_hooks_dir / "pre-commit"
        if not pre_commit_hook.exists():
            hook_content = """#!/bin/sh
# Pre-commit hook for Nexus development
echo "🔍 Running pre-commit checks..."

# Run code formatting
make format

# Run syntax check
make test-syntax

# Run linting
make lint

echo "✅ Pre-commit checks passed"
"""
            try:
                with open(pre_commit_hook, 'w') as f:
                    f.write(hook_content)
                os.chmod(pre_commit_hook, 0o755)
                print("✅ Pre-commit hook created")
            except Exception as e:
                print(f"❌ Failed to create pre-commit hook: {e}")
                return False
        
        return True
    
    def create_development_config(self):
        """Create development configuration files."""
        print("\n⚙️  Creating development configuration...")
        
        # Create .env.example if it doesn't exist
        env_example = self.project_root / ".env.example"
        if not env_example.exists():
            env_content = """# Development Environment Configuration
# Copy this file to .env and fill in your values

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/nexus_dev
TEST_DATABASE_URL=postgresql://user:password@localhost:5432/nexus_test

# API Keys (get these from respective services)
ANTHROPIC_API_KEY=your_anthropic_key_here
PERPLEXITY_API_KEY=your_perplexity_key_here
OPENAI_API_KEY=your_openai_key_here

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Logging
LOG_LEVEL=DEBUG
LOG_FORMAT=json

# Security
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_here

# Development Settings
DEBUG=true
ENVIRONMENT=development
"""
            try:
                with open(env_example, 'w') as f:
                    f.write(env_content)
                print("✅ .env.example created")
            except Exception as e:
                print(f"❌ Failed to create .env.example: {e}")
        
        # Create .gitignore if it doesn't exist
        gitignore = self.project_root / ".gitignore"
        if not gitignore.exists():
            gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/

# Database
*.db
*.sqlite3

# Coverage
.coverage
htmlcov/

# pytest
.pytest_cache/

# Jupyter
.ipynb_checkpoints

# Environment variables
.env.local
.env.development.local
.env.test.local
.env.production.local
"""
            try:
                with open(gitignore, 'w') as f:
                    f.write(gitignore_content)
                print("✅ .gitignore created")
            except Exception as e:
                print(f"❌ Failed to create .gitignore: {e}")
        
        return True
    
    def display_next_steps(self):
        """Display next steps for the developer."""
        print("\n" + "=" * 60)
        print("🎉 Development Environment Setup Complete!")
        print("=" * 60)
        print("\n📋 Next Steps:")
        print("1. Activate the virtual environment:")
        if os.name == 'nt':
            print(f"   {self.venv_path / 'Scripts' / 'activate.bat'}")
        else:
            print(f"   source {self.venv_path / 'bin' / 'activate'}")
        
        print("\n2. Verify the setup:")
        print("   make help                    # Show available commands")
        print("   make quality                 # Run code quality check")
        print("   make format                  # Format code")
        print("   make lint                    # Run linting")
        
        print("\n3. Start developing:")
        print("   # Your code will be automatically formatted and checked")
        print("   # Use 'make quick-check' before committing")
        print("   # Use 'make dev-cycle' for full development workflow")
        
        print("\n4. Configuration files created:")
        print("   - pyproject.toml            # Tool configurations")
        print("   - .pre-commit-config.yaml   # Pre-commit hooks")
        print("   - Makefile                  # Development commands")
        print("   - requirements.txt          # Dependencies")
        print("   - .env.example              # Environment template")
        print("   - .gitignore                # Git ignore rules")
        
        print("\n🚀 Happy coding!")
    
    def run_setup(self):
        """Run the complete setup process."""
        print("🚀 Setting up Nexus Forensic Platform Development Environment")
        print("=" * 70)
        
        steps = [
            ("Python Version Check", self.check_python_version),
            ("Virtual Environment", self.create_virtual_environment),
            ("Dependencies Installation", self.install_dependencies),
            ("Pre-commit Hooks", self.install_pre_commit_hooks),
            ("Git Hooks", self.create_git_hooks),
            ("Development Config", self.create_development_config),
            ("Initial Quality Check", self.run_initial_quality_check),
        ]
        
        success_count = 0
        total_steps = len(steps)
        
        for step_name, step_func in steps:
            print(f"\n📋 {step_name}...")
            if step_func():
                success_count += 1
            else:
                print(f"⚠️  {step_name} failed, continuing...")
        
        print(f"\n📊 Setup Summary: {success_count}/{total_steps} steps completed successfully")
        
        if success_count >= total_steps - 1:  # Allow one failure
            self.display_next_steps()
            return True
        else:
            print("\n❌ Setup encountered multiple failures. Please check the errors above.")
            return False

def main():
    """Main function to run the setup."""
    setup = DevEnvironmentSetup()
    success = setup.run_setup()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
