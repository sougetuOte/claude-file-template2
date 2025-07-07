# 変更履歴 - Claude File Template

プロジェクトの重要な変更はすべてこのファイルに記録されます。

形式は [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) に基づき、
[Semantic Versioning](https://semver.org/spec/v2.0.0.html) に従っています。

## [2.0.0] - 2025-07-07

### 🚀 新機能 (Memory Bank 2.0)

#### Phase 1: 知識管理基盤
- **SQLite + FTS5**: 高速全文検索対応知識ベース
- **Markdown同期**: .claude/*.mdファイルとの自動連携
- **リンク機能**: 知識間の関係性管理
- **Python CLI**: `k_command.py`による包括的知識管理

#### Phase 2: MCP統合
- **TypeScript MCPサーバー**: Anthropic標準プロトコル対応
- **セキュアPythonブリッジ**: CVE-2025-49596対策済み
- **MCPツール**: Claude Codeからの直接アクセス
- **知識操作API**: 検索・追加・リンク・関連表示

#### Phase 3: AI支援機能
- **コード品質監視**: AST解析による重複検出・複雑度計算
- **タスクコーディネーター**: 作業内容に応じた最適モード提案
- **知識自動整理**: 古いエラー情報のアーカイブ・重複統合
- **パターン抽出**: 共通パターンの自動識別・記録

### ⚡ パフォーマンス改善
- **プロンプトキャッシュ**: 90%コスト削減・85%レイテンシ短縮
- **階層型情報管理**: 必要な情報のみを効率的に参照
- **知識検索最適化**: SQLite FTS5による高速検索
- **自動Hooks**: ファイル変更時の自動品質チェック

### 🛠️ 機能強化

#### 新コマンド
```bash
/k search "query"           # 知識検索
/k add "title" "content"    # 知識追加
/k related "id"             # 関連知識表示
/debug:start                # デバッグ特化モード
/feature:plan               # 新機能開発モード
/review:check               # コードレビューモード
/project:plan               # プロジェクト計画モード
```

#### ディレクトリ構造拡張
```
.claude/
├── core/           # 常時参照ファイル
├── context/        # 必要時参照ファイル
├── index/          # 知識管理エンジン (新規)
├── mcp/            # MCP統合システム (新規)
├── quality/        # AI品質監視 (新規)
├── agents/         # タスクコーディネーター (新規)
├── commands/       # カスタムコマンド (新規)
└── guidelines/     # 開発ガイドライン (拡張)
```

### 📝 ドキュメント追加
- **README.md**: Memory Bank 2.0機能紹介
- **INSTALL.md**: 詳細インストールガイド
- **USER_GUIDE.md**: 包括的使用方法
- **MIGRATION.md**: v1.2からの移行手順

### 🛡️ セキュリティ強化
- **CVE-2025-49596対策**: MCP通信のセキュア化
- **入力検証**: SQLインジェクション等の防止
- **権限管理**: ファイルアクセス権の適切化

### 🔄 Breaking Changes
- **Python要件**: 3.8+必須（Memory Bank機能用）
- **ディレクトリ構造**: .claude/index/等の新規ディレクトリ
- **依存関係**: SQLite3、Node.js（MCP用）の追加

---

## [1.2.0] - 2025-06-22

### Added
- 汎用的開発テンプレート（言語・技術スタック非依存）
- Anthropicベストプラクティス統合
- 階層化Memory Bankシステム（core/context/archive構造）
- 軽量コマンドセット（基本4個+専門化3個）
- 開発規約（パッケージ管理・コード品質・Git/PR規約）
- 実行コマンド一覧（`[tool]`記法で言語非依存）
- エラー対応ガイド（問題解決順序・ベストプラクティス）
- 品質ゲート（段階別チェックリスト・自動化レベル分類）
- Git操作パターン・学習ログテンプレート
- タグ検索システム（#urgent #bug #feature #completed）

### Features
- 日次3分更新でMemory Bank維持
- コンテキスト使用量最小化
- 個人開発〜中規模プロジェクト対応
- AI主導開発フロー支援

### Initial Release
個人開発者向けの効率的なClaude Code開発テンプレートとして初回リリース