# 使い方ガイド - Claude File Template v2.0

## 📚 目次

1. [基本概念](#基本概念)
2. [Memory Bank使い方](#memory-bank使い方)
3. [モード切り替え](#モード切り替え)
4. [知識管理](#知識管理)
5. [コード品質監視](#コード品質監視)
6. [セキュリティ機能](#セキュリティ機能)
7. [自動化機能](#自動化機能)
8. [Vibe Logger（AI最適化ログ）](#vibe-loggerai最適化ログ)
9. [トラブルシューティング](#トラブルシューティング)

## 🎯 基本概念

### Memory Bank 2.0システム
Claude File Template v2.0は**Memory Bank 2.0**という知識管理システムを核としています：

```
.claude/
├── core/           # 常時参照ファイル
├── context/        # 必要時参照ファイル  
├── index/          # 知識管理エンジン
├── mcp/            # MCP統合システム
├── quality/        # AI品質監視
└── agents/         # タスクコーディネーター
```

### 階層型情報管理
- **Core**: 現在状況・次アクション（常時参照）
- **Context**: 技術詳細・履歴（必要時参照）
- **Index**: SQLite知識ベース（高速検索）

## 🧠 Memory Bank使い方

### Claude Codeでの基本操作

```bash
# Claude Codeを起動
claude

# 知識検索
/k search "検索したいキーワード"

# 知識追加
/k add "タイトル" "内容"

# 関連知識表示
/k related "ID番号"
```

### 高速同期機能 (v2.1.0新機能)

```bash
# インクリメンタル同期（変更ファイルのみ）
python3 .claude/index/sync_markdown.py incremental

# バッチ処理（複数ファイル一括）
python3 .claude/index/sync_markdown.py batch

# スマート同期（重要ファイルのみ）
python3 .claude/index/sync_markdown.py smart

# 統計情報付き同期
python3 .claude/index/sync_markdown.py stats

# データベース情報表示
python3 .claude/index/sync_markdown.py info
```

#### パフォーマンス改善
- **60-80%高速化**: インクリメンタル同期
- **重複チェック**: ハッシュベースの自動スキップ
- **実行時間**: 0.1秒以内での同期完了
- **自動実行**: hooks経由で自動同期（設定済み）

### Python CLIでの詳細操作

```bash
# 知識管理
python .claude/commands/k_command.py search "query"
python .claude/commands/k_command.py add "title" "content" "type"
python .claude/commands/k_command.py link "from_id" "to_id" "関係"

# 一覧表示
python .claude/commands/k_command.py list
python .claude/commands/k_command.py list --type memo
```

## 🔧 モード切り替え

### 利用可能なモード

#### `/debug:start` - デバッグモード
```bash
# 使用場面
- エラー発生時
- バグ修正
- 問題調査

# 自動参照ファイル
- .claude/debug/latest.md
- .claude/context/history.md
```

#### `/feature:plan` - 機能開発モード
```bash
# 使用場面
- 新機能実装
- 機能拡張
- プロトタイプ作成

# 自動参照ファイル
- .claude/core/overview.md
- .claude/context/tech.md
- docs/requirements.md
```

#### `/review:check` - コードレビューモード
```bash
# 使用場面
- コード品質確認
- セキュリティチェック
- パフォーマンス確認

# 自動参照ファイル
- .claude/guidelines/development.md
- .claude/guidelines/testing-quality.md
```

#### `/project:plan` - プロジェクト計画モード
```bash
# 使用場面
- タスク計画
- 進捗管理
- 目標設定

# 自動参照ファイル
- .claude/core/next.md
- .claude/core/current.md
```

### モード自動提案
```bash
# タスクに最適なモードを提案
python .claude/agents/simple_coordinator.py suggest "Fix authentication bug"
# → debugモードを提案

python .claude/agents/simple_coordinator.py suggest "Add user registration"
# → featureモードを提案
```

## 📝 知識管理

### 知識の追加

```bash
# メモの追加
/k add "API設計メモ" "RESTful APIの設計原則" "memo"

# エラーの記録
/k add "認証エラー" "JWT token expired error" "error"

# 解決策の記録
/k add "JWT修正方法" "トークン期限を延長" "solution"
```

### 知識のリンク
```bash
# エラーと解決策をリンク
/k link "error_id" "solution_id" "solves"

# 関連情報をリンク
/k link "memo_id" "reference_id" "references"
```

### 高度な検索
```bash
# タイプ別検索
python .claude/commands/k_command.py search "authentication" --type error

# タグ検索
python .claude/commands/k_command.py search "tag:api"

# 複合検索
python .claude/commands/k_command.py search "jwt AND token"
```

## 🔍 コード品質監視

### 自動品質チェック
```bash
# ファイル編集時に自動実行（Hooks設定済み）
# 手動実行の場合
python .claude/quality/code_monitor.py check "your_file.py"
```

### 重複コード検出
```python
# 結果例
{
  "file_path": "auth.py",
  "structure_hash": "a1b2c3d4",
  "complexity": 8,
  "duplicate_found": true,
  "similar_files": ["auth_utils.py"],
  "suggestions": [
    "既存のコードを再利用することを検討してください",
    "類似パターン: 2件"
  ]
}
```

### プロジェクト全体分析
```bash
# コードパターンの分析
python .claude/quality/code_monitor.py analyze

# 結果例
{
  "total_code_items": 15,
  "average_complexity": 6.2,
  "patterns": {
    "complexity_5": 8,
    "complexity_10": 3
  },
  "suggestions": [
    "コードパターンが豊富: 継続的な改善が見込まれます"
  ]
}
```

## 🛡️ セキュリティ機能

### Claude Code セキュリティシステム
v2.0では`--dangerously-skip-permissions`使用時でも安全にClaude Codeを利用できるセキュリティシステムを実装しています。

#### 多層防御システム
```bash
# 1. settings.json による事前ブロック
# 2. PreToolUseフック による詳細検証
# 3. PostToolUseフック による実行ログ記録
# 4. セキュリティテスト による継続的な検証
```

### 危険コマンドの自動ブロック

#### 🚫 ブロック対象コマンド
以下のコマンドは実行前に自動的にブロックされます：

```bash
# 権限昇格
sudo, su

# 破壊的削除
rm -rf /, rm -rf ~/, rm -rf *

# 危険な権限変更
chmod 777, chmod -R 777

# 外部ネットワークアクセス
curl, wget, nc, netcat

# システム変更
systemctl, service, mount, umount

# パッケージ管理
apt install, yum install, pip install, npm install -g

# その他危険な操作
git config --global, crontab, fdisk, mkfs
```

#### ⚠️ 警告レベルコマンド
以下のコマンドは警告付きで実行されます：

```bash
# Git危険操作
git push --force, git reset --hard, git clean -fd

# パッケージ削除
npm uninstall, pip uninstall

# Docker操作
docker rm, docker rmi
```

### セキュリティテスト

#### 自動テスト実行
```bash
# セキュリティテストスイートの実行
python3 .claude/scripts/test_security.py

# テスト結果例
🔒 Claude Code セキュリティテスト開始
✅ 安全なコマンドのテスト: 8/8 通過
🚫 危険なコマンドのテスト: 8/8 ブロック
💡 改善提案のテスト: 4/4 動作確認
```

#### 手動テスト
```bash
# 個別コマンドのテスト
echo '{"tool": "Bash", "command": "echo hello"}' | python3 .claude/scripts/bash_security_validator.py

# 危険コマンドのテスト
echo '{"tool": "Bash", "command": "sudo rm -rf /"}' | python3 .claude/scripts/bash_security_validator.py
```

### セキュリティログ

#### ログファイルの場所
- **セキュリティログ**: `.claude/logs/security.log`
- **コマンド履歴**: `.claude/logs/command_history.log`

#### ログの確認
```bash
# セキュリティイベントの確認
tail -f .claude/logs/security.log

# 危険なコマンドのアラート確認
grep "SECURITY-ALERT" .claude/logs/security.log

# 最近のコマンド実行履歴
tail -20 .claude/logs/command_history.log
```

### コマンド改善提案

#### 💡 推奨コマンド
システムがより安全・効率的なコマンドを自動提案します：

```bash
grep → rg (ripgrep)          # 高速・多機能検索
find → fd                    # 高速ファイル検索
cat → batcat                 # シンタックスハイライト
ls → eza --icons --git       # カラフル・Git統合表示
```

### 緊急時の対応

#### セキュリティフックの一時無効化
```bash
# 環境変数で一時無効化
export CLAUDE_HOOKS_ENABLED=false

# 設定ファイルで無効化
# .claude/settings.json から hooks セクションを削除
```

#### 問題発生時の対処
1. **コマンドが実行された場合**
   - 即座に実行を中止（Ctrl+C）
   - セキュリティログを確認
   - 必要に応じてシステム状態を検証

2. **誤検知の場合**
   - 一時的にフックを無効化
   - 必要に応じて`.claude/scripts/bash_security_validator.py`のパターンを調整

### カスタマイズ

#### セキュリティルールの追加
```python
# .claude/scripts/bash_security_validator.py の編集例
dangerous_patterns = [
    # 既存パターン...
    (r"your_custom_pattern", "カスタムメッセージ"),
]
```

#### プロジェクト固有の設定
```json
// .claude/settings.json でプロジェクト固有の危険コマンドを追加
{
  "permissions": {
    "deny": [
      "Bash(project_specific_dangerous_command)"
    ]
  }
}
```

詳細なセキュリティ設定: @.claude/security/README.md

## 🤖 自動化機能

### 自動Markdown同期
```bash
# .claude/*.mdファイル編集時に自動実行
# 手動同期の場合
python .claude/index/sync_markdown.py
```

### 知識自動整理
```bash
# 週1回自動実行（SessionStart時）
# 手動実行の場合
python .claude/index/auto_organize.py organize

# 実行内容
- 解決済みエラーのアーカイブ
- 重複知識の統合
- パターン抽出
- 統計情報更新
```

### ワークフロー提案
```bash
# タスクに応じたワークフロー提案
python .claude/agents/simple_coordinator.py workflow "Fix bug" "debug"

# 結果例
{
  "task": "Fix bug",
  "mode": "debug",
  "steps": [
    "1. 問題の再現と詳細な記録",
    "2. エラーログの分析",
    "3. 関連するコード箇所の特定",
    "4. 修正方法の検討と実装",
    "5. テストによる修正確認"
  ],
  "estimated_time": "30-60分",
  "tools_needed": ["Read", "Grep", "Edit", "Bash"]
}
```

## 🚀 Vibe Logger（AI最適化ログ）

### 概要
Vibe Loggerは、AIアシスタントがエラー文脈を完全に理解できるよう設計された構造化ログシステムです。

### 基本的な使い方

#### Python版
```python
from .claude.vibe.sync_vibe_logs import vibe_log

# 構造化ログの記録
vibe_log(
    level="ERROR",
    operation="database.connection",
    message="接続エラー",
    context={
        "host": "localhost",
        "port": 5432,
        "error_code": "ECONNREFUSED"
    },
    human_note="AI-FIXME: 接続プールの設定を見直してください"
)
```

#### TypeScript/Node.js版
```typescript
import { createFileLogger } from 'vibelogger';

const logger = createFileLogger('my_project');

logger.error({
    operation: 'api.request',
    message: 'APIタイムアウト',
    context: {
        endpoint: '/api/users',
        timeout: 30000
    },
    humanNote: 'AI-DEBUG: タイムアウト設定を確認'
});
```

### AI-TODOシステム
以下のタグを使用してAIに特定のアクションを依頼：
- `AI-TODO`: 実装や改善の提案
- `AI-FIXME`: バグ修正の提案
- `AI-DEBUG`: デバッグ支援
- `AI-OPTIMIZE`: パフォーマンス改善
- `AI-REVIEW`: コードレビュー

### CLIコマンド
```bash
# ログの作成
python .claude/vibe/sync_vibe_logs.py log error "api.timeout" "タイムアウトエラー"

# ログの検索
python .claude/vibe/sync_vibe_logs.py search "error"

# エラーサマリー
python .claude/vibe/sync_vibe_logs.py summary --days 7
```

### 自動エラー記録
hooks.yamlによりPython/Node.jsエラー時に自動的に記録されます：
- エラーコンテキストの完全キャプチャ
- Memory Bankへの自動同期
- AI向けデバッグノートの生成

### エラーハンドラー
```python
from .claude.vibe.sync_vibe_logs import vibe_error_handler

@vibe_error_handler
def risky_operation(data):
    # エラーが自動的にログされる
    return process_data(data)
```

詳細な使用例は `.claude/vibe/example_usage.py` と `.claude/vibe/example_usage.ts` を参照してください。

## 📊 MCP統合（Phase 2機能）

### MCP設定確認
```bash
# MCPサーバーの状態確認
cd .claude/mcp/memory-server
node index.js test

# Claude CodeからMCPツールとして利用
# （設定後は自動的に利用可能）
```

### MCP経由での知識アクセス
```javascript
// Claude CodeがMCPツールとして以下を利用
- knowledge_search: 知識検索
- knowledge_add: 知識追加
- knowledge_link: 知識リンク
- knowledge_related: 関連知識取得
```

## 🛠️ カスタマイズ

### プロジェクト固有設定

#### 1. 基本情報の更新
```bash
# プロジェクト概要
vi .claude/core/overview.md

# 現在状況
vi .claude/core/current.md

# 次のアクション
vi .claude/core/next.md
```

#### 2. 技術情報の設定
```bash
# 技術スタック
vi .claude/context/tech.md

# 開発ガイドライン
vi .claude/guidelines/development.md
```

#### 3. 自動化設定
```bash
# Hooks設定
vi .claude/hooks.yaml

# 特定の自動化を無効にする場合
# 該当セクションをコメントアウト
```

### モードの追加
```python
# .claude/agents/simple_coordinator.py
# modesディクショナリに新しいモードを追加

"custom_mode": {
    "trigger_words": ["custom", "カスタム"],
    "command": "/custom:start",
    "context_files": [".claude/custom/config.md"],
    "description": "カスタムモード",
    "priority": "medium"
}
```

## 🚨 トラブルシューティング

### よくある問題

#### 1. 知識検索が動作しない
```bash
# SQLiteデータベースの確認
ls -la .claude/index/knowledge.db

# データベースの再作成
rm .claude/index/knowledge.db
python .claude/index/knowledge_store.py
```

#### 2. MCPツールが利用できない
```bash
# Node.js依存関係の確認
cd .claude/mcp/memory-server
npm install

# MCPサーバーの起動確認
node index.js
```

#### 3. Hooksが動作しない
```bash
# Pythonパスの確認
export PYTHONPATH="${PYTHONPATH}:$(pwd)/.claude/index"

# ファイル権限の確認
chmod +x .claude/commands/*.py
chmod +x .claude/quality/*.py
```

#### 4. 重複検出が不正確
```bash
# コードモニターのテスト
python .claude/quality/code_monitor.py test

# データベースの初期化
rm .claude/index/knowledge.db
```

### パフォーマンス最適化

#### 1. 知識ベースのサイズ管理
```bash
# 古いパターンのクリーンアップ
python .claude/index/auto_organize.py cleanup 60

# アーカイブ済みデータの確認
python .claude/commands/k_command.py list --type archived
```

#### 2. キャッシュの活用
```bash
# .claude/settings.jsonでキャッシュ設定確認
cat .claude/settings.json

# キャッシュクリア（必要時）
rm -rf .ccache
```

## 📈 効果測定

### 開発効率の確認
```bash
# 知識ベース統計
python .claude/index/auto_organize.py stats

# 結果例
{
  "total_items": 25,
  "by_type": {
    "memo": 8,
    "error": 5,
    "solution": 5,
    "code": 7
  },
  "recent_activity": {
    "last_7_days": 12,
    "daily_average": 1.7
  },
  "health_score": 85
}
```

### 品質監視結果
```bash
# コード品質分析
python .claude/quality/code_monitor.py analyze

# 複雑度・重複度の推移を確認
```

## 🔗 関連リンク

- [インストールガイド](INSTALL.md)
- [マイグレーションガイド](MIGRATION.md)
- [変更履歴](CHANGELOG.md)
- [Claude Code公式](https://docs.anthropic.com/en/docs/claude-code)

---

**Memory Bank 2.0で効率的なAI開発を実現しましょう** 🚀