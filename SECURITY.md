# Security Guidelines

## 🔐 Overview

Survey Coder handles sensitive data including API keys, survey responses, and classification results. This document outlines security best practices and guidelines.

## 🗝️ API Key Management

### Environment Variables (Recommended)

```bash
# Set OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# Or create .env file (excluded from git)
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

### What NOT to do

❌ **Never commit API keys to git**
❌ **Don't hardcode keys in source code**
❌ **Avoid storing keys in plain text files tracked by git**

### Secure Storage Options

1. **Environment Variables** - Recommended for development
2. **System Keyring** - For production deployments
3. **Encrypted Configuration Files** - Advanced use cases

## 📊 Survey Data Protection

### Data Classification

- **Public**: Sample data, documentation
- **Internal**: Project metadata, codebook structures  
- **Confidential**: Survey responses, classification results
- **Restricted**: API keys, authentication tokens

### Storage Security

- **Local Database**: Stored in `~/.coder_app/` with restricted permissions
- **File Exclusions**: Comprehensive `.gitignore` excludes sensitive files
- **Data Exports**: Review before sharing outside organization

### Git Protection

The `.gitignore` file protects:

```
# API Keys
*.key
.env
.env.*
OPENAI_API_KEY

# Survey Data
*.csv
*.xlsx
survey_data/
responses/

# Results
results/
*_classified.csv
*_export.*

# Database
*.db
.coder_app/
```

## 🌐 Network Security

### API Communications

- **HTTPS Only**: All API communications use TLS
- **API Key Headers**: Securely transmitted in request headers
- **No Logging**: API keys never logged or printed

### Remote Agents (Future)

When multi-agent support is added:

- **SSH Tunnels**: All remote communications through encrypted SSH
- **Key-based Authentication**: No password authentication
- **Agent Isolation**: Each agent runs in isolated environment

## 🖥️ Local Security

### File Permissions

```bash
# Restrict database access
chmod 600 ~/.coder_app/projects.db

# Secure configuration directory
chmod 700 ~/.coder_app/
```

### Development Environment

- **Virtual Environment**: Use pipenv or venv for isolation
- **Dependency Scanning**: Regularly update dependencies
- **Code Review**: Review changes before deployment

## 🚨 Incident Response

### Data Breach Response

1. **Immediate Actions**:
   - Rotate affected API keys
   - Review access logs
   - Identify scope of exposure

2. **Assessment**:
   - Determine what data was accessed
   - Check for unauthorized API usage
   - Review system logs

3. **Recovery**:
   - Update security measures
   - Re-encrypt sensitive data
   - Update documentation

### API Key Compromise

```bash
# Immediately revoke old key from OpenAI dashboard
# Generate new API key
# Update environment variables
export OPENAI_API_KEY="new-api-key-here"

# Verify new key works
python -m coder_app status
```

## 📋 Security Checklist

### Before Development

- [ ] Install pipenv/venv for environment isolation
- [ ] Set up API keys in environment variables
- [ ] Review .gitignore exclusions
- [ ] Configure file permissions

### Before Commits

- [ ] No API keys in code or config files
- [ ] No sensitive survey data included
- [ ] No database files committed
- [ ] Security-sensitive changes reviewed

### Before Production

- [ ] Secure API key storage implemented
- [ ] Database access restricted
- [ ] Network communications encrypted
- [ ] Backup and recovery tested

## 🔍 Security Monitoring

### Regular Reviews

- **Monthly**: Review API key usage and costs
- **Quarterly**: Update dependencies and scan for vulnerabilities
- **Annually**: Complete security assessment

### Monitoring Tools

```bash
# Check for exposed secrets
pipenv check

# Audit dependencies
pipenv run safety check

# Scan for security issues
pipenv run bandit -r coder_app/
```

## 📞 Reporting Security Issues

If you discover a security vulnerability:

1. **Do NOT** create a public issue
2. Email security concerns to [maintainer email]
3. Include steps to reproduce
4. Allow time for response before disclosure

## 📚 Additional Resources

- [OpenAI API Security Best Practices](https://platform.openai.com/docs/guides/safety-best-practices)
- [Python Security Best Practices](https://python.org/dev/security/)
- [Git Security Guidelines](https://git-scm.com/book/en/v2/Git-Tools-Signing-Your-Work)

---

**Remember**: Security is everyone's responsibility. When in doubt, choose the more secure option.