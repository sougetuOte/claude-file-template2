#!/bin/bash
set -e

echo "🔧 Setting up development environment..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${BLUE}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Update package list
print_step "Updating package list..."
sudo apt-get update -qq

# Install system dependencies
print_step "Installing system dependencies..."
sudo apt-get install -y -qq \
    sqlite3 \
    libsqlite3-dev \
    ripgrep \
    jq \
    tree \
    curl \
    wget \
    build-essential \
    python3-dev

print_success "System dependencies installed"

# Install Python development tools
print_step "Installing Python development tools..."
pip install --user --upgrade pip setuptools wheel
pip install --user \
    black \
    flake8 \
    mypy \
    pytest \
    pytest-cov \
    ipython \
    rich

# Install vibe-logger (optional AI-optimized logging)
pip install --user vibelogger || print_warning "vibelogger installation failed (optional)"

print_success "Python tools installed"

# Setup Node.js environment for MCP server
if [ -f ".claude/mcp/memory-server/package.json" ]; then
    print_step "Setting up MCP Memory Server..."
    cd .claude/mcp/memory-server
    npm install
    npm run build || print_warning "MCP server build failed (optional component)"
    cd - > /dev/null
    print_success "MCP server configured"
fi

# Install vibe-logger for Node.js/TypeScript (optional)
print_step "Installing vibe-logger for Node.js..."
npm install -g vibelogger || print_warning "vibelogger npm installation failed (optional)"

# Initialize Memory Bank database
print_step "Initializing Memory Bank..."
python3 -c "
import sys
sys.path.insert(0, '.claude')
try:
    from index.OptimizedKnowledgeStore import OptimizedKnowledgeStore
    store = OptimizedKnowledgeStore()
    print('✓ Memory Bank database initialized')
except Exception as e:
    print(f'⚠ Memory Bank initialization failed: {e}')
    print('  This is optional - you can initialize it later')
"

# Create necessary directories
print_step "Creating project directories..."
mkdir -p .claude/logs
mkdir -p .claude/archive
mkdir -p .claude/index
mkdir -p .claude/cache

# Set permissions
chmod +x .claude/scripts/*.py 2>/dev/null || true
chmod +x .claude/commands/*.py 2>/dev/null || true

# Initialize git hooks (if not already initialized)
if [ -d ".git" ]; then
    print_step "Configuring git..."
    git config --local core.autocrlf input
    git config --local core.eol lf
    print_success "Git configured"
fi

# Create initial sync timestamp file
touch .claude/index/.last_sync_times

# Run initial Memory Bank sync
print_step "Running initial Memory Bank sync..."
if [ -f ".claude/index/sync_markdown.py" ]; then
    python3 .claude/index/sync_markdown.py smart || print_warning "Initial sync failed (can be run manually later)"
fi

# Claude Code CLI check
print_step "Checking for Claude Code CLI..."
if command -v claude &> /dev/null; then
    claude --version
    print_success "Claude Code CLI is available"
else
    print_warning "Claude Code CLI not found. Install instructions:"
    echo "  Visit: https://docs.anthropic.com/en/docs/claude-code/quickstart"
    echo "  Or run: curl -sSL https://claude.ai/install.sh | bash"
fi

# Create welcome message
cat > ~/.motd << 'EOF'
╔═══════════════════════════════════════════════════════════════╗
║           🚀 Claude File Template DevContainer Ready!          ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  Quick Commands:                                              ║
║  • claude --help         : Claude Code CLI help              ║
║  • python3 .claude/commands/k_command.py : Knowledge manager  ║
║  • /k search [query]     : Search knowledge base             ║
║  • /project:plan         : Plan your work                    ║
║  • /project:daily        : Daily standup                     ║
║                                                               ║
║  Memory Bank Sync:                                            ║
║  • python3 .claude/index/sync_markdown.py incremental        ║
║  • python3 .claude/index/sync_markdown.py smart              ║
║                                                               ║
║  Documentation:                                               ║
║  • CLAUDE.md            : Project overview                   ║
║  • .claude/core/        : Current status & plans             ║
║  • .claude/guidelines/  : Development guidelines             ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF

# Display welcome message
cat ~/.motd

# Final success message
echo ""
print_success "Development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. If Claude Code CLI is not installed, follow the installation instructions above"
echo "2. Review CLAUDE.md for project-specific setup"
echo "3. Run 'python3 .claude/index/sync_markdown.py smart' to sync knowledge base"
echo ""