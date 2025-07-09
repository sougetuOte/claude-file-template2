#!/usr/bin/env python3
"""
Claude Code Security Hook - Bash Command Validator
This script validates bash commands before execution to prevent dangerous operations.
Based on the official example from anthropics/claude-code repository.
"""

import json
import re
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# ログ設定
LOG_FILE = Path(".claude/logs/security.log")
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

class SecurityLevel:
    """セキュリティレベルの定義"""
    BLOCK = "block"
    WARNING = "warning"
    INFO = "info"
    ALLOW = "allow"

class CommandValidator:
    """コマンドセキュリティバリデーター"""
    
    def __init__(self):
        self.dangerous_patterns = [
            # システム破壊的コマンド
            (r"rm\s+-rf\s+/", "ルートディレクトリの削除は危険です"),
            (r"rm\s+-rf\s+~", "ホームディレクトリの削除は危険です"),
            (r"rm\s+-rf\s+\*", "全ファイルの削除は危険です"),
            (r"chmod\s+777", "全権限付与は危険です"),
            (r"chmod\s+-R\s+777", "再帰的な全権限付与は危険です"),
            
            # 権限昇格
            (r"^sudo\s+", "sudo コマンドは制限されています"),
            (r"^su\s+", "su コマンドは制限されています"),
            
            # ネットワーク関連
            (r"^curl\s+", "curl による外部アクセスは制限されています"),
            (r"^wget\s+", "wget による外部アクセスは制限されています"),
            (r"^nc\s+", "netcat の使用は制限されています"),
            (r"^netcat\s+", "netcat の使用は制限されています"),
            
            # システム変更
            (r"^systemctl\s+", "systemctl の使用は制限されています"),
            (r"^service\s+", "service コマンドの使用は制限されています"),
            (r"^mount\s+", "mount コマンドの使用は制限されています"),
            (r"^umount\s+", "umount コマンドの使用は制限されています"),
            (r"^fdisk\s+", "fdisk の使用は制限されています"),
            (r"^mkfs\.", "ファイルシステム作成は制限されています"),
            (r"^format\s+", "format コマンドの使用は制限されています"),
            
            # プロセス制御
            (r"kill\s+-9", "強制終了は制限されています"),
            (r"^killall\s+", "killall の使用は制限されています"),
            (r"^pkill\s+", "pkill の使用は制限されています"),
            
            # スケジューリング
            (r"^crontab\s+", "crontab の編集は制限されています"),
            (r"^at\s+", "at コマンドの使用は制限されています"),
            (r"^batch\s+", "batch コマンドの使用は制限されています"),
            
            # 危険なリダイレクト
            (r">\s*/etc/", "/etc/ への書き込みは制限されています"),
            (r">>\s*/etc/", "/etc/ への追記は制限されています"),
            (r"tee\s+/etc/", "/etc/ への書き込みは制限されています"),
            
            # 実行系
            (r"^eval\s+", "eval の使用は制限されています"),
            (r"^exec\s+", "exec の使用は制限されています"),
            
            # パッケージ管理
            (r"^apt\s+install", "apt install の使用は制限されています"),
            (r"^yum\s+install", "yum install の使用は制限されています"),
            (r"^brew\s+install", "brew install の使用は制限されています"),
            (r"^pip\s+install", "pip install の使用は制限されています"),
            (r"^npm\s+install\s+-g", "npm グローバルインストールは制限されています"),
            
            # リモートアクセス
            (r"ssh\s+.*\s+rm", "SSH経由での削除は制限されています"),
            (r"ssh\s+.*\s+sudo", "SSH経由でのsudoは制限されています"),
            (r"scp\s+.*:", "SCP による転送は制限されています"),
            (r"rsync\s+.*:", "rsync による転送は制限されています"),
            
            # Git危険操作
            (r"git\s+config\s+--global", "git グローバル設定変更は制限されています"),
            (r"gh\s+repo\s+delete", "GitHub リポジトリ削除は制限されています"),
            
            # バックグラウンド実行
            (r"^nohup\s+", "nohup の使用は制限されています"),
            (r"^screen\s+", "screen の使用は制限されています"),
            (r"^tmux\s+", "tmux の使用は制限されています"),
            (r"&\s*$", "バックグラウンド実行は制限されています"),
        ]
        
        self.warning_patterns = [
            (r"git\s+push\s+.*--force", "git push --force は危険です"),
            (r"git\s+push\s+.*-f", "git push -f は危険です"),
            (r"git\s+reset\s+--hard", "git reset --hard は変更を破棄します"),
            (r"git\s+clean\s+-fd", "git clean -fd は追跡外ファイルを削除します"),
            (r"docker\s+rm", "Docker コンテナの削除です"),
            (r"docker\s+rmi", "Docker イメージの削除です"),
            (r"npm\s+uninstall", "npm パッケージの削除です"),
            (r"pip\s+uninstall", "pip パッケージの削除です"),
        ]
        
        self.improvement_suggestions = [
            (r"^grep\b(?!.*rg)", "rg (ripgrep) の使用を推奨します"),
            (r"^find\s+.*-name", "fd コマンドの使用を推奨します"),
            (r"^cat\s+(?!.*batcat)", "batcat の使用を推奨します"),
            (r"^ls\s+(?!.*eza)", "eza --icons --git の使用を推奨します"),
        ]
        
        self.whitelist_patterns = [
            r"^git\s+status",
            r"^git\s+log",
            r"^git\s+diff",
            r"^git\s+add",
            r"^git\s+commit",
            r"^git\s+push\s+origin",
            r"^git\s+pull",
            r"^npm\s+run",
            r"^npm\s+test",
            r"^python\s+-m",
            r"^pip\s+list",
            r"^docker\s+ps",
            r"^docker\s+logs",
            r"^ls\s+-la",
            r"^pwd",
            r"^whoami",
            r"^date",
            r"^echo",
            r"^which",
            r"^command\s+-v",
        ]
    
    def validate_command(self, command: str) -> Tuple[str, List[str]]:
        """
        コマンドを検証する
        
        Args:
            command: 検証するコマンド
            
        Returns:
            (security_level, messages): セキュリティレベルとメッセージのリスト
        """
        messages = []
        
        if not command or not command.strip():
            return SecurityLevel.ALLOW, messages
        
        # ホワイトリストチェック
        for pattern in self.whitelist_patterns:
            if re.search(pattern, command):
                logger.info(f"Whitelisted command: {command}")
                return SecurityLevel.ALLOW, messages
        
        # 危険なパターンチェック
        for pattern, message in self.dangerous_patterns:
            if re.search(pattern, command):
                logger.warning(f"Dangerous command blocked: {command} (matched: {pattern})")
                messages.append(f"🚫 {message}")
                return SecurityLevel.BLOCK, messages
        
        # 警告パターンチェック
        for pattern, message in self.warning_patterns:
            if re.search(pattern, command):
                logger.warning(f"Warning command: {command} (matched: {pattern})")
                messages.append(f"⚠️ {message}")
                return SecurityLevel.WARNING, messages
        
        # 改善提案チェック
        for pattern, message in self.improvement_suggestions:
            if re.search(pattern, command):
                logger.info(f"Improvement suggestion for: {command}")
                messages.append(f"💡 {message}")
                return SecurityLevel.INFO, messages
        
        # デフォルトで許可
        logger.info(f"Command allowed: {command}")
        return SecurityLevel.ALLOW, messages
    
    def format_response(self, security_level: str, messages: List[str]) -> Dict:
        """
        レスポンスをフォーマットする
        
        Args:
            security_level: セキュリティレベル
            messages: メッセージのリスト
            
        Returns:
            JSONレスポンス
        """
        if security_level == SecurityLevel.BLOCK:
            return {
                "decision": "block",
                "reason": "\n".join(messages)
            }
        elif security_level == SecurityLevel.WARNING:
            return {
                "decision": "approve",
                "reason": f"警告: {' '.join(messages)}"
            }
        else:
            # INFO や ALLOW の場合は通常の処理を続行
            return {}

def main():
    """メイン処理"""
    try:
        # 標準入力からJSONを読み取り
        input_data = json.loads(sys.stdin.read())
        
        # Bashツールでない場合は許可
        if input_data.get("tool") != "Bash":
            sys.exit(0)
        
        # コマンドを取得
        command = input_data.get("command", "")
        
        # バリデーターを初期化
        validator = CommandValidator()
        
        # コマンドを検証
        security_level, messages = validator.validate_command(command)
        
        # メッセージを標準エラーに出力
        for message in messages:
            print(message, file=sys.stderr)
        
        # レスポンスを生成
        response = validator.format_response(security_level, messages)
        
        # JSONレスポンスを出力
        if response:
            print(json.dumps(response, ensure_ascii=False))
        
        # 終了コード
        if security_level == SecurityLevel.BLOCK:
            sys.exit(2)
        else:
            sys.exit(0)
            
    except json.JSONDecodeError:
        logger.error("Invalid JSON input")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()