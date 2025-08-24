#!/usr/bin/env python3


    """Manages code quality tools and provides comprehensive analysis.
    def __init__(self, workspace_path="nexus"):
        self.workspace_path = Path(workspace_path)
        self.python_files = []
        self.issues_found = []
        
    def discover_python_files(self):
        """Find all Python files in the workspace.
        print("🔍 Discovering Python files...")
        
        for py_file in self.workspace_path.rglob("*.py"):
            if not any(part.startswith('.') for part in py_file.parts):
                self.python_files.append(py_file)
        
        print(f"✅ Found {len(self.python_files)} Python files")
        return self.python_files
    
    def run_black_formatting(self):
        """Run Black code formatter.
        print("\n🎨 Running Black code formatter...")
        
        try:
            result = subprocess.run(
                ["black", "--check", "--diff", str(self.workspace_path)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ All files are properly formatted with Black")
                return True
            else:
                print("⚠️  Some files need formatting. Running Black to fix...")
                
                # Run Black to format files
                format_result = subprocess.run(
                    ["black", str(self.workspace_path)],
                    capture_output=True,
                    text=True
                )
                
                if format_result.returncode == 0:
                    print("✅ Black formatting completed successfully")
                    return True
                else:
                    print(f"❌ Black formatting failed: {format_result.stderr}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error running Black: {e}")
            return False
    
    def run_isort(self):
        """Run isort to organize imports.
        print("\n📦 Running isort to organize imports...")
        
        try:
            result = subprocess.run(
                ["isort", "--check-only", "--diff", str(self.workspace_path)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ All imports are properly organized")
                return True
            else:
                print("⚠️  Some imports need organization. Running isort to fix...")
                
                # Run isort to organize imports
                sort_result = subprocess.run(
                    ["isort", str(self.workspace_path)],
                    capture_output=True,
                    text=True
                )
                
                if sort_result.returncode == 0:
                    print("✅ Import organization completed successfully")
                    return True
                else:
                    print(f"❌ Import organization failed: {sort_result.stderr}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error running isort: {e}")
            return False
    
    def run_flake8(self):
        """Run flake8 for style and error checking.
        print("\n🔍 Running flake8 for style and error checking...")
        
        try:
            result = subprocess.run(
                ["flake8", str(self.workspace_path)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ No flake8 issues found")
                return True
            else:
                print("⚠️  Flake8 found some issues:")
                print(result.stdout)
                return False
                
        except Exception as e:
            print(f"❌ Error running flake8: {e}")
            return False
    
    def run_pylint(self):
        """Run pylint for comprehensive code analysis.
        print("\n🔬 Running pylint for comprehensive code analysis...")
        
        try:
            # Run pylint on a few key files to avoid overwhelming output
            key_files = [
                "ai_service/agents/pattern_detector.py",
                "ai_service/taskmaster/core/collective_worker_processor.py",
                "ai_service/auth/mfa/mfa_manager.py"
            ]
            
            total_score = 0
            files_checked = 0
            
            for file_path in key_files:
                full_path = self.workspace_path / file_path
                if full_path.exists():
                    try:
                        result = subprocess.run(
                            ["pylint", "--output-format=text", str(full_path)],
                            capture_output=True,
                            text=True
                        )
                        
                        if result.returncode == 0:
                            print(f"✅ {file_path}: No issues")
                            total_score += 10
                        else:
                            print(f"⚠️  {file_path}: Some issues found")
                            # Extract score if available
                            if "Your code has been rated at" in result.stdout:
                                score_line = [line for line in result.stdout.split('\n') if "Your code has been rated at" in line]
                                if score_line:
                                    score_text = score_line[0]
                                    try:
                                        score = float(score_text.split()[-1].split('/')[0])
                                        total_score += score
                                    except:
                                        total_score += 5
                                else:
                                    total_score += 5
                            else:
                                total_score += 5
                        
                        files_checked += 1
                        
                    except Exception as e:
                        print(f"❌ Error checking {file_path}: {e}")
            
            if files_checked > 0:
                avg_score = total_score / files_checked
                print(f"📊 Average pylint score: {avg_score:.1f}/10")
                
                if avg_score >= 8.0:
                    print("✅ Excellent code quality!")
                elif avg_score >= 6.0:
                    print("⚠️  Good code quality with room for improvement")
                else:
                    print("❌ Code quality needs attention")
                
                return avg_score >= 6.0
            else:
                print("❌ No files could be checked with pylint")
                return False
                
        except Exception as e:
            print(f"❌ Error running pylint: {e}")
            return False
    
    def run_syntax_check(self):
        """Run basic Python syntax check on all files.
        print("\n🐍 Running Python syntax check...")
        
        syntax_errors = []
        for py_file in self.python_files:
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "py_compile", str(py_file)],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    syntax_errors.append(str(py_file))
                    
            except Exception as e:
                syntax_errors.append(f"{py_file}: {e}")
        
        if not syntax_errors:
            print("✅ All Python files compile successfully")
            return True
        else:
            print(f"❌ Found {len(syntax_errors)} files with syntax errors:")
            for error in syntax_errors[:5]:  # Show first 5 errors
                print(f"   - {error}")
            if len(syntax_errors) > 5:
                print(f"   ... and {len(syntax_errors) - 5} more")
            return False
    
    def generate_quality_report(self):
        """Generate a comprehensive code quality report.
        print("\n📊 Generating code quality report...")
        
        report = f
        print("✅ Code quality report generated: CODE_QUALITY_REPORT.md")
    
    def run_full_quality_check(self):
        """Run all quality checks and generate report.
        print("🚀 Starting comprehensive code quality check...")
        print("=" * 60)
        
        # Discover files
        self.discover_python_files()
        
        # Run all quality checks
        self._black_passed = self.run_black_formatting()
        self._isort_passed = self.run_isort()
        self._flake8_passed = self.run_flake8()
        self._pylint_passed = self.run_pylint()
        self._syntax_passed = self.run_syntax_check()
        
        # Generate report
        self.generate_quality_report()
        
        # Summary
        print("\n" + "=" * 60)
        print("🎉 Code Quality Check Complete!")
        
        checks = [
            ("Black Formatting", self._black_passed),
            ("Import Organization", self._isort_passed),
            ("Style & Errors", self._flake8_passed),
            ("Code Analysis", self._pylint_passed),
            ("Syntax Validation", self._syntax_passed)
        ]
        
        passed = sum(1 for _, status in checks if status)
        total = len(checks)
        
        print(f"📊 Results: {passed}/{total} checks passed")
        
        for name, status in checks:
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {name}")
        
        print(f"\n📖 Check CODE_QUALITY_REPORT.md for detailed information")

def main():
    """Main function to run code quality manager.
if __name__ == "__main__":
    main()
