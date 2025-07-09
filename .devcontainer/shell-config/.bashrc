# DevContainer Bash Configuration

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

# Auto-sync on directory change (Bash version)
PROMPT_COMMAND='check_claude_sync'

check_claude_sync() {
    if [[ "$PWD" == *"/.claude"* ]] && [ -f ".claude/index/sync_markdown.py" ]; then
        # Only sync if directory changed
        if [ "$PWD" != "$LAST_PWD" ]; then
            echo "📝 Syncing Memory Bank..."
            python3 .claude/index/sync_markdown.py incremental >/dev/null 2>&1 &
            export LAST_PWD="$PWD"
        fi
    fi
}

# Display welcome message
if [ -f ~/.motd ]; then
    cat ~/.motd
fi

# Set prompt
PS1='🐳 \[\033[36m\]\u@devcontainer\[\033[0m\] \[\033[33m\]\w\[\033[0m\] \[\033[32m\]❯\[\033[0m\] '

# Enable command history
HISTFILE=~/.bash_history
HISTSIZE=10000
HISTFILESIZE=10000
HISTCONTROL=ignoredups:ignorespace

# Append to history instead of overwriting
shopt -s histappend

# Check window size after each command
shopt -s checkwinsize

# Path additions
export PATH="$HOME/.local/bin:$PATH"
export PYTHONPATH="${PYTHONPATH}:${PWD}/.claude"

# Enable bash completion
if [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
fi

# Load local overrides if they exist
if [ -f ~/.bashrc.local ]; then
    source ~/.bashrc.local
fi