# DevContainer 運用ガイド

## 概要
このプロジェクトは、VS Code Dev Containersを使用して、一貫性のある開発環境を提供します。
Python 3.11とNode.js 20をベースに、Claude Code Template専用の開発環境が自動構築されます。

## クイックスタート

### 前提条件
- [VS Code](https://code.visualstudio.com/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Dev Containers拡張機能](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

### 初回セットアップ
1. **リポジトリをクローン**
   ```bash
   git clone <repository-url>
   cd claude-file-template2
   ```

2. **VS Codeで開く**
   ```bash
   code .
   ```

3. **Dev Containerで開く**
   - コマンドパレット（F1）を開く
   - 「Dev Containers: Reopen in Container」を選択
   - 初回は数分かかります（イメージのビルド）

4. **環境変数の設定**（オプション）
   ```bash
   cp .devcontainer/.env.example .devcontainer/.env
   # .envファイルを編集して必要な値を設定
   ```

## 含まれる機能

### 開発ツール
- **Python 3.11**: 標準ライブラリ + 開発ツール（black, flake8, mypy, pytest）
- **Node.js 20**: MCP server用
- **SQLite**: Memory Bank用データベース
- **ripgrep**: 高速ファイル検索
- **Git**: 最新版

### VS Code拡張機能
自動的にインストールされる拡張機能：
- Python（Pylance, Black Formatter, Flake8）
- JavaScript/TypeScript（ESLint, Prettier）
- Markdown（All in One, Lint）
- Git（GitLens, Git Graph）
- その他便利ツール

### Claude Code統合
- Memory Bank 2.0（知識管理システム）
- MCP Server（AI統合）
- 自動化Hooks
- カスタムコマンド

## 日常的な使い方

### 基本コマンド
```bash
# Memory Bank同期
python3 .claude/index/sync_markdown.py smart

# 知識検索
python3 .claude/commands/k_command.py search "query"

# プロジェクト計画
/project:plan

# 日次更新
/project:daily
```

### 開発フロー
1. **朝のセットアップ**
   ```bash
   # 最新を取得
   git pull origin main
   
   # Memory Bank同期
   python3 .claude/index/sync_markdown.py incremental
   
   # 状況確認
   /project:daily
   ```

2. **作業中**
   - ファイル変更時に自動でMemory Bank同期
   - コード品質チェックが自動実行
   - セキュリティチェックが実行

3. **作業終了時**
   ```bash
   # 変更確認
   git status
   
   # テスト実行
   python3 -m pytest
   
   # コミット
   git add .
   git commit -m "feat: 機能追加"
   ```

## トラブルシューティング

### よくある問題

#### 1. コンテナが起動しない
```bash
# Dockerが起動しているか確認
docker version

# 既存のコンテナを削除
docker container prune

# 再度開く
Dev Containers: Rebuild Container
```

#### 2. 拡張機能が動作しない
```bash
# 拡張機能の再インストール
Dev Containers: Rebuild Container Without Cache
```

#### 3. Memory Bankエラー
```bash
# データベース再初期化
rm .claude/index/knowledge.db
python3 .claude/index/sync_markdown.py smart
```

#### 4. 権限エラー
```bash
# ファイル権限修正
sudo chown -R vscode:vscode /workspace
```

### パフォーマンス改善

#### 遅い場合の対処法
1. **Docker設定**
   - Docker Desktop > Settings > Resources
   - CPUs: 4以上
   - Memory: 8GB以上
   - Disk: 20GB以上

2. **キャッシュクリア**
   ```bash
   docker system prune -a
   docker volume prune
   ```

3. **ボリューム最適化**
   - macOSの場合：VirtioFS を有効化
   - Windowsの場合：WSL2 を使用

## カスタマイズ

### 追加のツールをインストール
`post-create.sh`を編集：
```bash
# 例：追加のPythonパッケージ
pip install --user pandas numpy matplotlib
```

### VS Code設定の変更
`devcontainer.json`の`customizations.vscode.settings`を編集

### 新しいサービスの追加
`docker-compose.yml`のコメントアウトされた例を参考に：
- PostgreSQL
- Redis
- Elasticsearch

## ベストプラクティス

### DO ✅
- 定期的にコンテナを再ビルド（月1回程度）
- `.env`ファイルでシークレット管理
- `post-create.sh`でプロジェクト固有の設定
- チーム全体で同じdevcontainer設定を使用

### DON'T ❌
- コンテナ内でグローバルインストール
- `.env`ファイルをコミット
- ホストとコンテナでツールバージョンを混在
- 大きなファイルをコンテナにコピー

## 高度な使い方

### 複数のコンテナを使用
```bash
# docker-compose.ymlを使用
Dev Containers: Reopen in Container
# "From docker-compose.yml"を選択
```

### リモート開発
1. SSH接続設定
2. Remote-SSHでサーバー接続
3. サーバー上でDev Container起動

### CI/CD統合
```yaml
# GitHub Actions例
- uses: devcontainers/ci@v0.3
  with:
    runCmd: |
      python3 -m pytest
      python3 .claude/index/sync_markdown.py smart
```

## 詳細リファレンス

### ファイル構成
```
.devcontainer/
├── devcontainer.json    # メイン設定ファイル
├── docker-compose.yml   # 複数サービス用（オプション）
├── post-create.sh       # 初期化スクリプト
├── .env.example         # 環境変数テンプレート
├── secrets-management.md # シークレット管理ガイド
└── README.md           # このファイル
```

### 環境変数
| 変数名 | 説明 | デフォルト値 |
|--------|------|-------------|
| CLAUDE_HOOKS_ENABLED | Hooks有効化 | true |
| CLAUDE_PROJECT_ROOT | プロジェクトルート | /workspace |
| CLAUDE_MEMORY_BANK_OPTIMIZED | 最適化版使用 | true |
| NODE_ENV | Node環境 | development |
| PYTHONPATH | Pythonパス | 自動設定 |

### ポート転送
必要に応じて`devcontainer.json`の`forwardPorts`に追加：
```json
"forwardPorts": [3000, 5000, 8080]
```

## サポート

### 問題報告
1. `.devcontainer/logs/`のログを確認
2. `docker logs`でコンテナログ確認
3. GitHubでIssue作成

### 更新情報
- 定期的に`.devcontainer/`ディレクトリを確認
- CHANGELOGで変更内容を確認

## 関連ドキュメント
- [VS Code Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers)
- [Docker公式ドキュメント](https://docs.docker.com/)
- [Claude Code ドキュメント](https://docs.anthropic.com/en/docs/claude-code)
- [プロジェクトCLAUDE.md](../CLAUDE.md)