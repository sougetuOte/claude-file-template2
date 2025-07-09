#!/usr/bin/env python3
"""
Vibe Logger と Memory Bank の統合
AI支援開発のための構造化ログをMemory Bankに同期
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
import sys
import os

# プロジェクトルートを追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from vibelogger import create_file_logger
    VIBE_LOGGER_AVAILABLE = True
except ImportError:
    VIBE_LOGGER_AVAILABLE = False
    print("Warning: vibelogger not installed. Run: pip install vibelogger")

from index.OptimizedKnowledgeStore import OptimizedKnowledgeStore


class VibeMemoryBankSync:
    """Vibe LoggerとMemory Bankを統合するクラス"""
    
    def __init__(self, project_name="claude_project"):
        self.project_name = project_name
        self.knowledge_store = OptimizedKnowledgeStore()
        
        if VIBE_LOGGER_AVAILABLE:
            self.logger = create_file_logger(project_name)
        else:
            self.logger = None
            
        # ログディレクトリ
        self.log_dir = Path(".claude/vibe/logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def log_and_sync(self, level, operation, message, context=None, human_note=None, ai_note=None):
        """ログを記録し、Memory Bankに同期"""
        if not self.logger:
            print(f"[{level}] {operation}: {message}")
            return
            
        # vibe-loggerでログ記録
        log_method = getattr(self.logger, level.lower())
        log_entry = {
            "operation": operation,
            "message": message,
            "context": context or {},
            "human_note": human_note,
            "ai_note": ai_note,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        log_method(**log_entry)
        
        # Memory Bankに同期
        self.sync_to_memory_bank(log_entry, level)
    
    def sync_to_memory_bank(self, log_entry, level):
        """ログエントリをMemory Bankに同期"""
        # Markdown形式に変換
        markdown_content = self._convert_to_markdown(log_entry, level)
        
        # タイトル生成
        title = f"VibeLog: {log_entry['operation']} [{level}]"
        
        # ファイルパス生成
        timestamp = log_entry['timestamp'].replace(':', '-').replace('.', '-')
        file_path = f".claude/vibe/logs/{timestamp}_{log_entry['operation']}.md"
        
        # Memory Bankに追加
        entry_id = self.knowledge_store.add_entry(
            title=title,
            content=markdown_content,
            file_path=file_path,
            tags=f"vibe-log,{level.lower()},ai-friendly,{log_entry['operation']}"
        )
        
        # 実際のファイルも保存
        self._save_markdown_file(file_path, markdown_content)
        
        return entry_id
    
    def _convert_to_markdown(self, log_entry, level):
        """JSONログをMarkdown形式に変換"""
        # human_noteからAIアクションを抽出
        ai_actions = self._extract_ai_actions(log_entry.get('human_note', ''))
        
        markdown = f"""# {log_entry['operation']} - {log_entry['timestamp']}

## 📊 ログ情報
- **レベル**: `{level}`
- **操作**: `{log_entry['operation']}`
- **タイムスタンプ**: {log_entry['timestamp']}

## 📝 メッセージ
{log_entry['message']}

## 🔍 コンテキスト
```json
{json.dumps(log_entry.get('context', {}), indent=2, ensure_ascii=False)}
```

## 💭 ノート
### Human Note
{log_entry.get('human_note', '*なし*')}

### AI Note
{log_entry.get('ai_note', '*なし*')}
"""

        # AIアクションがある場合は追加
        if ai_actions:
            markdown += f"""
## 🤖 AIアクション
{ai_actions}
"""

        # エラーレベルの場合は追加情報
        if level == "ERROR":
            markdown += """
## 🚨 エラー対応
- [ ] エラーの原因を特定
- [ ] 修正方法を検討
- [ ] テストケースを追加
- [ ] ドキュメントを更新
"""

        return markdown
    
    def _extract_ai_actions(self, human_note):
        """human_noteからAIアクションを抽出"""
        if not human_note:
            return ""
            
        actions = []
        ai_keywords = ["AI-TODO", "AI-FIXME", "AI-REVIEW", "AI-OPTIMIZE", "AI-DEBUG"]
        
        for keyword in ai_keywords:
            if keyword in human_note:
                action_type = keyword.replace("AI-", "")
                actions.append(f"- **{action_type}**: {human_note}")
                
        return "\n".join(actions)
    
    def _save_markdown_file(self, file_path, content):
        """Markdownファイルを保存"""
        full_path = Path(file_path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding='utf-8')
    
    def search_logs(self, query, level=None, operation=None):
        """ログを検索"""
        # Memory Bankから検索
        results = self.knowledge_store.search(query)
        
        # フィルタリング
        filtered_results = []
        for result in results:
            # vibe-logタグがあるものだけ
            if 'vibe-log' not in result.get('tags', ''):
                continue
                
            # レベルフィルタ
            if level and level.lower() not in result.get('tags', ''):
                continue
                
            # 操作フィルタ
            if operation and operation not in result.get('title', ''):
                continue
                
            filtered_results.append(result)
        
        return filtered_results
    
    def get_error_summary(self, days=7):
        """指定期間のエラーサマリーを取得"""
        # エラーログを検索
        errors = self.search_logs("", level="ERROR")
        
        # 操作別に集計
        error_summary = {}
        for error in errors:
            operation = error.get('title', '').split('[')[0].replace('VibeLog: ', '').strip()
            error_summary[operation] = error_summary.get(operation, 0) + 1
        
        return error_summary


# 便利な関数
def vibe_log(level, operation, message, context=None, human_note=None):
    """簡易ログ関数"""
    sync = VibeMemoryBankSync()
    sync.log_and_sync(level, operation, message, context, human_note)


def vibe_error_handler(func):
    """エラーハンドリングデコレータ"""
    import functools
    import traceback
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        sync = VibeMemoryBankSync()
        try:
            return func(*args, **kwargs)
        except Exception as e:
            sync.log_and_sync(
                level="ERROR",
                operation=f"{func.__module__}.{func.__name__}",
                message=str(e),
                context={
                    "args": str(args)[:200],  # 長すぎる場合は切り詰め
                    "kwargs": str(kwargs)[:200],
                    "traceback": traceback.format_exc()
                },
                human_note=f"AI-FIXME: {func.__name__}でエラーが発生。修正方法を提案してください"
            )
            raise
    
    return wrapper


# CLI機能
def main():
    """CLIエントリポイント"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Vibe Logger - Memory Bank Integration")
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # logコマンド
    log_parser = subparsers.add_parser('log', help='Create a vibe log')
    log_parser.add_argument('level', choices=['info', 'warning', 'error', 'debug'])
    log_parser.add_argument('operation', help='Operation name')
    log_parser.add_argument('message', help='Log message')
    log_parser.add_argument('--context', type=json.loads, help='JSON context')
    log_parser.add_argument('--note', help='Human note for AI')
    
    # searchコマンド
    search_parser = subparsers.add_parser('search', help='Search vibe logs')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--level', help='Filter by log level')
    search_parser.add_argument('--operation', help='Filter by operation')
    
    # summaryコマンド
    summary_parser = subparsers.add_parser('summary', help='Get error summary')
    summary_parser.add_argument('--days', type=int, default=7, help='Days to look back')
    
    args = parser.parse_args()
    
    if args.command == 'log':
        vibe_log(
            args.level.upper(),
            args.operation,
            args.message,
            args.context,
            args.note
        )
        print(f"✅ Logged: {args.operation}")
        
    elif args.command == 'search':
        sync = VibeMemoryBankSync()
        results = sync.search_logs(args.query, args.level, args.operation)
        
        print(f"\n🔍 Found {len(results)} vibe logs:\n")
        for result in results:
            print(f"- {result['title']}")
            print(f"  Tags: {result.get('tags', '')}")
            print(f"  File: {result.get('file_path', '')}\n")
            
    elif args.command == 'summary':
        sync = VibeMemoryBankSync()
        summary = sync.get_error_summary(args.days)
        
        print(f"\n📊 Error Summary (last {args.days} days):\n")
        for operation, count in sorted(summary.items(), key=lambda x: x[1], reverse=True):
            print(f"  {operation}: {count} errors")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()