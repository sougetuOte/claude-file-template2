# [プロジェクト名]

## プロジェクト概要
[プロジェクトの簡潔な説明をここに記載]

## プロンプトキャッシュ最適化設定
- **CLAUDE_CACHE**: `./.ccache` - 90%コスト削減・85%レイテンシ短縮
- **cache_control**: 長期安定情報に適用済み
- **設定**: `.claude/settings.json`参照

## Memory Bank構造
### コア（常時参照）
- 現在の状況: @.claude/core/current.md
- 次のアクション: @.claude/core/next.md
- プロジェクト概要: @.claude/core/overview.md
- クイックテンプレート: @.claude/core/templates.md

### コンテキスト（必要時参照）
- 技術詳細: @.claude/context/tech.md
- 履歴・決定事項: @.claude/context/history.md
- 技術負債: @.claude/context/debt.md

### デバッグ/その他
- 最新デバッグ: @.claude/debug/latest.md
- 完了済み情報: @.claude/archive/
- Hooks設定: @.claude/hooks.yaml

### Memory Bank 2.0 (Phase 1)
- **知識データベース**: `.claude/index/knowledge.db` (SQLite + FTS5)
- **知識管理API**: `.claude/index/knowledge_store.py`
- **Markdown同期**: `.claude/index/sync_markdown.py`
- **コマンドライン**: `python .claude/commands/k_command.py`

### Memory Bank 2.0 (Phase 2) - MCP統合
- **MCPサーバー**: `.claude/mcp/memory-server/index.js` (Node.js)
- **Python Bridge**: `.claude/mcp/memory-server/bridge.py` (セキュア)
- **MCP設定**: `.claude/mcp/config.json` (CVE-2025-49596対策)
- **テストスイート**: `.claude/mcp/memory-server/test-mcp.js`

### Memory Bank 2.0 (Phase 3) - 高度な機能
- **AI生成コード品質モニター**: `.claude/quality/code_monitor.py` (重複検出・品質改善)
- **簡易タスクコーディネーター**: `.claude/agents/simple_coordinator.py` (モード提案・ワークフロー)
- **知識自動整理システム**: `.claude/index/auto_organize.py` (パターン抽出・アーカイブ)
- **自動実行Hooks**: `.claude/hooks.yaml` (コード変更時の品質チェック)

## カスタムコマンド
| コマンド | 用途 | 詳細 |
|---------|------|------|
| `/project:plan` | 作業計画立案 | @.claude/commands/plan.md |
| `/project:act` | 計画実行 | @.claude/commands/act.md |
| `/project:focus` | タスク集中 | @.claude/commands/focus.md |
| `/project:daily` | 日次更新 | @.claude/commands/daily.md |
| `/debug:start` | デバッグ特化 | @.claude/commands/debug-start.md |
| `/feature:plan` | 新機能設計 | @.claude/commands/feature-plan.md |
| `/review:check` | コードレビュー | @.claude/commands/review-check.md |
| `/k` | 知識管理 | @.claude/commands/knowledge.md |

## 開発ガイドライン
- **開発全般**: @.claude/guidelines/development.md
- **Gitワークフロー**: @.claude/guidelines/git-workflow.md
- **テスト・品質**: @.claude/guidelines/testing-quality.md

## 実行コマンド一覧
```bash
# 基本開発フロー
[tool] install          # 依存関係インストール
[tool] run dev         # 開発サーバー起動
[tool] run test        # テスト実行
[tool] run check       # 総合チェック

# 詳細は @.claude/guidelines/development.md 参照
```

## プロジェクトデータ
- 設定: `config/settings.json`
- データ: `data/`
- 要求仕様: @docs/requirements.md

## Memory Bank使用方針
- **通常時**: coreファイルのみ参照でコンテキスト最小化
- **詳細必要時**: contextファイルを明示的に指定
- **定期整理**: 古い情報をarchiveに移動

## プロジェクト固有の学習
`.clauderules`ファイルに自動記録されます。