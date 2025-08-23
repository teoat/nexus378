# 🕵️ Nexus Forensic Platform - README

*Quick Start Guide - For comprehensive documentation see [NEXUS_MASTER_DOCUMENTATION.md](../NEXUS_MASTER_DOCUMENTATION.md)*

## 🚀 **Quick Start**

### **1. Setup Development Environment**
```bash
make dev-setup           # Complete environment setup
make install-dev         # Install development dependencies
make pre-commit          # Install pre-commit hooks
```

### **2. Run Quality Checks**
```bash
make quality              # Comprehensive quality check
make format              # Format all code
make lint                # Run linting tools
```

### **3. Start Development**
```bash
make test                # Run all tests
make quick-check         # Quick quality check before committing
```

## 📋 **Essential Commands**

| Command | Description |
|---------|-------------|
| `make help` | Show all available commands |
| `make quality` | Run comprehensive quality check |
| `make format` | Format code with Black and isort |
| `make lint` | Run linting tools |
| `make test` | Run all tests |
| `make dev-setup` | Complete development environment setup |

## 🏗️ **Project Structure**

```
forensic_reconciliation_app/
├── ai_service/           # Core AI services
│   ├── agents/          # AI agent implementations
│   ├── auth/            # Authentication services
│   ├── core_agents/     # Base agent classes
│   └── taskmaster/      # Task management system
├── gateway/              # API gateway & middleware
├── infrastructure/       # Load balancing & monitoring
└── frontend/            # Dashboard & UI components
```

## 📊 **Current Status**

- **Phase 1**: ✅ **COMPLETE** - Foundation & Infrastructure
- **Phase 2**: 🔄 **75% COMPLETE** - Core Development
- **Total Tasks**: 23 Priority TODO Items
- **Completed**: 13 tasks
- **Pending**: 8 tasks
- **Code Quality**: ⚠️ **NEEDS ATTENTION** - 54 files with syntax errors

## 🎯 **Next Steps**

1. **Fix Syntax Errors**: Address 86 files with parsing issues
2. **Complete Black Formatting**: Resolve syntax errors for full formatting
3. **Improve Quality Scores**: Target Pylint score ≥7.0/10
4. **Complete Phase 2**: Finish AI agent implementations

## 📚 **Documentation**

- **[NEXUS_MASTER_DOCUMENTATION.md](../NEXUS_MASTER_DOCUMENTATION.md)** - Complete project documentation
- **[TODO_MASTER.md](TODO_MASTER.md)** - Current task status and tracking
- **[CODE_QUALITY_REPORT.md](CODE_QUALITY_REPORT.md)** - Latest quality metrics

## 🔧 **Development Tools**

- **Code Quality Manager**: `python code_quality_manager.py`
- **Development Setup**: `python setup_dev_environment.py`
- **Tool Configuration**: `pyproject.toml`
- **Pre-commit Hooks**: `.pre-commit-config.yaml`

## 🆘 **Getting Help**

1. **Check this README** for quick commands
2. **Review master documentation** for comprehensive details
3. **Run quality checks** to identify issues
4. **Check TODO_MASTER.md** for current task status

---

*For comprehensive project documentation, architecture details, development guidelines, and current status, see [NEXUS_MASTER_DOCUMENTATION.md](../NEXUS_MASTER_DOCUMENTATION.md)*

**Last Updated**: December 19, 2024  
**Status**: Active Development - Phase 2
