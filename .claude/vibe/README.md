# Vibe Logger Integration for Claude File Template

## 概要
vibe-loggerは、AI支援開発のために設計された構造化ログライブラリです。
Claude CodeやGemini CLIなどのAIアシスタントがコードを理解しやすいログを生成し、
デバッグ効率を劇的に向上させます。

## 主な特徴
- **AI最適化ログ**: JSON形式の構造化ログでAIが文脈を理解しやすい
- **相関追跡**: 操作間の関連性を自動追跡
- **人間/AI注釈**: `human_note`と`ai_note`フィールドでコミュニケーション強化
- **スレッドセーフ**: 並行処理環境でも安全に使用可能

## インストール

### Python版
```bash
pip install vibelogger
```

### TypeScript/Node.js版
```bash
npm install vibelogger
```

## 基本的な使い方

### Python
```python
from vibelogger import create_file_logger

# ロガーの作成
logger = create_file_logger("my_project")

# 構造化ログの記録
logger.info(
    operation="user_authentication",
    message="ユーザー認証プロセス開始",
    context={
        "user_id": "123",
        "method": "oauth2",
        "ip_address": "192.168.1.1"
    },
    human_note="AI-TODO: 認証失敗時のリトライロジックを確認"
)

# エラーログ
logger.error(
    operation="database_connection",
    message="データベース接続エラー",
    context={
        "error_code": "ECONNREFUSED",
        "retry_count": 3,
        "host": "localhost:5432"
    },
    human_note="AI-FIXME: 接続プールの設定を見直す必要あり"
)
```

### TypeScript
```typescript
import { createFileLogger } from 'vibelogger';

// ロガーの作成
const logger = createFileLogger('my_project');

// 構造化ログの記録
logger.info({
    operation: 'user_authentication',
    message: 'ユーザー認証プロセス開始',
    context: {
        userId: '123',
        method: 'oauth2',
        ipAddress: '192.168.1.1'
    },
    humanNote: 'AI-TODO: 認証失敗時のリトライロジックを確認'
});
```

詳細な使用例は [example_usage.ts](.claude/vibe/example_usage.ts) を参照してください。

## Claude File Templateとの統合

### 1. Memory Bankとの連携
vibe-loggerのログを自動的にMemory Bankに同期：

```python
# .claude/vibe/sync_vibe_logs.py
import json
import sqlite3
from pathlib import Path
from vibelogger import create_file_logger

class VibeMemoryBankSync:
    def __init__(self):
        self.logger = create_file_logger("claude_project")
        self.db_path = Path(".claude/index/knowledge.db")
    
    def sync_log_to_memory_bank(self, log_entry):
        """vibe-loggerのエントリをMemory Bankに同期"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # ログをMarkdown形式に変換
        markdown_content = self._convert_to_markdown(log_entry)
        
        # Memory Bankに挿入
        cursor.execute("""
            INSERT INTO knowledge (title, content, file_path, tags)
            VALUES (?, ?, ?, ?)
        """, (
            f"VibeLog: {log_entry['operation']}",
            markdown_content,
            f"vibe-logs/{log_entry['timestamp']}.md",
            "vibe-log,debug,ai-friendly"
        ))
        
        conn.commit()
        conn.close()
    
    def _convert_to_markdown(self, log_entry):
        """JSONログをMarkdown形式に変換"""
        return f"""# {log_entry['operation']} - {log_entry['timestamp']}

## メッセージ
{log_entry['message']}

## コンテキスト
```json
{json.dumps(log_entry['context'], indent=2, ensure_ascii=False)}
```

## ノート
- **Human Note**: {log_entry.get('human_note', 'なし')}
- **AI Note**: {log_entry.get('ai_note', 'なし')}

## メタデータ
- **レベル**: {log_entry['level']}
- **相関ID**: {log_entry.get('correlation_id', 'なし')}
"""
```

### 2. Hooksによる自動化
`.claude/hooks.yaml`に追加：

```yaml
# Vibe Logger統合
- event: PostToolUse
  matcher:
    tool: Bash
    command_contains: "python"
  command: |
    # エラー発生時にvibe-loggerで記録
    if [ $CLAUDE_EXIT_CODE -ne 0 ]; then
      python3 -c "
from vibelogger import create_file_logger
logger = create_file_logger('claude_project')
logger.error(
    operation='command_execution',
    message='コマンド実行エラー',
    context={
        'command': '$CLAUDE_COMMAND',
        'exit_code': $CLAUDE_EXIT_CODE,
        'working_dir': '$PWD'
    },
    human_note='AI-DEBUG: このエラーの原因を調査してください'
)"
    fi
```

### 3. デバッグワークフロー統合

#### エラー発生時の自動記録
```python
# .claude/vibe/error_handler.py
import traceback
from vibelogger import create_file_logger

logger = create_file_logger("claude_project")

def vibe_error_handler(func):
    """デコレータ: エラーを自動的にvibe-loggerで記録"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(
                operation=f"{func.__module__}.{func.__name__}",
                message=str(e),
                context={
                    "args": str(args),
                    "kwargs": str(kwargs),
                    "traceback": traceback.format_exc()
                },
                human_note="AI-FIXME: このエラーの修正方法を提案してください"
            )
            raise
    return wrapper
```

## ベストプラクティス

### 1. 操作名の一貫性
```python
# Good
logger.info(operation="user.authentication.start", ...)
logger.info(operation="user.authentication.success", ...)
logger.info(operation="user.authentication.failed", ...)

# Bad
logger.info(operation="auth", ...)
logger.info(operation="user_logged_in", ...)
```

### 2. コンテキストの充実
```python
# Good - AIが理解しやすい詳細なコンテキスト
logger.info(
    operation="api_request",
    message="外部API呼び出し",
    context={
        "endpoint": "https://api.example.com/users",
        "method": "GET",
        "headers": {"Authorization": "Bearer [MASKED]"},
        "params": {"limit": 100, "offset": 0},
        "response_time_ms": 245,
        "status_code": 200
    }
)

# Bad - 情報が不足
logger.info(
    operation="api_request",
    message="API呼び出し",
    context={"status": "OK"}
)
```

### 3. AI-TODOパターン
```python
# AIに特定のアクションを依頼
human_note="AI-TODO: このループの最適化方法を提案"
human_note="AI-FIXME: メモリリークの可能性を調査"
human_note="AI-REVIEW: セキュリティの観点からレビュー"
human_note="AI-OPTIMIZE: パフォーマンス改善案を提示"
```

## 統合後の利点

1. **デバッグ効率の向上**
   - AIがエラーの文脈を完全に理解
   - 過去の類似エラーとの比較が容易

2. **知識の蓄積**
   - すべてのログがMemory Bankに保存
   - パターン認識による問題予防

3. **チーム開発の支援**
   - 誰が見ても理解できる構造化ログ
   - AIアシスタントとの効率的な協働

## トラブルシューティング

### ログファイルが大きくなりすぎる
```python
# ログローテーション設定
logger = create_file_logger(
    "my_project",
    max_memory_kb=10240,  # 10MB制限
    rotation_count=5      # 最大5ファイル保持
)
```

### パフォーマンスへの影響
- 非同期ロギングの使用を検討
- 本番環境では適切なログレベルを設定

## 参考リンク
- [vibe-logger GitHub](https://github.com/fladdict/vibe-logger)
- [作者による解説記事](https://note.com/fladdict/n/n5046f72bdadd)
- [Claude Code ドキュメント](https://docs.anthropic.com/en/docs/claude-code)