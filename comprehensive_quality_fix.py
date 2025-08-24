#!/usr/bin/env python3


    """Remove duplicate imports from a Python file.
                    print(f"  Removed duplicate import: {line.strip()}")
            else:
                fixed_lines.append(line)
        
        # Write back the fixed content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(fixed_lines))
        
        return True
    except Exception as e:
        print(f"  Error fixing {file_path}: {e}")
        return False

def fix_docstring_format(file_path):
    """Fix malformed docstrings in Python files.
        content = re.sub(r'^"""\s*[^"]*$', '', content, flags=re.MULTILINE)
        
        # Fix any unterminated docstrings
        content = re.sub(r'"""\s*[^"]*$', '', content, flags=re.MULTILINE)
        
        # Write back the fixed content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    except Exception as e:
        print(f"  Error fixing docstring in {file_path}: {e}")
        return False

def fix_syntax_errors(file_path):
    """Fix common syntax errors in Python files.
        content = re.sub(r'^[^\w#\s"\'`]+', '', content)
        
        # Fix any malformed string literals
        content = re.sub(r'(["\'])\s*\n\s*(["\'])', r'\1\2', content)
        
        # Write back the fixed content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    except Exception as e:
        print(f"  Error fixing syntax in {file_path}: {e}")
        return False

def check_file_quality(file_path):
    """Check and fix quality issues in a single file.
    print(f"Checking: {file_path}")
    
    issues_fixed = 0
    
    # Check for duplicate imports
    if fix_duplicate_imports(file_path):
        issues_fixed += 1
    
    # Check for docstring issues
    if fix_docstring_format(file_path):
        issues_fixed += 1
    
    # Check for syntax issues
    if fix_syntax_errors(file_path):
        issues_fixed += 1
    
    if issues_fixed > 0:
        print(f"  Fixed {issues_fixed} issues")
    
    return issues_fixed

def main():
    """Main function to fix quality issues across the codebase.
    print("🔧 Starting Comprehensive Quality Fix...")
    
    # Find all Python files
    python_files = []
    
    # Search in main directories
    search_dirs = [
        'ai_service',
        'frontend',
        'api_gateway',
        'gateway',
        'infrastructure',
        'monitoring',
        'datastore',
        'testing'
    ]
    
    for search_dir in search_dirs:
        if os.path.exists(search_dir):
            pattern = os.path.join(search_dir, '**', '*.py')
            python_files.extend(glob.glob(pattern, recursive=True))
    
    # Also include root Python files
    root_py_files = glob.glob('*.py')
    python_files.extend(root_py_files)
    
    print(f"Found {len(python_files)} Python files to check")
    
    total_issues_fixed = 0
    files_with_issues = 0
    
    for file_path in python_files:
        if os.path.isfile(file_path):
            issues_fixed = check_file_quality(file_path)
            if issues_fixed > 0:
                files_with_issues += 1
                total_issues_fixed += issues_fixed
    
    print(f"\n✅ Quality fix completed!")
    print(f"📊 Files with issues: {files_with_issues}")
    print(f"🔧 Total issues fixed: {total_issues_fixed}")
    
    # Now run a final quality check
    print("\n🔍 Running final quality check...")
    try:
        import subprocess
        result = subprocess.run([
            'python', '-m', 'flake8', '.', '--count', '--select=E9', '--show-source'
        ], capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            print("✅ No critical syntax errors found!")
        else:
            print(f"⚠️  {result.stdout.count('E999')} syntax errors remaining")
            print("Consider manual review of remaining issues")
    
    except Exception as e:
        print(f"⚠️  Could not run final quality check: {e}")

if __name__ == "__main__":
    main()
