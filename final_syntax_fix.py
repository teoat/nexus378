#!/usr/bin/env python3


    """Completely fix all syntax issues in a file.
                line.strip().startswith('
                (line.strip().endswith('
                 (i + 1 < len(lines) and '
                if line.strip().endswith('
                        if '
        content = re.sub(r'^"""[^"]*$', '', content, flags=re.MULTILINE)
        
        # Fix 3: Clean up multiple empty lines
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        # Fix 4: Remove any lines that are just quotes
        content = re.sub(r'^\s*
            content = '#!/usr/bin/env python3\n"""Module.
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    """Main function to fix all remaining syntax issues.
    print("🔧 Performing final comprehensive syntax fix...")
    
    # Get all Python files
    project_root = Path("nexus")
    python_files = list(project_root.rglob("*.py"))
    
    print(f"📁 Found {len(python_files)} Python files")
    
    fixed_count = 0
    for py_file in python_files:
        print(f"   Fixing: {py_file}")
        if fix_file_completely(py_file):
            fixed_count += 1
            print(f"     ✅ Fixed: {py_file}")
        else:
            print(f"     ⚠️  No changes needed: {py_file}")
    
    print(f"\n📊 Fixed {fixed_count} files")
    print("✅ Final syntax fixes completed. Now run Black formatting.")

if __name__ == "__main__":
    main()
