#!/bin/bash
# Claude Code Security Hook - Command Validator
# This script validates bash commands before execution to prevent dangerous operations

# ログファイルの設定
LOG_FILE=".claude/logs/security.log"
mkdir -p "$(dirname "$LOG_FILE")"

# 現在の日時を取得
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# 入力からJSONを読み取り
INPUT=$(cat)

# JSONからコマンドを抽出（簡易版）
COMMAND=$(echo "$INPUT" | grep -o '"command":"[^"]*"' | sed 's/"command":"//g' | sed 's/"$//g')

# 空のコマンドの場合は許可
if [ -z "$COMMAND" ]; then
    exit 0
fi

# 危険なコマンドパターンの定義
DANGEROUS_PATTERNS=(
    # システム破壊的コマンド
    "rm -rf /"
    "rm -rf ~/"
    "rm -rf \*"
    "chmod 777"
    "chmod -R 777"
    
    # 権限昇格
    "sudo"
    "su "
    
    # ネットワーク関連
    "curl"
    "wget"
    "nc "
    "netcat"
    
    # システム変更
    "systemctl"
    "service "
    "mount"
    "umount"
    "fdisk"
    "mkfs"
    "format"
    
    # プロセス制御
    "kill -9"
    "killall"
    "pkill"
    
    # スケジューリング
    "crontab"
    "at "
    "batch"
    
    # 危険なリダイレクト
    "> /etc/"
    ">> /etc/"
    "tee /etc/"
    
    # 実行系
    "eval "
    "exec "
    
    # パッケージ管理
    "apt install"
    "yum install"
    "brew install"
    "pip install"
    "npm install -g"
    
    # リモートアクセス
    "ssh.*rm"
    "ssh.*sudo"
    "scp.*:"
    "rsync.*:"
    
    # Git危険操作
    "git config --global"
    "gh repo delete"
    
    # バックグラウンド実行
    "nohup"
    "screen"
    "tmux"
    "&$"
)

# 警告レベルのコマンドパターン
WARNING_PATTERNS=(
    "git push.*force"
    "git push.*-f"
    "git reset --hard"
    "git clean -fd"
    "docker rm"
    "docker rmi"
    "npm uninstall"
    "pip uninstall"
)

# 情報レベルのコマンドパターン（推奨コマンドへの置換提案）
INFO_PATTERNS=(
    "grep"
    "find.*-name"
    "cat "
    "ls "
)

# 関数: ログ記録
log_security_event() {
    local level="$1"
    local message="$2"
    echo "[$TIMESTAMP] [$level] $message" >> "$LOG_FILE"
}

# 関数: 危険なコマンドチェック
check_dangerous_patterns() {
    for pattern in "${DANGEROUS_PATTERNS[@]}"; do
        if echo "$COMMAND" | grep -q "$pattern"; then
            log_security_event "BLOCKED" "Dangerous command blocked: $COMMAND (matched: $pattern)"
            echo "🚫 危険なコマンドが検出されました: $pattern" >&2
            echo "実行がブロックされました: $COMMAND" >&2
            echo '{"decision": "block", "reason": "危険なコマンドパターンが検出されました"}' >&1
            exit 2
        fi
    done
}

# 関数: 警告レベルのコマンドチェック
check_warning_patterns() {
    for pattern in "${WARNING_PATTERNS[@]}"; do
        if echo "$COMMAND" | grep -q "$pattern"; then
            log_security_event "WARNING" "Potentially dangerous command: $COMMAND (matched: $pattern)"
            echo "⚠️  注意が必要なコマンドです: $pattern" >&2
            echo "実行前に確認してください: $COMMAND" >&2
            # 警告だが実行は許可
            return 0
        fi
    done
}

# 関数: 情報レベルのコマンドチェック（推奨コマンド提案）
check_info_patterns() {
    case "$COMMAND" in
        *"grep"*)
            if ! echo "$COMMAND" | grep -q "rg"; then
                log_security_event "INFO" "Suggest using 'rg' instead of 'grep': $COMMAND"
                echo "💡 推奨: 'rg' (ripgrep) の使用を検討してください" >&2
            fi
            ;;
        *"find"*"-name"*)
            log_security_event "INFO" "Suggest using 'fd' instead of 'find': $COMMAND"
            echo "💡 推奨: 'fd' の使用を検討してください" >&2
            ;;
        *"cat "*)
            if ! echo "$COMMAND" | grep -q "batcat"; then
                log_security_event "INFO" "Suggest using 'batcat' instead of 'cat': $COMMAND"
                echo "💡 推奨: 'batcat' の使用を検討してください" >&2
            fi
            ;;
        *"ls "*)
            if ! echo "$COMMAND" | grep -q "eza"; then
                log_security_event "INFO" "Suggest using 'eza' instead of 'ls': $COMMAND"
                echo "💡 推奨: 'eza --icons --git' の使用を検討してください" >&2
            fi
            ;;
    esac
}

# 関数: ホワイトリストチェック
check_whitelist() {
    # 明示的に許可されたコマンドパターン
    local WHITELIST_PATTERNS=(
        "git status"
        "git log"
        "git diff"
        "git add"
        "git commit"
        "git push origin"
        "git pull"
        "npm run"
        "npm test"
        "python -m"
        "pip list"
        "docker ps"
        "docker logs"
        "ls -la"
        "pwd"
        "whoami"
        "date"
        "echo"
        "which"
        "command -v"
    )
    
    for pattern in "${WHITELIST_PATTERNS[@]}"; do
        if echo "$COMMAND" | grep -q "^$pattern"; then
            log_security_event "ALLOWED" "Whitelisted command: $COMMAND"
            return 0
        fi
    done
    
    return 1
}

# メイン処理
main() {
    # 空のコマンドは許可
    if [ -z "$COMMAND" ]; then
        exit 0
    fi
    
    # ホワイトリストチェック
    if check_whitelist; then
        exit 0
    fi
    
    # 危険なコマンドチェック
    check_dangerous_patterns
    
    # 警告レベルのコマンドチェック
    check_warning_patterns
    
    # 情報レベルのコマンドチェック
    check_info_patterns
    
    # デフォルトで許可（ログ記録）
    log_security_event "ALLOWED" "Command allowed: $COMMAND"
    exit 0
}

# スクリプト実行
main "$@"