# Claude File Template v2.1 - DevContainer対応版

このプロジェクトは**Claude File Template v2.1**を使用しており、DevContainer完全対応により、どこでも同じ開発環境を実現します。

## 🚀 プロジェクト概要

Claude Code用の高度なプロジェクトテンプレートで、以下の機能を提供：
- **Memory Bank 2.0**: AI支援開発のための知識管理システム（90%コスト削減・85%レイテンシ短縮）
- **DevContainer対応**: VS Code + Dockerで即座に開発環境構築
- **自動化ツール**: コード品質チェック、セキュリティ検証、知識同期
- **MCP統合**: Model Context Protocol対応でAIとの深い統合

## 📚 ドキュメント

### 基本ドキュメント
- **インストール**: [docs/INSTALL.md](docs/INSTALL.md)
- **使い方ガイド**: [docs/USER_GUIDE.md](docs/USER_GUIDE.md)  
- **移行ガイド**: [docs/MIGRATION.md](docs/MIGRATION.md)
- **変更履歴**: [docs/CHANGELOG.md](docs/CHANGELOG.md)

### DevContainer開発
- **セットアップガイド**: [.devcontainer/README.md](.devcontainer/README.md)
- **シークレット管理**: [.devcontainer/secrets-management.md](.devcontainer/secrets-management.md)
- **動作確認手順**: [.devcontainer/test-checklist.md](.devcontainer/test-checklist.md)

## 🔧 セットアップ

### 方法1: DevContainer（推奨）
```bash
# 1. VS Codeでプロジェクトを開く
code .

# 2. 「Reopen in Container」を実行（F1キー）
# 3. 自動環境構築を待つ（初回3-5分）
```

### 方法2: ローカル環境
```bash
# Python 3.11とNode.js 20が必要
python3 --version  # 3.11以上
node --version     # v20以上

# Memory Bank初期化
python3 .claude/index/sync_markdown.py smart
```

## 💡 使い方

### Memory Bank検索
```bash
# コマンドライン検索
python3 .claude/commands/k_command.py search "検索キーワード"

# DevContainerエイリアス
ks "検索キーワード"
```

### プロジェクト管理
```bash
/project:plan   # 作業計画立案
/project:daily  # 日次スタンドアップ
/project:focus  # タスクに集中
/project:act    # 計画実行
```

### 開発フロー
```bash
# 朝のルーティン
git pull origin main
python3 .claude/index/sync_markdown.py incremental
/project:daily

# コード品質チェック
npm run lint      # JavaScript/TypeScript
python3 -m flake8 # Python
python3 -m mypy   # 型チェック
```

## 🛠 主な機能

### Memory Bank 2.0
- SQLite + FTS5による高速全文検索
- インクリメンタル同期で効率的な更新
- 知識の自動整理とアーカイブ
- リンク機能による知識の関連付け

### 自動化機能
- コード変更時の品質チェック
- セキュリティコマンドの事前検証
- Git操作の自動記録
- テスト成功の履歴管理

### 開発支援
- 20種類以上のVS Code拡張機能を自動設定
- Python/Node.js/SQLite環境の自動構築
- 便利なシェルエイリアス設定
- プロジェクト固有のカスタムコマンド

### Vibe Logger統合 (NEW!)
- AI理解に最適化された構造化ログ
- エラー時の詳細コンテキスト自動記録
- Memory Bankとの自動同期
- デバッグ効率の大幅向上

## 📂 ディレクトリ構成
```
.
├── .claude/              # Memory Bank & 自動化設定
│   ├── core/            # 現在の状況・計画
│   ├── context/         # 技術詳細・履歴
│   ├── index/           # 知識データベース
│   ├── mcp/             # MCP統合
│   ├── vibe/            # AI最適化ログシステム
│   └── hooks.yaml       # 自動化設定
├── .devcontainer/       # DevContainer設定
├── docs/                # プロジェクトドキュメント
├── CLAUDE.md            # Claude Code設定
└── README.md            # このファイル
```

## 🤝 貢献方法

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'feat: add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. Pull Requestを作成

## 📝 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

---

**Memory Bank 2.0**: AI開発の未来を今すぐ体験 🚀