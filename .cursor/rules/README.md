# Nexus Forensic Platform - Cursor Rules

This directory contains Cursor agent rules that ensure consistent code quality and development practices across the Nexus Forensic Platform.

## 📁 **Available Rules**

### 1. **`nexus_code_quality.mdc`** - Code Quality Standards
- **Purpose**: Defines code quality requirements and standards
- **Coverage**: Line length, imports, type hints, documentation, testing
- **When to use**: Always applied for all Python files

### 2. **`nexus_development_workflow.mdc`** - Development Workflow
- **Purpose**: Defines development process and best practices
- **Coverage**: Development workflow, testing, security, performance
- **When to use**: Always applied for all Python files

### 3. **`nexus_quick_reference.mdc`** - Quick Reference
- **Purpose**: Essential commands and patterns for quick access
- **Coverage**: Key commands, patterns, standards, thresholds
- **When to use**: Always applied for all Python files

## 🚀 **How to Use**

### **For Cursor Agents**
These rules are automatically applied when working with Python files in the Nexus project. They will:

- **Guide code generation** with proper patterns and standards
- **Suggest improvements** based on quality requirements
- **Enforce consistency** with platform architecture
- **Provide examples** of correct implementations

### **For Developers**
Use these rules as a reference for:

- **Code quality standards** and thresholds
- **Development workflow** and best practices
- **Architecture patterns** and conventions
- **Security requirements** and guidelines

## 🔧 **Integration with Development Tools**

### **Makefile Commands**
```bash
make quality              # Run comprehensive quality check
make format              # Format code with Black and isort
make lint                # Run linting tools
make quick-check         # Quick quality check
```

### **Pre-commit Hooks**
The rules integrate with pre-commit hooks to automatically:
- Format code with Black
- Organize imports with isort
- Check style with flake8
- Validate syntax

### **Quality Manager**
```bash
python code_quality_manager.py    # Comprehensive analysis
```

## 📊 **Quality Metrics**

### **Target Thresholds**
- **Black formatting**: 100% compliance
- **Import organization**: 100% isort compliance
- **Linting**: <10 flake8 warnings per file
- **Pylint**: ≥7.0/10 score
- **Syntax**: 100% validation
- **Test coverage**: ≥80%

### **Current Status**
- **Formatted files**: 69/183 (37.7%)
- **Quality score**: 5.0/10 (needs improvement)
- **Syntax errors**: 86 files need fixing

## 🎯 **Key Benefits**

1. **Consistent Code Quality**: All code follows the same standards
2. **Professional Standards**: Enterprise-grade development practices
3. **Team Productivity**: Clear guidelines and automated tools
4. **Maintainability**: Well-structured, documented code
5. **Security**: Built-in security patterns and validation

## 🔄 **Updating Rules**

### **When to Update**
- New patterns emerge in the codebase
- Quality standards are raised
- Architecture changes occur
- Security requirements evolve

### **How to Update**
1. Modify the appropriate `.mdc` file
2. Test with `make quality`
3. Update documentation if needed
4. Commit changes to version control

## 📚 **Additional Resources**

### **Documentation**
- **Implementation Summary**: `IMPLEMENTATION_SUMMARY.md`
- **Code Quality Manager**: `code_quality_manager.py`
- **Development Setup**: `setup_dev_environment.py`

### **Configuration Files**
- **Tool Configuration**: `pyproject.toml`
- **Pre-commit Hooks**: `.pre-commit-config.yaml`
- **Makefile**: `Makefile`
- **Requirements**: `requirements.txt`

## 🆘 **Getting Help**

### **Common Issues**
1. **Quality check fails**: Run `make quality` to see specific issues
2. **Formatting issues**: Use `make format` to auto-fix
3. **Import problems**: Use `isort --profile=black --line-length=88 .`
4. **Syntax errors**: Check individual files with `python -m py_compile`

### **Next Steps**
1. **Fix syntax errors** in the 86 problematic files
2. **Complete formatting** with Black for all files
3. **Improve quality scores** to meet thresholds
4. **Maintain standards** with pre-commit hooks

---

*These rules ensure the Nexus Forensic Platform maintains high-quality, professional development standards.*
