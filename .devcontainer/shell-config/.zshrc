# DevContainer Zsh Configuration

# Oh My Zsh configuration (if installed)
if [ -d "$HOME/.oh-my-zsh" ]; then
    export ZSH="$HOME/.oh-my-zsh"
    ZSH_THEME="robbyrussell"
    plugins=(git python node docker vscode)
    source $ZSH/oh-my-zsh.sh
fi

# Aliases for Claude File Template
alias k="python3 .claude/commands/k_command.py"
alias ksearch="python3 .claude/commands/k_command.py search"
alias ksync="python3 .claude/index/sync_markdown.py"
alias kinfo="python3 .claude/index/sync_markdown.py info"

# Project shortcuts
alias plan="/project:plan"
alias daily="/project:daily"
alias focus="/project:focus"
alias act="/project:act"

# Development aliases
alias ll="ls -la"
alias py="python3"
alias pytest="python3 -m pytest"
alias black="python3 -m black"
alias mypy="python3 -m mypy"

# Git aliases
alias gs="git status"
alias gd="git diff"
alias ga="git add"
alias gc="git commit"
alias gp="git push"
alias gl="git log --oneline -10"

# Docker aliases
alias ds="docker stats"
alias dps="docker ps"
alias dclean="docker system prune -f"

# Navigation helpers
alias ..="cd .."
alias ...="cd ../.."
alias claude="cd .claude"
alias core="cd .claude/core"
alias context="cd .claude/context"

# Environment info function
devinfo() {
    echo "🐳 DevContainer Environment Info"
    echo "================================"
    echo "Python: $(python3 --version)"
    echo "Node: $(node --version)"
    echo "Git: $(git --version | cut -d' ' -f3)"
    echo "SQLite: $(sqlite3 --version | cut -d' ' -f1)"
    echo "User: $USER"
    echo "Workspace: $PWD"
    echo "Memory Bank: $(python3 .claude/index/sync_markdown.py info 2>/dev/null | grep 'Total entries' || echo 'Not initialized')"
}

# Quick Memory Bank search function
ks() {
    if [ -z "$1" ]; then
        echo "Usage: ks <search term>"
        return 1
    fi
    python3 .claude/commands/k_command.py search "$@"
}

# Auto-sync on directory change
autoload -U add-zsh-hook
add-zsh-hook chpwd check_claude_sync

check_claude_sync() {
    if [[ "$PWD" == *"/.claude"* ]] && [ -f ".claude/index/sync_markdown.py" ]; then
        echo "📝 Syncing Memory Bank..."
        python3 .claude/index/sync_markdown.py incremental >/dev/null 2>&1 &
    fi
}

# Display welcome message
if [ -f ~/.motd ]; then
    cat ~/.motd
fi

# Set prompt
PROMPT='🐳 %F{cyan}%n@devcontainer%f %F{yellow}%~%f %F{green}❯%f '

# Enable command history
HISTFILE=~/.zsh_history
HISTSIZE=10000
SAVEHIST=10000
setopt SHARE_HISTORY

# Path additions
export PATH="$HOME/.local/bin:$PATH"
export PYTHONPATH="${PYTHONPATH}:${PWD}/.claude"

# Load local overrides if they exist
if [ -f ~/.zshrc.local ]; then
    source ~/.zshrc.local
fi