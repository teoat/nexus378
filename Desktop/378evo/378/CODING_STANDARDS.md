# Coding Standards

This document outlines the coding standards for Python and JavaScript development in this project. Adhering to these guidelines ensures consistency, readability, and maintainability of the codebase.

## Python

All Python code must follow the [PEP 8 -- Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/).

### Key PEP 8 Guidelines:

*   **Indentation:** Use 4 spaces per indentation level.
*   **Line Length:** Limit all lines to a maximum of 79 characters.
*   **Imports:**
    *   Imports should usually be on separate lines.
    *   Imports are always put at the top of the file, just after any module comments and docstrings, and before module globals and constants.
    *   Imports should be grouped in the following order:
        1.  Standard library imports.
        2.  Related third-party imports.
        3.  Local application/library specific imports.
*   **Whitespace in Expressions and Statements:**
    *   Avoid extraneous whitespace in the following situations:
        *   Immediately inside parentheses, brackets, or braces.
        *   Immediately before a comma, semicolon, or colon.
    *   Always surround these binary operators with a single space on either side: assignment (`=`), augmented assignment (`+=`, `-=`, etc.), comparisons (`==`, `<`, `>`, `!=`, `<>`, `<=`, `>=`, `in`, `not in`, `is`, `is not`), Booleans (`and`, `or`, `not`).
*   **Naming Conventions:**
    *   `lowercase` for functions and variables.
    *   `lower_case_with_underscores` for functions and variables.
    *   `UPPERCASE` for constants.
    *   `UPPER_CASE_WITH_UNDERSCORES` for constants.
    *   `CapWords` for classes.
*   **Comments:**
    *   Comments that contradict the code are worse than no comments. Always make a priority of keeping the comments up-to-date when the code changes!
    *   Comments should be complete sentences.
    *   Block comments generally apply to some (or all) code that follows them, and are indented to the same level as that code.
    *   Use inline comments sparingly.

### Tooling & Configuration

*   **Linter:** `flake8` is mandatory. Configuration is in `.flake8`.
*   **Formatter:** `black` is mandatory. Configuration is in `pyproject.toml`.
*   **Type Checking:** `mypy` is mandatory for static type analysis.

## TypeScript/JavaScript (React & NestJS)

All TypeScript/JavaScript code will be governed by **ESLint** and **Prettier**.

### Key Guidelines:

*   **Framework-Specific Rules:** We will use the recommended ESLint plugins for our frameworks:
    *   `eslint-plugin-react` and `eslint-plugin-react-hooks` for React.
    *   `@typescript-eslint/eslint-plugin` for TypeScript.
    *   `eslint-plugin-jest` for tests.
*   **Imports:**
    *   Imports must be organized by the `eslint-plugin-import` rules.
    *   Use absolute paths for imports from other modules (e.g., `import { MyComponent } from 'src/components/MyComponent'`).
*   **React:**
    *   Components must be defined using function declarations and hooks. Class components are disallowed.
    *   Follow the Rules of Hooks.
*   **NestJS:**
    *   Use decorators for routing, dependency injection, and guards.
    *   Services should contain business logic, while controllers should be lean and only handle HTTP request/response cycles.

### Tooling & Configuration

*   **Linter:** `ESLint`. Configuration is in `.eslintrc.js`.
*   **Formatter:** `Prettier`. Configuration is in `.prettierrc`. Prettier will be run automatically on commit.

## Pre-Commit Hooks

To enforce these standards automatically, a pre-commit hook will be configured using `husky`. This hook will run `lint-staged`, which will execute `black`, `flake8`, and `prettier` on all staged files before allowing a commit. This ensures that no code that violates our standards can enter the codebase.
