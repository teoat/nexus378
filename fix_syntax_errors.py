#!/usr/bin/env python3


    """Find all Python files with syntax errors.
    forensic_dir = Path("nexus")
    
    for py_file in forensic_dir.rglob("*.py"):
        try:
            # Try to compile the file
            result = subprocess.run(
                ["python", "-m", "py_compile", str(py_file)],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                python_files.append(str(py_file))
        except Exception as e:
            print(f"Error checking {py_file}: {e}")
    
    return python_files

def fix_common_syntax_errors(file_path):
    """Fix common syntax errors in a Python file.
            if '"""' in line and line.count('
                    if '
                        line = line + '
                    line = line + '
            if line.count("'") % 2 == 1 and not line.strip().startswith('#'):
                # Check if it's a valid case (like in a string)
                if not re.search(r"'.*'", line):
                    # Add closing quote
                    line = line + "'"
            
            # Fix unterminated double quotes
            if line.count('"') % 2 == 1 and not line.strip().startswith('#'):
                # Check if it's a valid case
                if not re.search(r'".*"', line):
                    # Add closing quote
                    line = line + '"'
            
            fixed_lines.append(line)
        
        content = '\n'.join(fixed_lines)
        
        # Fix 2: Missing colons after if/for/while/def/class
        content = re.sub(r'(\s+)(if|for|while|def|class|elif|else|try|except|finally|with)\s+([^:]+?)(?=\s*$)', r'\1\2 \3:', content)
        
        # Fix 3: Generator expression parentheses
        content = re.sub(r'(\w+)\s+for\s+(\w+)\s+in\s+(\w+)', r'(\1 for \2 in \3)', content)
        
        # Fix 4: Missing parentheses in function calls
        content = re.sub(r'(\w+)\s*=\s*(\w+)\s*for\s*(\w+)\s*in\s*(\w+)', r'(\1 = \2 for \3 in \4)', content)
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def run_black_formatting():
    """Run Black formatting on all Python files.
            ["black", "--line-length=88", "nexus"],
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error running Black: {e}")
        return False

def main():
    """Main function to fix syntax errors and run formatting.
    print("🔧 Starting Syntax Error Fix Process...")
    
    # Step 1: Find files with syntax errors
    print("\n📋 Finding Python files with syntax errors...")
    problematic_files = find_python_files_with_syntax_errors()
    
    if not problematic_files:
        print("✅ No syntax errors found!")
        return
    
    print(f"❌ Found {len(problematic_files)} files with syntax errors:")
    for file_path in problematic_files[:10]:  # Show first 10
        print(f"   - {file_path}")
    if len(problematic_files) > 10:
        print(f"   ... and {len(problematic_files) - 10} more")
    
    # Step 2: Fix syntax errors
    print(f"\n🔧 Fixing syntax errors in {len(problematic_files)} files...")
    fixed_count = 0
    
    for file_path in problematic_files:
        print(f"   Fixing: {file_path}")
        if fix_common_syntax_errors(file_path):
            fixed_count += 1
            print(f"     ✅ Fixed: {file_path}")
        else:
            print(f"     ⚠️  No changes needed: {file_path}")
    
    print(f"\n📊 Fixed {fixed_count} out of {len(problematic_files)} files")
    
    # Step 3: Run Black formatting
    print("\n📝 Running Black formatting...")
    if run_black_formatting():
        print("✅ Black formatting completed successfully!")
    else:
        print("❌ Black formatting failed. Some syntax errors may remain.")
    
    # Step 4: Verify fixes
    print("\n🔍 Verifying fixes...")
    remaining_errors = find_python_files_with_syntax_errors()
    
    if not remaining_errors:
        print("🎉 All syntax errors have been fixed!")
    else:
        print(f"⚠️  {len(remaining_errors)} files still have syntax errors:")
        for file_path in remaining_errors[:5]:
            print(f"   - {file_path}")
        if len(remaining_errors) > 5:
            print(f"   ... and {len(remaining_errors) - 5} more")
    
    print(f"\n📋 Summary:")
    print(f"   - Files with initial errors: {len(problematic_files)}")
    print(f"   - Files fixed: {fixed_count}")
    print(f"   - Remaining errors: {len(remaining_errors)}")

if __name__ == "__main__":
    main()
