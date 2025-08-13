# Coding Sections

This document outlines the different sectional coding areas that agents can work on simultaneously, along with their boundaries and responsibilities.

## 1. Frontend Development Section
- **Location**: `app/pages`, `app/components`, `app/stories`, `app/hooks`, `app/lib`
- **Responsibilities**:
  - Develop, test, and maintain all client-side React components using Next.js.
  - Manage application state using hooks and context.
  - Implement UI/UX designs, ensuring responsiveness and accessibility (WCAG compliance).
  - Create and document reusable components in Storybook.
- **Boundaries**: Does not directly query databases. All data access must go through the Node.js API Gateway.

## 2. Node.js API Gateway / BFF Section
- **Location**: `app/backend/api`
- **Responsibilities**:
  - Develop and maintain the NestJS-based API gateway, which serves as the single entry point for the frontend.
  - Implement authentication, authorization (RBAC), and session management.
  - Aggregate and shape data from downstream services (Python AI, databases) for efficient consumption by the frontend.
  - Manage WebSocket connections for real-time communication.
- **Boundaries**: Does not contain core business logic for AI or complex data analysis. It is primarily an orchestration and security layer.

## 3. Python AI Service Section
- **Location**: `python-ai/`
- **Responsibilities**:
  - Implement all core data processing, machine learning, and agentic logic.
  - Develop and maintain the FastAPI server for synchronous operations.
  - Create and manage asynchronous workers (RabbitMQ consumers) for long-running tasks.
  - Build and train ML models for fraud detection and data analysis.
  - Implement and manage the LangGraph agents and their associated tools.
- **Boundaries**: Does not directly interact with the user or serve frontend assets. All communication is routed through the Node.js Gateway.

## 4. Shared Components/Utils Section
- **Location**: `core/utils`, `shared-components`
- **Responsibilities**:
  - Develop and maintain reusable components and utility functions.
  - Provide shared libraries and tools used across the project.
- **Boundaries**: Do not modify or maintain project-specific configurations or sensitive data handling.

## 5. Data Analysis Section
- **Location**: `core/analysis`
- **Responsibilities**:
  - Implement data analysis tools and algorithms.
  - Develop fraud detection mechanisms and reporting tools.
- **Boundaries**: Focus on analytical tasks and avoid direct user interface or backend business logic.

## Collaboration Guidelines
- **Clear Boundaries**: Each section operates within defined boundaries to prevent overlap and conflict.
- **Communication**: 
  - Hold weekly cross-section meetings.
  - Use ad-hoc syncs for critical issues or major changes.
- **Code Reviews**: 
  - Conduct code reviews across sections.
  - Mandate reviews from at least two maintainers per section.
  - Include a senior developer if complex or high-risk changes are being reviewed.

## Contribution Process
1. **Issue Tracking**: 
   - Create issues in the relevant section's repository with clear labels (e.g., "Frontend", "Backend").
2. **Code Submission**: 
   - Follow branch naming conventions (e.g., "feature/section-name-issue-id").
   - Submit pull requests with detailed descriptions and links to relevant documentation.
3. **Code Reviews**: 
   - Ensure all changes pass review by section maintainers.
   - Address feedback promptly and be prepared to make adjustments.

## Document Structure
- Use consistent headings and subheadings for clarity.
- Include visual representations of the codebase structure where helpful.
- Add examples or diagrams to illustrate key points.

This structure ensures clear boundaries, efficient collaboration, and maintainable code quality while allowing for growth and complexity in the project.