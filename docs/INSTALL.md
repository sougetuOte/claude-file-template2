# インストールガイド - Claude File Template v2.0

## 📋 要件確認

### 必須要件
- **Claude Code**: [公式サイト](https://docs.anthropic.com/en/docs/claude-code)からインストール済み
- **Python**: 3.8以上（Memory Bank機能用）
- **Git**: バージョン管理用

### 確認コマンド
```bash
claude --version    # Claude Codeバージョン確認
python --version    # Python 3.8+ 必須
git --version       # Git確認
```

### オプション要件
- **Node.js**: 18以上（MCP統合機能用）
- **npm/yarn**: Node.jsパッケージ管理
- **Vibe Logger**: AI最適化ログシステム（デバッグ効率化用）

## 🚀 インストール方法

### 方法1: 新規プロジェクト作成

```bash
# 1. テンプレートをクローン
git clone https://github.com/sougetuOte/claude-file-template2.git my-project
cd my-project

# 2. テンプレート用ファイルを削除  
rm -rf .git docs/

# 3. 新しいGitリポジトリとして初期化
git init
git add .
git commit -m "feat: initialize project with Memory Bank 2.0"

# 4. プロジェクト情報を編集
# CLAUDE.mdのプロジェクト情報を更新
# .claude/core/overview.mdの内容を編集
```

### 方法2: 既存プロジェクトへの追加

```bash
# 1. 一時的にテンプレートをクローン
git clone https://github.com/sougetuOte/claude-file-template2.git temp-template

# 2. 既存プロジェクトに必要ファイルをコピー
cp -r temp-template/.claude ./
cp temp-template/CLAUDE.md ./
cp temp-template/.gitignore ./.gitignore.new

# 3. 設定ファイルをマージ（必要に応じて）
cat .gitignore.new >> .gitignore
rm .gitignore.new

# 4. 一時ファイルを削除
rm -rf temp-template

# 5. プロジェクト固有の設定
# CLAUDE.mdを編集してプロジェクト情報を更新
```

## ⚙️ 初期設定

### 1. プロジェクト情報の設定

```bash
# CLAUDE.mdを編集
nano CLAUDE.md
```

以下を更新：
- プロジェクト名
- プロジェクト概要
- 技術スタック
- 実行コマンド

### 2. Memory Bank初期化

```bash
# 知識ベースの初期化（自動作成）
python .claude/commands/k_command.py list

# 初期設定の確認
python .claude/index/knowledge_store.py
```

### 3. コア情報の編集

```bash
# 現在状況ファイルの編集
nano .claude/core/current.md      # 現在の作業状況
nano .claude/core/next.md         # 次のアクション
nano .claude/core/overview.md     # プロジェクト概要
```

## 🔧 オプション機能の設定

### Vibe Logger統合（AI最適化ログシステム）

```bash
# Python版のインストール
pip install vibelogger

# Node.js/TypeScript版のインストール
npm install -g vibelogger

# インストール確認
python -c "import vibelogger; print('Python版: OK')"
node -e "require('vibelogger'); console.log('Node.js版: OK')"

# CLIツールのテスト
python .claude/vibe/sync_vibe_logs.py --help

# 使用例の実行（オプション）
python .claude/vibe/example_usage.py
node .claude/vibe/example_usage.ts
```

#### DevContainerを使用する場合
DevContainerでは自動的にインストールされるため、手動インストールは不要です。

### MCP統合（Phase 2機能）

```bash
# Node.js依存関係のインストール
cd .claude/mcp/memory-server
npm install

# MCP設定ファイルの確認
cat .claude/mcp/config.json

# MCPサーバーテスト
node .claude/mcp/memory-server/index.js test
```

### 自動化Hooksの有効化

```bash
# Hooks設定確認
cat .claude/hooks.yaml

# 必要に応じてHooksの有効/無効を調整
nano .claude/hooks.yaml
```

## ✅ インストール確認

### 基本機能テスト

```bash
# 1. 知識管理システム
python .claude/commands/k_command.py add "Test" "Installation test" "memo"
python .claude/commands/k_command.py search "test"

# 2. コード品質監視
python .claude/quality/code_monitor.py test

# 3. タスクコーディネーター
python .claude/agents/simple_coordinator.py test

# 4. 知識自動整理
python .claude/index/auto_organize.py test

# 5. セキュリティ機能
python .claude/scripts/test_security.py
```

### Claude Codeでの動作確認

```bash
# Claude Codeを起動
claude

# Memory Bankコマンドテスト
/k search "test"
/debug:start
/feature:plan
```

## 🚨 トラブルシューティング

### Python関連エラー

```bash
# Pythonパスエラーの場合
export PYTHONPATH="${PYTHONPATH}:$(pwd)/.claude/index"

# 権限エラーの場合
chmod +x .claude/commands/*.py
chmod +x .claude/quality/*.py
chmod +x .claude/agents/*.py
```

### SQLiteエラー

```bash
# SQLiteデータベースの再初期化
rm .claude/index/knowledge.db
python .claude/index/knowledge_store.py
```

### MCP接続エラー

```bash
# Node.js依存関係の再インストール
cd .claude/mcp/memory-server
rm -rf node_modules package-lock.json
npm install

# MCPサーバーの手動起動
node index.js
```

### ファイル権限エラー

```bash
# .claudeディレクトリの権限修正
chmod -R 755 .claude/
find .claude/ -name "*.py" -exec chmod +x {} \;
```

## 🔄 アップデート手順

### テンプレートの更新

```bash
# 1. 現在の設定をバックアップ
cp -r .claude .claude.backup
cp CLAUDE.md CLAUDE.md.backup

# 2. 最新テンプレートを取得
git clone https://github.com/sougetuOte/claude-file-template2.git temp-update

# 3. 新機能をマージ
# 新しいファイルのみコピー（既存設定は保持）
rsync -av --ignore-existing temp-update/.claude/ .claude/

# 4. 一時ファイル削除
rm -rf temp-update
```

### v1.2からのマイグレーション

詳細は [MIGRATION.md](MIGRATION.md) を参照

## 💡 推奨設定

### VS Code統合

```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "python3",
  "files.associations": {
    "*.md": "markdown",
    ".clauderules": "text"
  }
}
```

### Gitフック

```bash
# プリコミットフックの設定
echo "python .claude/quality/code_monitor.py check \$CHANGED_FILES" > .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## 📞 サポート

- **Issues**: [GitHub Issues](https://github.com/sougetuOte/claude-file-template2/issues)
- **Documentation**: [USER_GUIDE.md](USER_GUIDE.md)
- **Migration**: [MIGRATION.md](MIGRATION.md)

---

**インストール完了後は [USER_GUIDE.md](USER_GUIDE.md) で使い方を確認してください** 📚