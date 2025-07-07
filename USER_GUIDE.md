# 使い方ガイド - Claude File Template v2.0

## 📚 目次

1. [基本概念](#基本概念)
2. [Memory Bank使い方](#memory-bank使い方)
3. [モード切り替え](#モード切り替え)
4. [知識管理](#知識管理)
5. [コード品質監視](#コード品質監視)
6. [自動化機能](#自動化機能)
7. [トラブルシューティング](#トラブルシューティング)

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