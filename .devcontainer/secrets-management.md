# DevContainer Secrets Management Guide

## Overview
This guide explains how to securely manage secrets and sensitive information in your devcontainer environment.

## Environment Variables

### Local Development
1. Copy `.env.example` to `.env` in the `.devcontainer` directory
2. Fill in your actual values
3. Never commit `.env` to version control

### VS Code Integration
DevContainer automatically loads environment variables from:
- `.devcontainer/.env` (local, gitignored)
- `.devcontainer/devcontainer.env` (shared, committed)
- Host environment variables (selectively)

## Secrets Storage Options

### 1. Local .env File (Recommended for Development)
```bash
cp .devcontainer/.env.example .devcontainer/.env
# Edit .env with your values
```

### 2. VS Code User Secrets
Store in VS Code settings.json (user level):
```json
{
  "remote.containers.defaultExtensions": [],
  "remote.containers.env": {
    "MY_SECRET": "value"
  }
}
```

### 3. System Keychain Integration
For macOS/Linux:
```bash
# Store secret
security add-generic-password -a "$USER" -s "project-secret" -w "secret-value"

# Retrieve in devcontainer
export MY_SECRET=$(security find-generic-password -a "$USER" -s "project-secret" -w)
```

### 4. Docker Secrets (Production-like)
Create docker secret:
```bash
echo "my-secret-value" | docker secret create my_secret -
```

Reference in devcontainer.json:
```json
{
  "runArgs": ["--secret", "my_secret"]
}
```

## SSH Keys

### Automatic SSH Agent Forwarding
The devcontainer is configured to mount your SSH keys read-only:
```json
"mounts": [
  "source=${localEnv:HOME}/.ssh,target=/home/vscode/.ssh,type=bind,consistency=cached,readonly"
]
```

### Manual SSH Key Setup
If automatic mounting doesn't work:
```bash
# Inside devcontainer
mkdir -p ~/.ssh
cp /host-ssh/id_rsa ~/.ssh/
chmod 600 ~/.ssh/id_rsa
```

## GPG Keys

### GPG Signing for Git
```bash
# Export from host
gpg --export-secret-keys YOUR_KEY_ID > private.key

# Import in container
gpg --import private.key
git config --global user.signingkey YOUR_KEY_ID
```

## Best Practices

### DO:
- ✅ Use `.env` files for local development
- ✅ Use environment variable references in code
- ✅ Rotate secrets regularly
- ✅ Use different secrets for different environments
- ✅ Document required environment variables

### DON'T:
- ❌ Hardcode secrets in source code
- ❌ Commit `.env` files
- ❌ Share secrets in plain text
- ❌ Use production secrets in development
- ❌ Store secrets in Docker images

## Security Checklist

- [ ] `.env` is in `.gitignore`
- [ ] No secrets in `devcontainer.json`
- [ ] SSH keys are mounted read-only
- [ ] Secrets are environment-specific
- [ ] Documentation lists required variables
- [ ] Team knows how to set up secrets

## Troubleshooting

### Environment Variable Not Available
1. Check if defined in `.env`
2. Rebuild container: `Dev Containers: Rebuild Container`
3. Check devcontainer.json `containerEnv` section

### SSH Key Permission Denied
```bash
# Fix permissions
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub
```

### Secret Rotation
When rotating secrets:
1. Update `.env` file
2. Rebuild container
3. Verify new secrets work
4. Remove old secrets

## Tools for Secret Management

### Development
- **direnv**: Auto-load env vars per directory
- **dotenv**: Load .env files in applications
- **chamber**: AWS Parameter Store integration

### Production
- **HashiCorp Vault**: Enterprise secret management
- **AWS Secrets Manager**: Cloud-native secrets
- **Azure Key Vault**: Azure integrated secrets
- **Kubernetes Secrets**: K8s native secrets

## Example: Complete Setup

1. **Create .env file:**
```bash
cd .devcontainer
cp .env.example .env
# Edit .env with your editor
```

2. **Update .gitignore:**
```bash
echo ".devcontainer/.env" >> ../.gitignore
```

3. **Test in container:**
```bash
# Rebuild and enter container
# In container terminal:
echo $CLAUDE_HOOKS_ENABLED  # Should show 'true'
```

## References
- [VS Code DevContainer Docs](https://code.visualstudio.com/docs/devcontainers/containers)
- [Docker Secrets](https://docs.docker.com/engine/swarm/secrets/)
- [12-Factor App Config](https://12factor.net/config)