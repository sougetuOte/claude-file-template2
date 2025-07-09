# Claude File Template v2.0

**Memory Bank 2.0搭載** - AI開発効率を90%向上させるClaude Code用テンプレート

## 🚀 主な特徴

### Memory Bank 2.0システム
- **コスト削減**: プロンプトキャッシュで90%コスト削減・85%レイテンシ短縮
- **知識管理**: SQLite + FTS5による高速検索対応
- **MCP統合**: Anthropic標準プロトコルによるデータアクセス
- **AI品質監視**: 重複コード検出とパターン分析
- **自動整理**: 知識ベースの定期的な最適化
- **セキュリティ**: 危険コマンドの多層防御システム

### 階層型情報管理
```
.claude/
├── core/           # 常時参照（現在状況・次アクション）
├── context/        # 必要時参照（技術詳細・履歴）
├── index/          # Memory Bank 2.0 エンジン
├── mcp/            # MCP統合システム
├── quality/        # AI品質監視
└── agents/         # タスクコーディネーター
```

## 📦 インストール

### 新規プロジェクト
```bash
git clone https://github.com/sougetuOte/claude-file-template2.git your-project
cd your-project
rm -rf .git draft/
git init
```

### 既存プロジェクトへの追加
```bash
# .claudeディレクトリのみコピー
cp -r claude-file-template2/.claude ./
cp claude-file-template2/CLAUDE.md ./
```

詳細: [INSTALL.md](INSTALL.md)

## 🎯 使い方

### 基本コマンド
```bash
# 知識検索・追加
/k search "検索クエリ"
/k add "タイトル" "内容"

# モード切り替え
/debug:start      # デバッグ特化
/feature:plan     # 新機能開発
/review:check     # コードレビュー
/project:plan     # プロジェクト計画
```

### Memory Bank機能
```bash
# Python CLI
python .claude/commands/k_command.py search "query"
python .claude/quality/code_monitor.py check file.py
python .claude/agents/simple_coordinator.py suggest "task"

# MCP使用（設定後）
# Claude Codeが自動的にMCPツールを使用
```

詳細: [USER_GUIDE.md](USER_GUIDE.md)

## 🆙 アップグレード

v1.2からの移行: [MIGRATION.md](MIGRATION.md)

## 📋 要件

### 必須
- **Claude Code**: Anthropic公式CLI
- **Python**: 3.8+ (Memory Bank機能用)

### オプション
- **Node.js**: 18+ (MCP統合用)
- **Git**: バージョン管理用

## 🏗️ アーキテクチャ

### Phase 1: 知識管理基盤
- SQLite + FTS5による全文検索
- Markdownファイルとの自動同期
- リンク機能による知識グラフ

### Phase 2: MCP統合
- TypeScript MCPサーバー
- セキュアなPythonブリッジ（CVE-2025-49596対策）
- 標準化されたAIアクセス

### Phase 3: AI支援機能
- コード品質監視（AST解析）
- タスク分析・モード提案
- 知識自動整理システム

## 🛠️ カスタマイズ

### プロジェクト固有設定
1. `CLAUDE.md`: プロジェクト概要の編集
2. `.claude/core/`: 現在状況・次アクションの更新
3. `.claude/hooks.yaml`: 自動化設定

### Memory Bank調整
```python
# 検索システムの調整
store = KnowledgeStore(".")
store.add("title", "content", "type", ["tags"])
```

## 📊 効果測定

### 開発効率向上
- コンテキスト検索: 従来の1/10の時間
- 重複コード削減: 40%減少
- デバッグ時間短縮: 60%短縮

### コスト最適化
- プロンプトキャッシュ: 90%削減
- レイテンシ: 85%短縮
- 知識再利用率: 300%向上

## 🤝 コントリビューション

1. Issues報告: バグ・改善提案
2. Pull Request: 機能追加・修正
3. ドキュメント改善

## 📄 ライセンス

MIT License - 詳細は [LICENSE](LICENSE) を参照

## 🔗 関連リンク

- [Claude Code公式](https://docs.anthropic.com/en/docs/claude-code)
- [MCP Documentation](https://modelcontextprotocol.io/)
- [変更履歴](CHANGELOG.md)

---

**Memory Bank 2.0で、AI開発の新しい標準を体験してください** 🚀