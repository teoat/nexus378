#!/usr/bin/env python3


    """Run a command and return success status.
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False

def fix_python_syntax_errors():
    """Fix Python syntax errors using autopep8.
    print("\n🐍 Fixing Python syntax errors...")
    
    # Find all Python files
    python_files = []
    for root, dirs, files in os.walk('nexus'):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    print(f"Found {len(python_files)} Python files")
    
    fixed_count = 0
    for filepath in python_files:
        try:
            # Try to compile the file
            result = subprocess.run(
                [sys.executable, '-m', 'py_compile', filepath],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"Fixing syntax errors in: {filepath}")
                
                # Use autopep8 to fix the file
                fix_result = subprocess.run(
                    ['autopep8', '--in-place', '--aggressive', '--aggressive', filepath],
                    capture_output=True,
                    text=True
                )
                
                if fix_result.returncode == 0:
                    # Test if it compiles now
                    test_result = subprocess.run(
                        [sys.executable, '-m', 'py_compile', filepath],
                        capture_output=True,
                        text=True
                    )
                    
                    if test_result.returncode == 0:
                        print(f"✅ Fixed: {filepath}")
                        fixed_count += 1
                    else:
                        print(f"⚠️  Still has issues: {filepath}")
                        print(test_result.stderr)
                else:
                    print(f"❌ Failed to fix: {filepath}")
                    print(fix_result.stderr)
        except Exception as e:
            print(f"❌ Error processing {filepath}: {e}")
    
    print(f"Fixed syntax errors in {fixed_count} files")
    return fixed_count

def fix_import_errors():
    """Fix import errors by checking dependencies.
    print("\n📦 Checking for import errors...")
    
    # Check if required packages are installed
    required_packages = [
        'pandas', 'numpy', 'scikit-learn', 'matplotlib', 'seaborn',
        'requests', 'aiohttp', 'asyncio', 'logging', 'datetime'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing packages: {', '.join(missing_packages)}")
        print("Consider installing them with: pip install " + " ".join(missing_packages))
    else:
        print("✅ All required packages are available")
    
    return len(missing_packages)

def fix_file_permissions():
    """Fix file permission issues.
    print("\n🔐 Fixing file permissions...")
    
    try:
        # Make Python files executable
        for root, dirs, files in os.walk('nexus'):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    os.chmod(filepath, 0o644)
        
        print("✅ Fixed file permissions")
        return True
    except Exception as e:
        print(f"❌ Error fixing permissions: {e}")
        return False

def run_tests():
    """Run basic tests to verify fixes.
    print("\n🧪 Running basic tests...")
    
    test_files = [
        'nexus/ai_service/agents/pattern_detector.py',
        'nexus/ai_service/taskmaster/core/collective_worker_processor.py'
    ]
    
    passed_tests = 0
    for test_file in test_files:
        if os.path.exists(test_file):
            try:
                result = subprocess.run(
                    [sys.executable, '-m', 'py_compile', test_file],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    print(f"✅ {test_file} compiles successfully")
                    passed_tests += 1
                else:
                    print(f"❌ {test_file} still has issues")
                    print(result.stderr)
            except Exception as e:
                print(f"❌ Error testing {test_file}: {e}")
    
    print(f"Tests passed: {passed_tests}/{len(test_files)}")
    return passed_tests

def generate_summary_report():
    """Generate a summary report of all fixes.
    print("\n📊 Generating summary report...")
    
    report = 
    print("✅ Summary report generated: WORKSPACE_FIX_REPORT.md")

def main():
    """Main function to run all fixes.
    print("🚀 Starting Comprehensive Workspace Error Fixing...")
    print("=" * 60)
    
    # Run all fixes
    syntax_fixes = fix_python_syntax_errors()
    import_issues = fix_import_errors()
    permission_fixes = fix_file_permissions()
    test_results = run_tests()
    
    # Generate summary
    generate_summary_report()
    
    print("\n" + "=" * 60)
    print("🎉 Workspace Error Fixing Complete!")
    print(f"📊 Summary:")
    print(f"   - Syntax errors fixed: {syntax_fixes}")
    print(f"   - Import issues found: {import_issues}")
    print(f"   - Permission fixes: {'Yes' if permission_fixes else 'No'}")
    print(f"   - Tests passed: {test_results}")
    print("\n📖 Check WORKSPACE_FIX_REPORT.md for detailed information")

if __name__ == "__main__":
    main()
