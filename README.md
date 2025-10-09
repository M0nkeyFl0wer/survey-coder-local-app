# Survey Coder - Modernized Architecture

> 🚀 **AI-powered survey data analysis with persistent local storage and multi-agent capabilities**

A modernized, local-first version of the Survey Coder application that moves beyond Streamlit sessions to provide persistent project management, CLI workflows, and IDE integration for intelligent survey response classification.

## ✨ Features

- **🗄️ Persistent Storage**: SQLite database with project versioning - no more lost work!
- **🖥️ CLI Interface**: Complete command-line interface for project management and automation
- **🔧 IDE Integration**: VS Code tasks, snippets, and workflow optimization
- **🤖 AI Classification**: OpenAI-powered survey response classification and codebook generation
- **📊 Multi-format Export**: JSON, CSV, Excel, and one-hot encoded outputs
- **🔄 Upstream Sync**: Track and integrate changes from the original repository
- **🔐 Security-First**: Comprehensive protection of API keys and sensitive data

## 🏗️ Architecture

### Current State vs Target State

| **Current (Streamlit)** | **Target (Modernized)** |
|------------------------|-------------------------|
| Session-based storage | Persistent SQLite database |
| Web UI only | CLI + IDE integration |
| Single agent | Multi-agent via SSH/Ollama |
| Manual workflows | Automated IDE workflows |

### Modular Structure

```
coder_app/
├── models/           # Pydantic data models
├── services/         # Business logic (project management, classification)
├── clients/          # API clients (OpenAI, future Ollama)
├── storage/          # Database models and persistence
└── cli/             # Command-line interface
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- pipenv (recommended) or pip
- OpenAI API key (for AI features)

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd survey-coder-modernized

# Install dependencies
pipenv install

# Activate virtual environment
pipenv shell

# Check installation
python -m coder_app status
```

### Basic Usage

```bash
# Create a new project
python -m coder_app project init --name "customer-feedback" --description "Analyze customer satisfaction" --question "How satisfied are you with our service?"

# List projects
python -m coder_app project list

# Show project details
python -m coder_app project show -n "customer-feedback"

# Load survey data
python -m coder_app project load-data -n "customer-feedback" -f "survey_data.csv"

# Import a codebook
python -m coder_app codebook import -p "customer-feedback" -f "codebook.json"

# Export project data
python -m coder_app export project-data -p "customer-feedback" -o "results.json"
```

## 💻 IDE Integration

### VS Code Support

The repository includes comprehensive VS Code integration:

- **Extensions**: Recommended Python development extensions
- **Tasks**: Pre-configured tasks for common operations
- **Snippets**: Survey coding snippets
- **Debug**: Launch configurations for development

#### Available VS Code Tasks

Access via `Ctrl+Shift+P` → "Tasks: Run Task":

- `Survey Coder: Create New Project`
- `Survey Coder: List Projects`
- `Survey Coder: Check Status`
- `Survey Coder: Export Project Data`
- `Survey Coder: Run Tests`
- `Survey Coder: Format Code`

#### IDE-Specific Commands

```bash
# Classify text with IDE-friendly JSON output
python -m coder_app ide classify-text -p "my-project" -t "Great service!" -f json

# Batch classify from file
python -m coder_app ide batch-classify -p "my-project" -i selections.txt -o results.json

# Export codebook as VS Code snippets
python -m coder_app ide export-codebook-for-ide -p "my-project" -f vscode-snippets
```

## 🗃️ Data Management

### Persistent Storage

Projects are stored in `~/.coder_app/projects.db` with:

- **Projects**: Metadata, questions, configuration
- **Codebooks**: Versioned codebooks with examples
- **Classifications**: Complete classification history

### Security

- API keys stored securely in environment variables
- Sensitive data excluded from git via comprehensive `.gitignore`
- Local-first processing with optional remote agent support

## 🔄 Upstream Synchronization

Stay updated with the original repository:

```bash
# Fetch upstream changes
git fetch upstream

# View what's new
git log --oneline HEAD..upstream/main

# Compare files
git diff upstream/main -- app.py

# Create sync branch
git checkout -b sync-upstream-$(date +%Y%m%d)
git merge upstream/main
```

## 📈 Development Roadmap

### Phase 1: Local Storage & Persistence ✅
- [x] SQLite database with SQLAlchemy
- [x] Project management CLI
- [x] Persistent codebook storage
- [x] Data export capabilities

### Phase 2: Multi-Agent Architecture (Next)
- [ ] Abstract LLM provider interface
- [ ] Ollama client implementation
- [ ] SSH tunnel management
- [ ] Agent coordination system

### Phase 3: Advanced IDE Integration
- [ ] Language Server Protocol (LSP)
- [ ] VS Code extension
- [ ] Real-time classification
- [ ] Command palette integration

### Phase 4: Hot Data & Adaptive Systems
- [ ] File system watching
- [ ] Streaming classification pipeline
- [ ] Adaptive codebook refinement
- [ ] Real-time dashboard

## 🧪 Testing

Run the test suite:

```bash
# Run comprehensive tests
python test_new_architecture.py

# Or via VS Code task
# Ctrl+Shift+P → "Tasks: Run Task" → "Survey Coder: Run Tests"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pipenv install --dev

# Format code
pipenv run black coder_app/

# Lint code
pipenv run flake8 coder_app/

# Type checking
pipenv run mypy coder_app/
```

## 🔐 Security

- **Never commit API keys** - Use environment variables
- **Survey data protection** - Excluded from git by default
- **Database security** - Local storage only
- **Upstream monitoring** - Track changes without exposing secrets

See [SECURITY.md](SECURITY.md) for detailed security guidelines.

## 📚 Documentation

- [WARP.md](WARP.md) - Complete development guide for AI assistants
- [SECURITY.md](SECURITY.md) - Security best practices
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Original Survey Coder by [pbagedelli](https://github.com/pbagedelli/coder-app)
- Built with OpenAI API for intelligent classification
- Powered by modern Python tooling (Pydantic, SQLAlchemy, Click)

---

**📬 Questions?** Open an issue or start a discussion!

**🚀 Ready to modernize your survey coding workflow?** Get started with the quick start guide above!