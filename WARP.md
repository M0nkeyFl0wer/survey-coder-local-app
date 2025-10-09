# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

The Survey Coder is an intelligent AI-powered application for generating, refining, and applying codebooks to survey data. Currently implemented as a Streamlit web application, it uses OpenAI's API for natural language processing tasks including codebook generation, text classification, and semantic clustering.

**Current State**: Streamlit-based web application with session-based state management
**Target State**: Local, persistent, multi-agent capable system integrated with IDE workflows

## Development Commands

### Current Environment Setup
```bash
# Install dependencies using pipenv
pipenv install

# Activate virtual environment  
pipenv shell

# Run the current Streamlit application
streamlit run app.py

# Alternative: Run with specific port
streamlit run app.py --server.port 8501
```

### Development Workflow
```bash
# Check Python version compatibility
python --version  # Should be 3.13+

# Install additional development tools
pipenv install --dev pytest black flake8

# Run linting
flake8 app.py

# Format code
black app.py

# Basic testing (when tests are added)
pytest
```

## Current Architecture

### Core Components

1. **Streamlit UI Layer** (`app.py` lines 1-1161)
   - Session state management via `st.session_state`
   - Multi-step workflow: Setup → Configure → Generate/Refine → Test → Classify
   - File upload/download capabilities
   - Progress tracking and async processing

2. **OpenAI Integration**
   - Structured output using Pydantic models
   - Batch processing with concurrent API calls
   - Token estimation and cost optimization
   - Embedding generation for semantic clustering

3. **Data Processing Pipeline**
   - CSV/Excel file ingestion
   - Text preprocessing and validation
   - Semantic clustering using DBSCAN
   - Multi-label and single-label classification
   - Export formats: CSV, Excel, One-Hot encoded

4. **Codebook Management**
   - JSON and CSV import/export
   - Interactive editing interface
   - Merge capabilities between codebooks
   - Automatic refinement with new samples

### Key Data Models (Pydantic)

- `Code`: Individual code with label, description, examples
- `Codebook`: Collection of codes
- `ClassificationOutput`: Results with evidence and pertinence scores
- `BatchItem`/`BatchClassificationOutput`: Batch processing results

### Processing Flow

1. **Data Upload** → Validation → Column Selection
2. **Codebook Generation** → Interactive Editing → Refinement
3. **Classification** → Semantic Clustering → Batch Processing
4. **Results Export** → Multiple formats with frequency analysis

## Modernization Roadmap

### Phase 1: Local Storage & Persistence

**Goal**: Replace Streamlit session state with persistent local storage

**Key Changes**:
- Implement SQLite database for project persistence
- Add file-based configuration management
- Create local data directories structure
- Implement project versioning and history

**Commands to add**:
```bash
# Initialize new project
python -m coder_app init --name "project_name" --description "desc"

# Load existing project
python -m coder_app load --project "project_name"

# List projects
python -m coder_app list

# Export project data
python -m coder_app export --project "project_name" --format json|csv
```

### Phase 2: Multi-Agent Architecture

**Goal**: Support multiple agents via SSH/Ollama tunnels

**Key Changes**:
- Abstract OpenAI client into provider interface
- Add Ollama client implementation
- Implement agent coordination and task distribution
- Add SSH tunnel management for remote agents

**Architecture Components**:
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Local Agent   │    │  Coordination    │    │  Remote Agent   │
│  (Primary)     │◄──►│  Manager         │◄──►│  (Via SSH/      │
│                │    │                  │    │   Ollama)       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

**Commands to add**:
```bash
# Configure remote agent
python -m coder_app agent add --name "agent1" --host "remote.host" --port 11434

# List available agents  
python -m coder_app agent list

# Run classification with specific agent
python -m coder_app classify --agent "agent1" --project "project_name"

# Distribute work across agents
python -m coder_app classify --distribute --agents "agent1,agent2"
```

### Phase 3: IDE Integration

**Goal**: Seamless integration with VS Code, Cursor, and other IDEs

**Key Changes**:
- Language Server Protocol (LSP) implementation
- VS Code extension
- Command palette integration
- Hot reload capabilities for codebooks

**IDE Commands**:
- `Coder: Initialize Project`
- `Coder: Generate Codebook`  
- `Coder: Classify Selection`
- `Coder: View Results Dashboard`

### Phase 4: Hot Data Outputs & Code Books

**Goal**: Real-time data analysis and adaptive codebooks

**Key Changes**:
- Real-time file watching for new data
- Streaming classification pipeline
- Adaptive codebook refinement
- Interactive data exploration interface

## Important Project-Specific Patterns

### Async Processing Pattern
The application uses ThreadPoolExecutor for concurrent API calls:
```python
with ThreadPoolExecutor(max_workers=MAX_CONCURRENCY) as executor:
    future_to_idx = {executor.submit(worker, i, b): i for i, b in enumerate(batches)}
    for future in as_completed(future_to_idx):
        # Process results
```

### Semantic Clustering Optimization
DBSCAN clustering reduces API calls by grouping similar responses:
```python
# Generate embeddings → Cluster → Classify representatives → Apply to clusters
embeddings = get_embeddings(unique_responses, api_key)
db = DBSCAN(eps=0.3, min_samples=2, metric='cosine').fit(embeddings)
```

### Token Estimation Strategy
Proactive token estimation prevents API cost surprises:
```python
est_tokens = estimate_chat_tokens(system_prompt, user_prompt, model)
```

## Critical Dependencies

### Core Libraries
- `streamlit`: Web interface (to be replaced)
- `pandas`: Data manipulation
- `openai`: API client
- `pydantic`: Data validation and structured outputs
- `scikit-learn`: Clustering algorithms
- `tiktoken`: Token counting

### Target Dependencies for Modernization
- `sqlalchemy`: Database ORM
- `fastapi`: API framework for multi-agent coordination
- `watchdog`: File system monitoring
- `paramiko`: SSH connections for remote agents
- `ollama`: Local LLM integration
- `click`: Command-line interface

## Data Persistence Strategy

### Current State (Session-based)
- All data stored in `st.session_state`
- Lost on browser refresh/restart
- No project management capabilities

### Target State (Local Database)
```sql
-- Projects table
CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    description TEXT,
    created_at TIMESTAMP,
    last_modified TIMESTAMP
);

-- Codebooks table  
CREATE TABLE codebooks (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    version INTEGER,
    data JSON,
    created_at TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects (id)
);

-- Classifications table
CREATE TABLE classifications (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    codebook_id INTEGER,
    response_text TEXT,
    assigned_codes JSON,
    details JSON,
    created_at TIMESTAMP
);
```

## Security Considerations

### API Key Management
- Store API keys in environment variables or secure keyring
- Implement key rotation capabilities
- Support multiple provider configurations

### Data Privacy
- All data processing happens locally by default
- Option to use remote agents for distributed processing
- Ensure no sensitive data in logs or temporary files

## Testing Strategy

### Current Gap
- No automated tests exist
- Manual testing through Streamlit interface

### Target Testing Framework
```bash
# Unit tests for core functions
pytest tests/test_codebook.py
pytest tests/test_classification.py

# Integration tests for API clients
pytest tests/test_openai_client.py
pytest tests/test_ollama_client.py

# End-to-end workflow tests
pytest tests/test_workflow.py --slow
```

## Migration Path

### Step 1: Extract Core Logic
```bash
# Refactor app.py into modular components
mkdir coder_app/{models,services,clients,storage}

# Move Pydantic models
mv # models section → coder_app/models/

# Extract API clients
# Extract storage layer
# Extract business logic
```

### Step 2: Add CLI Interface
```bash
# Create CLI entry point
touch coder_app/cli.py

# Add project management commands
# Add data processing commands
# Add agent management commands
```

### Step 3: Implement Persistence
```bash
# Add database models
# Implement project CRUD operations
# Add data export/import
# Create migration scripts
```

### Step 4: Multi-Agent Support
```bash
# Abstract LLM providers
# Implement agent registry
# Add coordination logic
# Create SSH tunnel management
```

## Performance Optimization

### Current Bottlenecks
- Sequential API calls for individual responses
- Memory usage for large datasets
- No caching of embeddings or classifications

### Optimization Targets
- Implement result caching with TTL
- Add streaming processing for large files
- Use connection pooling for API clients
- Implement incremental processing

## Common Development Tasks

### Adding New LLM Provider
1. Create provider class implementing `LLMProvider` interface
2. Add configuration schema
3. Update agent registry
4. Add tests for provider-specific functionality

### Extending Classification Models
1. Define new Pydantic output model
2. Update prompt templates
3. Add model-specific parsing logic
4. Update export formats

### Adding New Export Format
1. Create exporter class implementing `DataExporter`
2. Add format-specific serialization logic  
3. Update download handlers
4. Add format validation

## Troubleshooting

### Common Issues
- **API Rate Limits**: Implement exponential backoff
- **Memory Issues**: Use streaming processing for large datasets
- **SSH Connection Failures**: Add connection retry logic with timeout
- **Token Estimation Errors**: Fallback to character-based estimation

### Debug Commands
```bash
# Enable verbose logging
export CODER_LOG_LEVEL=DEBUG

# Test API connectivity
python -m coder_app test --provider openai|ollama

# Validate project data
python -m coder_app validate --project "project_name"

# Check agent connectivity
python -m coder_app agent test --name "agent1"
```

## Upstream Synchronization Strategy

### Monitoring Upstream Changes

**Repository**: `https://github.com/pbagedelli/coder-app`

To stay synchronized with upstream development while maintaining our modernization:

```bash
# Add upstream remote (one-time setup)
git remote add upstream https://github.com/pbagedelli/coder-app.git

# Check current remotes
git remote -v

# Fetch latest changes from upstream
git fetch upstream

# View changes in upstream
git log --oneline HEAD..upstream/main

# Compare current app.py with upstream
git diff upstream/main -- app.py

# Create sync branch for testing upstream changes
git checkout -b sync-upstream-$(date +%Y%m%d)
git merge upstream/main
```

### Automated Sync Workflow

```bash
# Daily sync check (add to cron)
#!/bin/bash
# File: scripts/check-upstream.sh
cd /home/flower/coder-app
git fetch upstream
if ! git diff --quiet HEAD upstream/main; then
    echo "Upstream changes detected!"
    git log --oneline HEAD..upstream/main
    # Send notification or create issue
fi
```

### Feature Migration Process

1. **Detect Changes**: Monitor upstream for new features/fixes
2. **Analyze Impact**: Review changes against modernized architecture  
3. **Extract Core Logic**: Identify business logic vs. UI changes
4. **Adapt to New Architecture**: Implement in modular, persistent system
5. **Test Compatibility**: Ensure feature works in both modes

### Sync Commands to Add

```bash
# Compare upstream changes
python -m coder_app sync --check

# Import specific upstream feature
python -m coder_app sync --import-feature "classification_improvements"

# Generate migration report
python -m coder_app sync --report --since "2025-01-01"
```

This modernization roadmap maintains the core functionality while evolving toward a more robust, scalable, and IDE-integrated solution that supports your multi-agent workflow requirements.
