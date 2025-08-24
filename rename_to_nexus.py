#!/usr/bin/env python3
"""
Comprehensive script to rename all instances of "Nexus" 
and related terms to "Nexus" throughout the entire workspace.
"""

import os
import re
import shutil
from pathlib import Path
from typing import List, Tuple, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NexusRenamer:
    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.rename_patterns = {
            # Text content replacements
            r'Nexus': 'Nexus',
            r'Nexus': 'Nexus',
            r'Nexus': 'Nexus',
            r'NEXUS': 'NEXUS',
            r'NEXUS': 'nexus',
            r'Nexus': 'Nexus',
            r'Nexus': 'nexus',
            
            # File and directory name patterns
            r'nexus': 'nexus',
            r'nexus': 'nexus',
            r'Nexus': 'Nexus',
            r'Nexus': 'nexus',
            
            # Common variations
            r'nexus': 'nexus',
            r'nexus': 'NEXUS',
            r'nexus': 'nexus',
            r'nexus': 'Nexus'
        }
        
        # File extensions to process
        self.text_extensions = {
            '.md', '.txt', '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', 
            '.scss', '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',
            '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat', '.cmd', '.sql',
            '.xml', '.svg', '.vue', '.svelte', '.php', '.rb', '.go', '.rs',
            '.java', '.cpp', '.c', '.h', '.hpp', '.cs', '.fs', '.vb'
        }
        
        # Directories to skip
        self.skip_dirs = {
            '.git', '.node_modules', '.venv', 'venv', 'env', '__pycache__',
            '.pytest_cache', '.mypy_cache', 'dist', 'build', 'coverage',
            '.next', '.nuxt', '.output', 'node_modules', 'bower_components'
        }
        
        # Files to skip
        self.skip_files = {
            'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
            '.DS_Store', 'Thumbs.db', 'desktop.ini'
        }
        
        self.stats = {
            'files_processed': 0,
            'files_modified': 0,
            'total_replacements': 0,
            'errors': []
        }

    def should_process_file(self, file_path: Path) -> bool:
        """Determine if a file should be processed for text replacement."""
        # Skip binary files and non-text files
        if file_path.suffix.lower() not in self.text_extensions:
            return False
            
        # Skip files in skip directories
        for skip_dir in self.skip_dirs:
            if skip_dir in file_path.parts:
                return False
                
        # Skip specific files
        if file_path.name in self.skip_files:
            return False
            
        return True

    def should_process_directory(self, dir_path: Path) -> bool:
        """Determine if a directory should be processed for renaming."""
        return not any(skip_dir in dir_path.parts for skip_dir in self.skip_dirs)

    def rename_file_content(self, file_path: Path) -> int:
        """Rename text content within a file."""
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            original_content = content
            replacements_made = 0
            
            # Apply all rename patterns
            for old_pattern, new_pattern in self.rename_patterns.items():
                # Use word boundaries for better matching
                pattern = r'\b' + re.escape(old_pattern) + r'\b'
                new_content, count = re.subn(pattern, new_pattern, content, flags=re.IGNORECASE)
                if count > 0:
                    content = new_content
                    replacements_made += count
                    logger.info(f"  Replaced {count} instances of '{old_pattern}' with '{new_pattern}'")
            
            # Write back if changes were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.stats['files_modified'] += 1
                self.stats['total_replacements'] += replacements_made
                logger.info(f"  Updated file: {file_path}")
                return replacements_made
            
            return 0
            
        except Exception as e:
            error_msg = f"Error processing file {file_path}: {str(e)}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
            return 0

    def rename_file_or_directory(self, path: Path) -> bool:
        """Rename a file or directory if it matches rename patterns."""
        try:
            old_name = path.name
            new_name = old_name
            
            # Check if the name matches any rename patterns
            for old_pattern, new_pattern in self.rename_patterns.items():
                if re.search(old_pattern, old_name, re.IGNORECASE):
                    new_name = re.sub(old_pattern, new_pattern, old_name, flags=re.IGNORECASE)
                    break
            
            if new_name != old_name:
                new_path = path.parent / new_name
                
                # Handle conflicts
                if new_path.exists():
                    counter = 1
                    while new_path.exists():
                        name_parts = new_path.stem, new_path.suffix
                        new_path = path.parent / f"{name_parts[0]}_{counter}{name_parts[1]}"
                        counter += 1
                
                # Perform the rename
                path.rename(new_path)
                logger.info(f"Renamed: {old_name} -> {new_path.name}")
                return True
                
            return False
            
        except Exception as e:
            error_msg = f"Error renaming {path}: {str(e)}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
            return False

    def process_workspace(self):
        """Process the entire workspace for renaming."""
        logger.info(f"Starting Nexus renaming process in: {self.workspace_root}")
        logger.info("=" * 60)
        
        # First pass: Rename files and directories
        logger.info("Phase 1: Renaming files and directories...")
        renamed_items = []
        
        # Process directories first (bottom-up to avoid path issues)
        dirs_to_process = []
        for root, dirs, files in os.walk(self.workspace_root, topdown=False):
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                if self.should_process_directory(dir_path):
                    dirs_to_process.append(dir_path)
        
        # Rename directories
        for dir_path in dirs_to_process:
            if self.rename_file_or_directory(dir_path):
                renamed_items.append(dir_path)
        
        # Process files
        for root, dirs, files in os.walk(self.workspace_root):
            for file_name in files:
                file_path = Path(root) / file_name
                if self.rename_file_or_directory(file_path):
                    renamed_items.append(file_path)
        
        logger.info(f"Phase 1 complete. Renamed {len(renamed_items)} items.")
        
        # Second pass: Update file contents
        logger.info("\nPhase 2: Updating file contents...")
        
        for root, dirs, files in os.walk(self.workspace_root):
            for file_name in files:
                file_path = Path(root) / file_name
                
                if self.should_process_file(file_path):
                    self.stats['files_processed'] += 1
                    logger.info(f"Processing: {file_path}")
                    
                    replacements = self.rename_file_content(file_path)
                    if replacements > 0:
                        logger.info(f"  Made {replacements} replacements")
        
        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print a summary of the renaming operation."""
        logger.info("\n" + "=" * 60)
        logger.info("NEXUS RENAMING SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Files processed: {self.stats['files_processed']}")
        logger.info(f"Files modified: {self.stats['files_modified']}")
        logger.info(f"Total replacements: {self.stats['total_replacements']}")
        logger.info(f"Items renamed: {len([e for e in self.stats['errors'] if 'renaming' in e.lower()])}")
        
        if self.stats['errors']:
            logger.info(f"\nErrors encountered: {len(self.stats['errors'])}")
            for error in self.stats['errors']:
                logger.error(f"  {error}")
        else:
            logger.info("\nNo errors encountered!")
        
        logger.info("\nRenaming process complete!")

def main():
    """Main function to run the Nexus renaming process."""
    # Get the current working directory as the workspace root
    workspace_root = os.getcwd()
    
    print(f"Current workspace: {workspace_root}")
    print("This script will rename all instances of 'Nexus' and related terms to 'Nexus'")
    print("in the current workspace and all subdirectories.")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        return
    
    # Create and run the renamer
    renamer = NexusRenamer(workspace_root)
    renamer.process_workspace()

if __name__ == "__main__":
    main()
