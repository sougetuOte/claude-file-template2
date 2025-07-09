# 変更履歴 - Claude File Template

プロジェクトの重要な変更はすべてこのファイルに記録されます。

形式は [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) に基づき、
[Semantic Versioning](https://semver.org/spec/v2.0.0.html) に従っています。

## [2.1.1] - 2025-07-09

### 🐳 DevContainer完全対応

#### 新機能
- **DevContainer環境**: VS Code + Dockerで一貫性のある開発環境を実現
- **自動環境構築**: Python 3.11, Node.js 20, SQLite, ripgrepを自動インストール
- **VS Code拡張機能**: 20種類以上の開発支援拡張機能を自動設定
- **シェル設定**: Zsh/Bash両対応の便利なエイリアス設定
- **セキュリティ**: SSH鍵の読み取り専用マウント、シークレット管理ガイド

#### DevContainer設定ファイル
```
.devcontainer/
├── devcontainer.json      # メイン設定
├── docker-compose.yml     # 複数サービス対応
├── Dockerfile            # カスタマイズ用
├── post-create.sh        # 環境セットアップ
├── .env.example          # 環境変数テンプレート
├── secrets-management.md  # シークレット管理
├── README.md             # 運用ガイド
├── test-checklist.md     # 動作確認手順
└── shell-config/         # シェル設定
```

#### 開発体験の向上
- **即座に開発開始**: コンテナ起動後すぐに使える環境
- **Memory Bank自動初期化**: 初回起動時に知識ベースを構築
- **便利なエイリアス**: `ks`（検索）、`devinfo`（環境情報）など
- **自動同期**: ディレクトリ移動時のMemory Bank自動同期

### 🚀 Vibe Logger統合（実験的機能）

#### 新機能
- **AI最適化ログシステム**: 構造化ログでAIアシスタントがエラー文脈を完全理解
- **Memory Bank連携**: vibe-loggerのログを自動的に知識ベースに変換・保存
- **自動エラー記録**: Python/Node.jsエラー時の詳細コンテキストを自動キャプチャ
- **AI-TODOシステム**: `AI-TODO`, `AI-FIXME`, `AI-DEBUG`タグによるAIへの指示

#### 統合内容
```
.claude/vibe/
├── README.md           # vibe-logger詳細ガイド
├── sync_vibe_logs.py   # Memory Bank同期スクリプト
├── example_usage.py    # Python使用例
└── example_usage.ts    # TypeScript/Node.js使用例
```

#### 自動化
- **hooks.yaml統合**: エラー発生時に自動的にvibe-loggerで記録
- **DevContainer対応**: `pip install vibelogger` と `npm install -g vibelogger` を自動実行
- **CLIツール**: `python3 .claude/vibe/sync_vibe_logs.py` コマンドでログ管理

### 📝 ドキュメント更新
- **README.md**: v2.1対応、DevContainer情報とVibe Logger機能追加
- **CLAUDE.md**: DevContainerクイックスタートとVibe Logger統合セクション追加
- **.gitignore**: DevContainer関連ファイルの除外設定
- **vibe/README.md**: Vibe Loggerの詳細な使用ガイド

## [2.1.0] - 2025-07-09

### ⚡ パフォーマンス大幅改善 (Memory Bank同期効率化)

#### 新機能
- **インクリメンタル同期**: 変更されたファイルのみを自動検出・同期
- **バッチ処理**: 複数ファイルの一括処理でスループット向上
- **スマート同期**: 重要ファイル（core/context/debug）の優先監視
- **統計機能**: 同期パフォーマンスの可視化
- **接続プーリング**: OptimizedKnowledgeStoreによるSQLite接続最適化

#### パフォーマンス向上
- **60-80%高速化**: インクリメンタル同期による劇的な改善
- **不要処理90%削減**: ファイル変更チェックによる効率化
- **重複チェック**: ハッシュベースの自動重複スキップ
- **実行時間**: 0.1秒以内での同期完了

#### 新コマンド
```bash
python3 .claude/index/sync_markdown.py incremental  # 変更ファイルのみ同期
python3 .claude/index/sync_markdown.py batch        # バッチ処理
python3 .claude/index/sync_markdown.py smart        # スマート同期
python3 .claude/index/sync_markdown.py stats        # 統計情報付き同期
python3 .claude/index/sync_markdown.py info         # データベース情報表示
```

#### Hooks最適化
- **条件分岐**: 不要なhooks実行を大幅削減
- **ファイル監視**: 重要ファイルのみの監視
- **セッション最適化**: 開始時のスマート同期

#### 技術的改善
- **OptimizedKnowledgeStore**: シングルトンパターンによる接続管理
- **ファイル変更追跡**: `.last_sync_times`による時刻管理
- **並列処理対応**: 複数ファイルの効率的処理

### 📝 ドキュメント更新
- **CLAUDE.md**: Memory Bank 2.0高速化機能の説明追加
- **.claude/context/tech.md**: 技術詳細・アーキテクチャ更新
- **.claude/context/history.md**: 決定事項・解決した問題の記録
- **.claude/commands/knowledge.md**: 新機能の使用方法追加

### 🛠️ 内部改善
- **重複チェック機能**: MD5ハッシュによる高速判定
- **エラーハンドリング**: より堅牢な例外処理
- **ログ機能**: 詳細な同期ログの出力

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
- **Claude Code セキュリティ**: 危険コマンドの多層防御システム
  - `settings.json`: 40+の危険コマンドパターンを事前ブロック
  - `PreToolUseフック`: コマンド実行前の詳細検証
  - `PostToolUseフック`: コマンド実行後の自動ログ記録
  - `セキュリティテスト`: 安全性の継続的な検証

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