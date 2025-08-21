# IntelliAudit AI - Merged Frontend Application

This is the consolidated frontend application that combines the best features and components from multiple development branches (378TS and 378fire) into a unified, comprehensive forensic analysis platform.

## 🏗️ Architecture Overview

The application follows a modern, modular architecture with the following key components:

### Core Structure
- **Next.js 14** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **Radix UI** components for accessible UI elements
- **Firebase** for authentication and backend services
- **Zustand** for state management

### Key Directories

#### `/app`
- **`layout.tsx`** - Root layout with theme provider
- **`page.tsx`** - Main application entry point
- **`firebase-config.ts`** - Firebase configuration
- **`config.ts`** - Application configuration
- **`globals.css`** - Global styles and Tailwind configuration

#### `/components`
- **`ui/`** - Radix UI components and custom UI elements
- **`views/`** - Page-level view components
- **`theme-provider.tsx`** - Theme management (light/dark mode)
- **`theme-toggle.tsx`** - Theme switching component
- **`app-shell.tsx`** - Main application shell layout
- **`error-boundary.tsx`** - Error handling and recovery
- **`analysis-modules.tsx`** - Analysis workflow components
- **`rule-engine-dialog.tsx`** - Rule engine configuration interface

#### `/features`
- **`1-ingestion/`** - File upload and data ingestion
  - **`actions/`** - Server actions for file processing
  - **`ai-flows/`** - AI-powered ingestion workflows
  - **`components/`** - Ingestion-specific UI components
- **`2-reconciliation/`** - Transaction matching and reconciliation
  - **`actions/`** - Reconciliation server actions
  - **`ai-flows/`** - AI-powered matching algorithms
  - **`components/`** - Reconciliation interface components
- **`3-analysis/`** - Forensic analysis and reporting
  - **`actions/`** - Analysis server actions
  - **`ai-flows/`** - AI-powered analysis workflows
  - **`components/`** - Analysis and visualization components
  - **`pdf-report-generator.ts`** - PDF report generation
- **`4-maintenance/`** - System maintenance and AI training
  - **`ai-flows/`** - Self-learning and maintenance workflows
  - **`components/`** - Maintenance interface components

#### `/lib`
- **`firebase.ts`** - Firebase client configuration
- **`firebase-admin.ts`** - Firebase admin SDK setup
- **`csv-to-json.ts`** - CSV parsing utilities
- **`csv.worker.ts`** - Web worker for CSV processing
- **`financial-integrations.ts`** - Banking and financial API integrations
- **`rule-engine.ts`** - Business rule processing engine
- **`utils.ts`** - General utility functions
- **`performance-trace.ts`** - Performance monitoring utilities

#### `/hooks`
- **`use-auth.tsx`** - Authentication state management
- **`use-audit-store.ts`** - Audit data state management
- **`use-mobile.tsx`** - Mobile device detection
- **`use-notifications.ts`** - Notification management

#### `/store`
- **`gamification.store.ts`** - Gamification and achievement system
- **`root.store.ts`** - Root application state

#### `/types`
- **`types.ts`** - TypeScript type definitions

#### `/plugins`
- **`csv-parser.ts`** - CSV parsing plugin

#### `/ai`
- **`dev.ts`** - AI development utilities
- **`genkit.ts`** - Genkit AI framework integration

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Firebase project setup

### Installation
```bash
cd 378/app
npm install
```

### Environment Setup
Create a `.env.local` file with your Firebase configuration:
```env
NEXT_PUBLIC_FIREBASE_API_KEY#your_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN#your_domain
NEXT_PUBLIC_FIREBASE_PROJECT_ID#your_project_id
# ... other Firebase config
```

### Development
```bash
npm run dev
```

### Building
```bash
npm run build
npm start
```

## 🔧 Key Features

### 1. Multi-Mode Operation
- **Guided Mode**: Step-by-step analysis with user control
- **Automated Mode**: Full AI-powered automation
- **Cost-Optimized Mode**: Balanced performance and cost

### 2. AI-Powered Analysis
- **Multi-Pass Reconciliation**: Iterative transaction matching
- **Fuzzy Matching**: AI-powered description matching
- **Forensic Analysis**: Comprehensive risk assessment
- **Entity Relationship Mapping**: Network analysis and visualization

### 3. Advanced UI Components
- **Responsive Design**: Mobile-first approach
- **Dark/Light Theme**: User preference support
- **Real-time Updates**: WebSocket integration
- **Interactive Dashboards**: Dynamic data visualization

### 4. Security & Compliance
- **Role-Based Access Control**: Granular permissions
- **Audit Logging**: Complete activity tracking
- **Data Encryption**: End-to-end security
- **Compliance Reporting**: Regulatory requirement support

## 📊 Data Flow

1. **File Ingestion**: Upload and parse financial data
2. **Column Mapping**: AI-assisted data structure recognition
3. **Reconciliation**: Multi-pass transaction matching
4. **Analysis**: AI-powered forensic investigation
5. **Reporting**: Generate compliance and audit reports

## 🧪 Testing

```bash
npm run test          # Run Jest tests
npm run test:coverage # Run tests with coverage
```

## 📚 Storybook

```bash
npm run storybook     # Start Storybook development server
npm run build-storybook # Build static Storybook
```

## 🐳 Docker

```bash
docker build -t intelliaudit-frontend .
docker run -p 3000:3000 intelliaudit-frontend
```

## 🔄 Migration Notes

This application represents a consolidation of:
- **378TS**: TypeScript-focused development with comprehensive UI components
- **378fire**: Firebase-integrated features with advanced AI workflows

### Resolved Conflicts
- **Error Boundaries**: Kept the more comprehensive error-boundary.tsx
- **Package Dependencies**: Merged all dependencies without conflicts
- **Component Structure**: Maintained unique components from both branches
- **Configuration Files**: Preserved essential configs from both sources

### Preserved Features
- All AI workflows and analysis modules
- Complete UI component library
- Firebase integration and authentication
- Advanced reconciliation algorithms
- Comprehensive testing and development tools

## 🤝 Contributing

1. Follow the established coding standards
2. Use TypeScript for all new code
3. Write tests for new features
4. Update this README for significant changes

## 📄 License

This project is proprietary software for forensic analysis and audit purposes.

