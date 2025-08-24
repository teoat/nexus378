#!/usr/bin/env python3
"""
Markdown Consolidation Script
Consolidates all .md files into a single master document for the Forensic Platform.
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List


class MarkdownConsolidator:
    """Consolidates multiple markdown files into a single master document"""

    def __init__(self, root_directory: str = "."):
        self.root_directory = Path(root_directory)
        self.markdown_files: List[Path] = []
        self.consolidated_content: Dict[str, Any] = {}
        self.sections: Dict[str, str] = {}

    def discover_markdown_files(self) -> List[Path]:
        """Discover all markdown files in the directory tree"""
        markdown_files = []

        for file_path in self.root_directory.rglob("*.md"):
            # Skip certain files that shouldn't be consolidated
            if any(
                skip in str(file_path)
                for skip in [
                    "FORENSIC_PLATFORM_MASTER.md",
                    "consolidate_markdown.py",
                    "__pycache__",
                    ".git",
                ]
            ):
                continue

            markdown_files.append(file_path)

        # Sort files by importance/priority
        markdown_files.sort(key=self._get_file_priority)

        self.markdown_files = markdown_files
        return markdown_files

    def _get_file_priority(self, file_path: Path) -> int:
        """Get priority for file ordering in consolidation"""
        priority_map = {
            "README.md": 1,
            "MASTER_ARCHITECTURE.md": 2,
            "TODO_MASTER.md": 3,
            "QUICKSTART.md": 4,
            "project_overview.md": 5,
            "architecture.md": 6,
            "api_reference.md": 7,
            "workflows.md": 8,
            "taskmaster_system.md": 9,
            "MCP_SYSTEM_SUMMARY.md": 10,
            "MCP_WORK_LOG.md": 11,
            "MFA_IMPLEMENTATION_SUMMARY.md": 12,
            "forensic_cases.md": 13,
            "TASK_BREAKDOWN_REPORT.md": 14,
            "INFRASTRUCTURE_TODOS.md": 15,
        }

        filename = file_path.name
        return priority_map.get(filename, 100)  # Default low priority

    def categorize_file(self, file_path: Path) -> str:
        """Categorize a markdown file based on its content and location"""
        filename = file_path.name.lower()
        path_str = str(file_path).lower()

        # Architecture and Design
        if any(
            keyword in filename for keyword in ["architecture", "master", "overview"]
        ):
            return "Architecture & Design"

        # Documentation and API
        if any(keyword in filename for keyword in ["api", "reference", "docs"]):
            return "Documentation & API"

        # Development and Tasks
        if any(keyword in filename for keyword in ["todo", "task", "breakdown"]):
            return "Development & Tasks"

        # Implementation and Work
        if any(keyword in filename for keyword in ["implementation", "work", "mcp"]):
            return "Implementation & Work"

        # Security and Authentication
        if any(keyword in filename for keyword in ["mfa", "security", "auth"]):
            return "Security & Authentication"

        # Use Cases and Examples
        if any(keyword in filename for keyword in ["cases", "workflows", "examples"]):
            return "Use Cases & Examples"

        # Quick Start and Setup
        if any(keyword in filename for keyword in ["quickstart", "setup", "install"]):
            return "Quick Start & Setup"

        # Default category
        return "General Documentation"

    def extract_file_content(self, file_path: Path) -> Dict[str, Any]:
        """Extract content and metadata from a markdown file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Extract title from first heading
            title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            title = (
                title_match.group(1)
                if title_match
                else file_path.stem.replace("_", " ").title()
            )

            # Extract description from first paragraph
            description_match = re.search(r"^([^#\n]+)$", content, re.MULTILINE)
            description = (
                description_match.group(1).strip() if description_match else ""
            )

            # Count sections and content
            sections = len(re.findall(r"^#{2,}\s+", content, re.MULTILINE))
            lines = len(content.split("\n"))

            return {
                "path": str(file_path),
                "filename": file_path.name,
                "title": title,
                "description": description,
                "category": self.categorize_file(file_path),
                "sections": sections,
                "lines": lines,
                "content": content,
                "relative_path": str(file_path.relative_to(self.root_directory)),
            }

        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return {
                "path": str(file_path),
                "filename": file_path.name,
                "title": "Error Reading File",
                "description": f"Could not read file: {e}",
                "category": "Error",
                "sections": 0,
                "lines": 0,
                "content": f"# Error Reading File\n\nCould not read {file_path}: {e}",
                "relative_path": str(file_path.relative_to(self.root_directory)),
            }

    def consolidate_content(self) -> str:
        """Consolidate all markdown content into a single document"""
        print("🔍 Discovering markdown files...")
        self.discover_markdown_files()

        print(f"📚 Found {len(self.markdown_files)} markdown files")

        # Extract content from all files
        file_contents = []
        for file_path in self.markdown_files:
            print(f"  📖 Processing: {file_path.name}")
            content = self.extract_file_content(file_path)
            file_contents.append(content)

        # Group by category
        categories = {}
        for content in file_contents:
            category = content["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append(content)

        # Generate consolidated content
        consolidated = self._generate_consolidated_document(file_contents, categories)

        return consolidated

    def _generate_consolidated_document(
        self, file_contents: List[Dict], categories: Dict
    ) -> str:
        """Generate the consolidated markdown document"""

        # Header
        consolidated = """# 🎯 Nexus + Fraud Platform - MASTER DOCUMENT

> **Single Source of Truth** - Consolidated from all platform documentation and specifications

---

## 📋 Table of Contents

"""

        # Generate table of contents
        toc_sections = []
        for category, files in categories.items():
            category_id = category.lower().replace(" & ", "-").replace(" ", "-")
            toc_sections.append(f"- [{category}](#{category_id})")

            for file_info in files:
                file_id = (
                    file_info["filename"].lower().replace(".md", "").replace("_", "-")
                )
                toc_sections.append(f"  - [{file_info['title']}](#{file_id})")

        consolidated += "\n".join(toc_sections)
        consolidated += "\n\n---\n\n"

        # Generate content sections
        for category, files in categories.items():
            category_id = category.lower().replace(" & ", "-").replace(" ", "-")
            consolidated += f"## {category}\n\n"

            for file_info in files:
                file_id = (
                    file_info["filename"].lower().replace(".md", "").replace("_", "-")
                )

                # File header
                consolidated += f"### {file_info['title']}\n\n"
                consolidated += f"**File**: `{file_info['relative_path']}`\n\n"

                if file_info["description"]:
                    consolidated += f"**Description**: {file_info['description']}\n\n"

                consolidated += f"**Stats**: {file_info['sections']} sections, {file_info['lines']} lines\n\n"

                # Add content with adjusted heading levels
                content = self._adjust_heading_levels(file_info["content"], 4)
                consolidated += content

                consolidated += "\n\n---\n\n"

        # Footer
        consolidated += """## 📊 Consolidation Summary

This document consolidates information from the following sources:

"""

        for file_info in file_contents:
            consolidated += (
                f"- **{file_info['title']}** (`{file_info['relative_path']}`)\n"
            )
            consolidated += f"  - Category: {file_info['category']}\n"
            consolidated += f"  - Sections: {file_info['sections']}, Lines: {file_info['lines']}\n\n"

        consolidated += f"""
**Total Files Consolidated**: {len(file_contents)}
**Total Categories**: {len(categories)}
**Generated**: {self._get_timestamp()}

---

*This document is automatically generated and should be regenerated when source files change.*
"""

        return consolidated

    def _adjust_heading_levels(self, content: str, min_level: int = 1) -> str:
        """Adjust heading levels to fit within the consolidated document structure"""
        lines = content.split("\n")
        adjusted_lines = []

        for line in lines:
            if line.startswith("#"):
                # Count leading #s
                level = len(line) - len(line.lstrip("#"))
                # Adjust level to be at least min_level
                new_level = max(level, min_level)
                # Replace with new level
                adjusted_line = "#" * new_level + line[level:]
                adjusted_lines.append(adjusted_line)
            else:
                adjusted_lines.append(line)

        return "\n".join(adjusted_lines)

    def _get_timestamp(self) -> str:
        """Get current timestamp for the document"""
        from datetime import datetime

        return datetime.now().strftime("%B %d, %Y at %I:%M %p")

    def save_consolidated_document(
        self, output_path: str = "FORENSIC_PLATFORM_MASTER.md"
    ) -> None:
        """Save the consolidated document"""
        consolidated_content = self.consolidate_content()

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(consolidated_content)

        print(f"✅ Consolidated document saved to: {output_path}")

        # Also save metadata
        metadata_path = output_path.replace(".md", "_metadata.json")
        metadata = {
            "consolidation_date": self._get_timestamp(),
            "total_files": len(self.markdown_files),
            "categories": {
                cat: len(files) for cat, files in self._group_by_category().items()
            },
            "files": [
                {
                    "filename": f["filename"],
                    "title": f["title"],
                    "category": f["category"],
                    "path": f["relative_path"],
                }
                for f in [self.extract_file_content(fp) for fp in self.markdown_files]
            ],
        }

        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        print(f"📊 Metadata saved to: {metadata_path}")

    def _group_by_category(self) -> Dict[str, List]:
        """Group files by category"""
        categories = {}
        for file_path in self.markdown_files:
            content = self.extract_file_content(file_path)
            category = content["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append(content)
        return categories


def main():
    """Main function to run the consolidation"""
    print("🚀 Forensic Platform Markdown Consolidation")
    print("=" * 50)

    consolidator = MarkdownConsolidator(".")
    consolidator.save_consolidated_document()

    print("\n🎉 Consolidation completed successfully!")
    print("\n📋 Next steps:")
    print("1. Review the consolidated document")
    print("2. Update any cross-references")
    print("3. Remove or archive individual markdown files")
    print("4. Set up automated consolidation if needed")


if __name__ == "__main__":
    main()
