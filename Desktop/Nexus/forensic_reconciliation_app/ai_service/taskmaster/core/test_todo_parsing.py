#!/usr/bin/env python3
"""
Test TODO parsing with the updated parser
"""

import sys
from pathlib import Path

# Add the core directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from todo_master_reader import TodoMasterReader


def test_todo_parsing():
    """Test the updated TODO parser"""
    print("🧪 Testing Updated TODO Parser")
    print("=" * 50)

    # Initialize reader
    reader = TodoMasterReader()

    # Read and parse content
    content = reader.read_todo_master()
    todos = reader.parse_markdown_content(content)

    print(f"📄 Content length: {len(content)} characters")
    print(f"🔍 Parsed TODOs: {len(todos)}")
    print()

    if todos:
        print("📋 Found TODOs:")
        for i, todo in enumerate(todos[:5], 1):  # Show first 5
            print(f"  {i}. {todo['title'][:60]}...")
            print(f"     Status: {todo['status']}, Priority: {todo['priority']}")
            print()
    else:
        print("❌ No TODOs found - parser may still need adjustment")

    return len(todos)


if __name__ == "__main__":
    count = test_todo_parsing()
    if count > 0:
        print(f"✅ SUCCESS: Found {count} TODO items!")
    else:
        print("❌ FAILED: No TODO items found")
