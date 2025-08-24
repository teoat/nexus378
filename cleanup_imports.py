#!/usr/bin/env python3


    """Find unused imports in a Python file.
        print(f"Error parsing {file_path}: {e}")
        return []

def cleanup_file_imports(file_path):
    """Clean up unused imports in a single file.
        print(f"Error cleaning {file_path}: {e}")
        return False

def main():
    """Main function to clean up imports across all Python files.
    workspace_path = Path("nexus")
    
    if not workspace_path.exists():
        print("❌ nexus directory not found")
        return
    
    print("🔍 Scanning for Python files...")
    python_files = list(workspace_path.rglob("*.py"))
    print(f"✅ Found {len(python_files)} Python files")
    
    print("\n🧹 Cleaning up unused imports...")
    cleaned_count = 0
    
    for py_file in python_files:
        if cleanup_file_imports(py_file):
            cleaned_count += 1
    
    print(f"✅ Cleaned {cleaned_count} files")
    
    print("\n🔍 Running syntax check...")
    syntax_errors = []
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            ast.parse(content)
        except Exception as e:
            syntax_errors.append(f"{py_file}: {e}")
    
    if syntax_errors:
        print(f"❌ Found {len(syntax_errors)} syntax errors:")
        for error in syntax_errors[:5]:
            print(f"   - {error}")
        if len(syntax_errors) > 5:
            print(f"   ... and {len(syntax_errors) - 5} more")
    else:
        print("✅ All files have valid syntax")

if __name__ == "__main__":
    main()
