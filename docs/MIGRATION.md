# マイグレーションガイド - v1.2 → v2.0

v1.2からMemory Bank 2.0への移行手順とアップグレード方法を説明します。

## 📋 移行前の確認

### 現在バージョンの確認
```bash
# .claudeディレクトリの存在確認
ls -la .claude/

# 既存設定の確認
cat CLAUDE.md 2>/dev/null || echo "CLAUDE.md not found"
```

### バックアップ作成
```bash
# 重要: 移行前に必ずバックアップを作成
cp -r .claude .claude.backup.$(date +%Y%m%d)
cp CLAUDE.md CLAUDE.md.backup.$(date +%Y%m%d) 2>/dev/null || true

# プロジェクト全体のバックアップ（推奨）
git add . && git commit -m "backup: before v2.0 migration"
```

## 🚀 移行パターン

### パターン1: 段階的移行（推奨）

#### Step 1: Memory Bank 2.0のダウンロード
```bash
# 一時ディレクトリに v2.0 をダウンロード
git clone https://github.com/sougetuOte/claude-file-template2.git temp-v2

# 新機能ディレクトリを追加
cp -r temp-v2/.claude/index ./claude/
cp -r temp-v2/.claude/mcp ./claude/
cp -r temp-v2/.claude/quality ./claude/
cp -r temp-v2/.claude/agents ./claude/
cp -r temp-v2/.claude/commands ./claude/
```

#### Step 2: 設定ファイルのマージ
```bash
# hooks.yamlの統合
if [ -f .claude/hooks.yaml ]; then
    echo "# === v1.2 existing hooks ===" >> temp-hooks.yaml
    cat .claude/hooks.yaml >> temp-hooks.yaml
    echo "# === v2.0 new hooks ===" >> temp-hooks.yaml
    cat temp-v2/.claude/hooks.yaml >> temp-hooks.yaml
    mv temp-hooks.yaml .claude/hooks.yaml
else
    cp temp-v2/.claude/hooks.yaml .claude/
fi

# ガイドラインの更新
cp -r temp-v2/.claude/guidelines .claude/
```

#### Step 3: 既存データの移行
```bash
# Python環境の確認
python --version | grep -E "3\.[8-9]|3\.[1-9][0-9]" || echo "Warning: Python 3.8+ required"

# 知識ベースの初期化
python .claude/index/knowledge_store.py

# 既存メモの移行（手動）
# .claude/core/*.md の内容を知識ベースに登録
python .claude/commands/k_command.py add "Current Status" "$(cat .claude/core/current.md)" "status"
python .claude/commands/k_command.py add "Next Actions" "$(cat .claude/core/next.md)" "planning"
```

#### Step 4: 動作確認
```bash
# 基本機能テスト
python .claude/commands/k_command.py test
python .claude/quality/code_monitor.py test
python .claude/agents/simple_coordinator.py test

# Claude Codeでの確認
claude
# /k search "test" でテスト
```

### パターン2: 完全移行

#### 既存設定の保存
```bash
# 重要な設定を別途保存
mkdir migration-data
cp .claude/core/* migration-data/ 2>/dev/null || true
cp .claude/context/* migration-data/ 2>/dev/null || true
cp CLAUDE.md migration-data/ 2>/dev/null || true
```

#### v2.0の導入
```bash
# 既存 .claude を削除（バックアップ済み前提）
rm -rf .claude

# v2.0の .claude をコピー
cp -r temp-v2/.claude ./
cp temp-v2/CLAUDE.md ./

# プロジェクト固有情報の復元
# migration-data/ から必要な情報を手動で .claude/ に復元
```

## ⚙️ 設定の移行

### CLAUDE.mdの更新

#### v1.2の設定を確認
```bash
# 既存のプロジェクト情報を確認
grep -A 5 "プロジェクト概要" CLAUDE.md.backup.* || true
```

#### v2.0形式への更新
```bash
# プロジェクト名・概要を更新
vi CLAUDE.md

# 必要に応じて以下のセクションを更新：
# - プロジェクト概要
# - 技術スタック 
# - 実行コマンド一覧
# - プロジェクトデータ
```

### Memory Bankコアファイルの移行

#### 既存ファイルの内容確認
```bash
# v1.2の重要情報を確認
head -20 .claude.backup.*/core/current.md
head -20 .claude.backup.*/core/next.md
head -20 .claude.backup.*/core/overview.md
```

#### v2.0への適用
```bash
# 新しいテンプレートを基に既存内容をマージ
# 以下のファイルを手動編集：
vi .claude/core/current.md     # 現在の状況
vi .claude/core/next.md        # 次のアクション
vi .claude/core/overview.md    # プロジェクト概要
```

## 🔧 新機能の有効化

### Memory Bank機能
```bash
# Python依存関係の確認
python -c "import sqlite3; print('SQLite OK')"

# 知識ベースの初期化
python .claude/index/knowledge_store.py

# 最初の知識を追加
python .claude/commands/k_command.py add "Migration Complete" "v1.2からv2.0への移行完了" "milestone"
```

### MCP統合（オプション）
```bash
# Node.js環境の確認
node --version | grep -E "v1[8-9]|v[2-9][0-9]" || echo "Node.js 18+ recommended for MCP"

# MCP依存関係のインストール
cd .claude/mcp/memory-server
npm install

# MCP機能テスト
node index.js test
```

### 自動化Hooks
```bash
# Hooksの有効性確認
python .claude/quality/code_monitor.py check README.md

# 必要に応じてHooksを調整
vi .claude/hooks.yaml
```

## 🚨 トラブルシューティング

### よくある問題

#### 1. Python関連エラー
```bash
# パス問題の解決
export PYTHONPATH="${PYTHONPATH}:$(pwd)/.claude/index"

# 権限問題の解決
chmod +x .claude/commands/*.py
chmod +x .claude/quality/*.py
chmod +x .claude/agents/*.py
```

#### 2. SQLiteエラー
```bash
# データベースの再作成
rm .claude/index/knowledge.db 2>/dev/null || true
python .claude/index/knowledge_store.py
```

#### 3. 設定ファイルの競合
```bash
# hooks.yamlの確認
python -c "import yaml; yaml.safe_load(open('.claude/hooks.yaml'))" && echo "YAML OK"

# 問題がある場合はサンプルをコピー
cp temp-v2/.claude/hooks.yaml .claude/hooks.yaml
```

#### 4. 既存データの消失
```bash
# バックアップからの復元
cp -r .claude.backup.*/* .claude/ 2>/dev/null || true

# 手動で重要データを復元
vi .claude/core/current.md  # バックアップ内容を参考に復元
```

## 📊 移行後の確認

### 機能テスト
```bash
# 1. 基本Memory Bank機能
python .claude/commands/k_command.py list
python .claude/commands/k_command.py search "*"

# 2. コード品質監視
python .claude/quality/code_monitor.py test

# 3. タスクコーディネーター
python .claude/agents/simple_coordinator.py test

# 4. 知識自動整理
python .claude/index/auto_organize.py test
```

### Claude Codeでの動作確認
```bash
claude
# 以下のコマンドをテスト：
# /k search "migration"
# /debug:start
# /feature:plan
# /project:plan
```

### パフォーマンス確認
```bash
# 知識ベース統計
python .claude/index/auto_organize.py stats

# 期待される結果例：
# {
#   "total_items": 3-10,
#   "health_score": 60-100,
#   "recent_activity": {...}
# }
```

## 🔄 ロールバック手順

移行に問題がある場合のロールバック：

```bash
# 1. 現在の状態を保存
mv .claude .claude.v2-failed

# 2. v1.2バックアップの復元
cp -r .claude.backup.* .claude
cp CLAUDE.md.backup.* CLAUDE.md

# 3. Git履歴の確認
git log --oneline -5

# 4. 必要に応じてGitリセット
git reset --hard HEAD~1  # 移行コミット前に戻る
```

## 📈 移行後の活用

### 段階的機能活用
1. **Week 1**: 基本知識管理（/k search, /k add）
2. **Week 2**: モード切り替え（/debug:start, /feature:plan）
3. **Week 3**: 自動化機能（Hooks、自動整理）
4. **Week 4**: MCP統合（高度な機能）

### 設定の最適化
```bash
# プロジェクト固有の調整
vi .claude/core/overview.md      # プロジェクト情報の詳細化
vi .claude/context/tech.md       # 技術スタック詳細
vi .claude/hooks.yaml           # プロジェクト固有の自動化
```

## 📞 サポート

- **移行支援**: [GitHub Issues](https://github.com/sougetuOte/claude-file-template2/issues)で"migration"ラベル付きで質問
- **ドキュメント**: [USER_GUIDE.md](USER_GUIDE.md)で詳細機能を確認
- **コミュニティ**: 他のユーザーの移行事例を参考

---

**Memory Bank 2.0への移行で、AI開発効率を次のレベルへ** 🚀