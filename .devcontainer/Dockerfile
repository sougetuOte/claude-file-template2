# Dockerfile for advanced customization
# This file is optional - devcontainer.json uses the image directly by default

# Base image - Python 3.11 with common development tools
ARG VARIANT="3.11-bookworm"
FROM mcr.microsoft.com/devcontainers/python:${VARIANT}

# Install Node.js (if not using features)
# ARG NODE_VERSION="20"
# RUN curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash - \
#     && apt-get install -y nodejs

# Install additional OS packages
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
        # Database tools
        sqlite3 \
        libsqlite3-dev \
        # Search and text processing
        ripgrep \
        jq \
        # Build tools
        build-essential \
        cmake \
        # Network tools
        curl \
        wget \
        httpie \
        # System monitoring
        htop \
        ncdu \
        # File utilities
        tree \
        unzip \
        # Terminal enhancements
        tmux \
        # Documentation tools
        pandoc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install global Python packages (optional)
# RUN pip3 install --no-cache-dir \
#     jupyter \
#     notebook \
#     jupyterlab

# Install Claude Code CLI (when available)
# RUN curl -sSL https://claude.ai/install.sh | bash

# Set up custom shell configuration
COPY --chown=vscode:vscode shell-config/.zshrc /home/vscode/.zshrc
COPY --chown=vscode:vscode shell-config/.bashrc /home/vscode/.bashrc

# Create project directories
RUN mkdir -p /workspace/.claude/logs \
    && mkdir -p /workspace/.claude/cache \
    && chown -R vscode:vscode /workspace

# Install custom tools or scripts
# COPY --chown=vscode:vscode scripts/ /usr/local/bin/
# RUN chmod +x /usr/local/bin/*

# Configure git (optional - can be done in post-create)
# RUN git config --global init.defaultBranch main \
#     && git config --global pull.rebase false

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    CLAUDE_HOOKS_ENABLED=true \
    CLAUDE_MEMORY_BANK_OPTIMIZED=true

# Switch to non-root user
USER vscode

# Pre-install Python packages in user space
RUN pip install --user \
    black \
    flake8 \
    mypy \
    pytest \
    pytest-cov \
    ipython \
    rich \
    click \
    pyyaml

# Optional: Pre-build or cache heavy dependencies
# WORKDIR /tmp/prebuild
# COPY requirements.txt* pyproject.toml* ./
# RUN pip install --user -r requirements.txt || true
# WORKDIR /workspace

# Set the default shell
SHELL ["/bin/zsh", "-c"]

# Default command
CMD ["sleep", "infinity"]