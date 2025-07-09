---
cache_control: {"type": "ephemeral"}
---
# Technical Context

## アーキテクチャ概要
```
Memory Bank 2.0 最適化アーキテクチャ

.claude/
├── hooks.yaml (最適化済みhooks)
├── index/
│   ├── knowledge.db (SQLite + FTS5)
│   ├── knowledge_store.py (従来版)
│   ├── OptimizedKnowledgeStore (新版)
│   ├── sync_markdown.py (高速同期)
│   └── .last_sync_times (同期管理)
└── commands/
    └── k_command.py (知識管理CLI)

同期フロー:
1. ファイル変更検知 (hooks)
2. インクリメンタル判定
3. バッチ処理実行
4. 重複チェック
5. SQLite挿入
```

## 技術スタック詳細
### フロントエンド
- [フレームワーク] v[バージョン]
- [ライブラリ1] v[バージョン] - [用途]
- [ライブラリ2] v[バージョン] - [用途]

### バックエンド
- [言語] v[バージョン]
- [フレームワーク] v[バージョン]
- [重要ライブラリ] v[バージョン] - [用途]

### インフラ・ツール
- [DB] v[バージョン]
- [その他重要ツール]

## 開発環境
```bash
# セットアップ手順
[コマンド1]
[コマンド2]
[コマンド3]
```

## 起動手順
```bash
# 開発環境
[起動コマンド]

# 本番環境
[デプロイコマンド]
```

## API設計
### 主要エンドポイント
- `GET /api/[resource]` - [用途]
- `POST /api/[resource]` - [用途]
- `PUT /api/[resource]/:id` - [用途]
- `DELETE /api/[resource]/:id` - [用途]

## データベース設計
### 主要テーブル
- `[table1]`: [用途]
- `[table2]`: [用途]

## 設定ファイル
- `.claude/hooks.yaml`: Claude Code hooks設定（最適化済み）
- `.claude/index/knowledge.db`: SQLite知識データベース
- `.claude/index/.last_sync_times`: 同期時刻管理ファイル
- `.claude/settings.json`: Claude Code設定ファイル

## パフォーマンス要件
- Memory Bank同期: 0.1秒以内（インクリメンタル）
- バッチ処理: 複数ファイル一括処理対応
- 重複チェック: ハッシュベース高速判定
- データベース接続: シングルトンパターンによる最適化

## セキュリティ考慮事項
- [考慮事項1]
- [考慮事項2]

## 已知の制約・課題
- SQLiteファイルサイズ: 大量データ時はバックアップ必須
- FTS5日本語検索: トークン化の精度限界
- hooks実行頻度: 過度な実行を避けるための最適化実施済み
- 接続プーリング: シングルトンパターンによる管理