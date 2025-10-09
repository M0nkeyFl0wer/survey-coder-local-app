# Contributing to Survey Coder - Modernized

Thank you for your interest in contributing to the modernized Survey Coder! This document provides guidelines and information for contributors.

## 🚀 Quick Start for Contributors

### Prerequisites

- Python 3.12+
- Git
- pipenv (recommended) or pip
- GitHub account

### Development Setup

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/your-username/survey-coder-modernized.git
cd survey-coder-modernized

# Add upstream remote
git remote add upstream https://github.com/original-owner/survey-coder-modernized.git

# Install dependencies
pipenv install --dev

# Activate virtual environment
pipenv shell

# Run tests to ensure everything works
python test_new_architecture.py
```

## 🛠️ Development Workflow

### Before Making Changes

1. **Create an Issue** (for significant changes)
   - Describe the problem or feature request
   - Wait for feedback from maintainers

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

### Making Changes

1. **Write Code**
   - Follow existing code style and patterns
   - Add type hints where appropriate
   - Include docstrings for public functions

2. **Test Your Changes**
   ```bash
   # Run tests
   python test_new_architecture.py
   
   # Run linting
   pipenv run flake8 coder_app/
   
   # Format code
   pipenv run black coder_app/
   
   # Check types (if mypy is installed)
   pipenv run mypy coder_app/
   ```

3. **Update Documentation**
   - Update README.md if adding new features
   - Update WARP.md for AI assistant guidance
   - Add docstrings and comments

### Submitting Changes

1. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add new IDE integration command"
   # or
   git commit -m "fix: resolve database connection issue"
   ```

2. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create Pull Request**
   - Use the GitHub web interface
   - Fill out the PR template
   - Link any related issues

## 📋 Contribution Types

### 🐛 Bug Fixes

- Fix existing functionality
- Include test cases that reproduce the bug
- Update documentation if necessary

### ✨ New Features

- Add new functionality
- Include comprehensive tests
- Update CLI help and documentation
- Consider IDE integration implications

### 📚 Documentation

- Fix typos or unclear instructions
- Add examples and use cases
- Improve API documentation
- Update development guides

### 🔧 IDE Integration

- VS Code tasks and configurations
- Command palette integrations
- Snippet creation
- Workflow optimizations

## 🎯 Priority Areas

### High Priority
- Multi-agent architecture (Phase 2)
- Real AI classification integration
- Performance optimizations
- Security improvements

### Medium Priority  
- Additional export formats
- Enhanced CLI features
- Better error handling
- Test coverage improvements

### Welcome for New Contributors
- Documentation improvements
- Example projects and tutorials
- Bug fixes and small enhancements
- IDE workflow optimizations

## 📏 Code Standards

### Python Style

- Follow PEP 8 style guide
- Use Black for code formatting
- Maximum line length: 88 characters
- Use type hints for function signatures

### Example Code Style

```python
from typing import List, Optional

class ExampleService:
    """Service for handling example operations."""
    
    def process_data(self, data: List[str], options: Optional[dict] = None) -> dict:
        """Process the provided data with optional configuration.
        
        Args:
            data: List of strings to process
            options: Optional configuration dictionary
            
        Returns:
            Dictionary containing processed results
        """
        # Implementation here
        return {"processed": True}
```

### Commit Message Format

Use conventional commits:

- `feat:` New features
- `fix:` Bug fixes  
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test additions or modifications
- `chore:` Maintenance tasks

Examples:
```
feat: add batch classification for IDE integration
fix: resolve database connection timeout issue
docs: update installation instructions for Windows
```

## 🧪 Testing

### Running Tests

```bash
# Full test suite
python test_new_architecture.py

# Specific functionality
python -m pytest tests/test_models.py  # (when added)

# With coverage
python -m pytest --cov=coder_app tests/  # (when added)
```

### Writing Tests

- Add tests for new functionality
- Follow existing test patterns
- Include edge cases
- Test error conditions

## 🔐 Security Guidelines

### Before Submitting

- [ ] No API keys in commits
- [ ] No sensitive data in examples
- [ ] Security implications considered
- [ ] Dependencies are secure

### Security-Sensitive Changes

- Database access modifications
- API client implementations
- Authentication/authorization
- Data export functionality

These require extra review and testing.

## 🤝 Code Review Process

### For Contributors

1. **Self-Review**: Check your own PR before submitting
2. **Address Feedback**: Respond promptly to review comments
3. **Update Tests**: Ensure tests pass after changes
4. **Stay Engaged**: Participate in discussion

### Review Criteria

- **Functionality**: Does it work as intended?
- **Security**: Are there security implications?
- **Performance**: Is it efficient?
- **Maintainability**: Is the code clean and documented?
- **Testing**: Are there adequate tests?

## 🌟 Recognition

Contributors are recognized in:

- README.md acknowledgments
- Release notes
- GitHub contributors page

## 🆘 Getting Help

### Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Code Comments**: Implementation-specific questions

### What to Include

- **Bug Reports**: Steps to reproduce, expected vs actual behavior
- **Feature Requests**: Use case, proposed implementation
- **Questions**: Context, what you've tried, specific error messages

## 📊 Project Roadmap

### Current Phase: Local Storage & Persistence ✅

### Next Phase: Multi-Agent Architecture

Key areas for contribution:
- Abstract LLM provider interface
- Ollama client implementation
- SSH tunnel management
- Agent coordination system

### Future Phases

- Advanced IDE Integration
- Hot Data & Adaptive Systems
- Performance optimizations

## 📝 License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project (MIT License).

## 🙏 Thank You!

Your contributions make this project better for everyone. Whether you're fixing a typo, adding a feature, or improving documentation, every contribution is valuable.

---

**Questions?** Feel free to open an issue or start a discussion!

**Ready to contribute?** Check out the [good first issue](https://github.com/your-repo/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) label for beginner-friendly tasks.