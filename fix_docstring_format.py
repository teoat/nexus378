#!/usr/bin/env python3


    """Fix docstring formatting issues in a file.
        # Look for lines like: """Module description
                line.strip().startswith('
                line.strip().endswith('
                fixed_lines.append('
                fixed_lines.append('
                line.strip().startswith('
                not line.strip().endswith('
                fixed_lines.append('
                    if '
                        doc_content = lines[i].split('
                        fixed_lines.append('
        content = re.sub(r'"""\n([^"]+)\n"""', r'"""\n\1\n
        content = re.sub(r'"""\s*\n\s*
            content = '#!/usr/bin/env python3\n"""Module.
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    """Main function to fix docstring formatting issues.
    print("🔧 Fixing docstring formatting issues...")
    
    # Get all Python files
    project_root = Path("nexus")
    python_files = list(project_root.rglob("*.py"))
    
    print(f"📁 Found {len(python_files)} Python files")
    
    fixed_count = 0
    for py_file in python_files:
        print(f"   Fixing: {py_file}")
        if fix_docstring_format(py_file):
            fixed_count += 1
            print(f"     ✅ Fixed: {py_file}")
        else:
            print(f"     ⚠️  No changes needed: {py_file}")
    
    print(f"\n📊 Fixed {fixed_count} files")
    print("✅ Docstring formatting fixes completed. Now run Black formatting.")

if __name__ == "__main__":
    main()
