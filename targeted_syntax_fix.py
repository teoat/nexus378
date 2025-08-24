#!/usr/bin/env python3
"""Targeted syntax fix for remaining critical errors."""

import os
import re

def fix_file_syntax(file_path):
    """Fix specific syntax issues in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix 1: Remove any text before the shebang or imports
        if not content.startswith('#!/usr/bin/env python3') and not content.startswith('#!/usr/bin/python'):
            # Find the first valid Python line
            lines = content.split('\n')
            fixed_lines = []
            found_python = False
            
            for line in lines:
                if not found_python:
                    if (line.strip().startswith('#!/') or 
                        line.strip().startswith('import ') or 
                        line.strip().startswith('from ') or
                        line.strip().startswith('"""') or
                        line.strip().startswith("'''") or
                        line.strip() == ''):
                        found_python = True
                        fixed_lines.append(line)
                else:
                    fixed_lines.append(line)
            
            content = '\n'.join(fixed_lines)
        
        # Fix 2: Fix unterminated docstrings
        content = re.sub(r'"""\s*[^"]*$', '', content, flags=re.MULTILINE)
        
        # Fix 3: Fix unmatched parentheses
        content = re.sub(r'\)\s*$', '', content, flags=re.MULTILINE)
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    """Fix the remaining syntax errors."""
    problem_files = [
        'ai_service/agents/automated_escalation.py',
        'ai_service/agents/compliance_rule_engine.py',
        'ai_service/agents/fraud_agent_entity_network.py',
        'ai_service/agents/fraud_agent_pattern_detection.py',
        'ai_service/agents/litigation_agent.py',
        'ai_service/agents/todo_automation_enhanced.py',
        'ai_service/agents/todo_cli.py',
        'ai_service/agents/todo_config.py',
        'ai_service/auth/encryption_service.py',
        'ai_service/auth/mfa/__init__.py',
        'ai_service/auth/mfa/config.py',
        'ai_service/auth/mfa/hardware_auth.py',
        'ai_service/auth/mfa/mfa_implementation.py',
        'ai_service/auth/mfa/mfa_manager.py',
        'ai_service/auth/mfa/mfa_mcp_server.py',
        'ai_service/auth/mfa/sms_auth.py'
    ]
    
    fixed_count = 0
    for file_path in problem_files:
        if os.path.exists(file_path):
            print(f"Fixing: {file_path}")
            if fix_file_syntax(file_path):
                fixed_count += 1
                print(f"  ✅ Fixed")
            else:
                print(f"  ⚠️  No changes needed")
    
    print(f"\nFixed {fixed_count} files")

if __name__ == "__main__":
    main()
