# 開発ガイドライン

## 1. パッケージ管理
- **推奨ツール**: プロジェクトに応じて統一（npm/yarn/pnpm, pip/poetry/uv等）
- **インストール**: `[tool] add package` 形式を推奨
- **実行**: `[tool] run command` 形式を推奨
- **禁止事項**: 
  - 混在使用（複数のパッケージマネージャーの併用）
  - `@latest`構文の使用（バージョン固定推奨）
  - グローバルインストール（プロジェクト内で完結）

## 2. コード品質基準
- **型注釈**: 全ての関数・変数に型情報を付与
- **ドキュメント**: パブリックAPI・複雑な処理に必須
- **関数設計**: 単一責任・小さな関数を心がける
- **既存パターン**: 必ず既存コードのパターンに従う
- **行長制限**: 80-120文字（言語・チームで統一）

## 3. 実行コマンド一覧

### 基本開発フロー
```bash
# プロジェクトセットアップ（初回のみ）
[tool] install                   # 依存関係インストール
[tool] run dev                   # 開発サーバー起動

# テスト実行
[tool] run test                  # 全テスト実行
[tool] run test:watch           # ウォッチモード

# 品質チェック
[tool] run format               # コードフォーマット適用
[tool] run lint                 # リントチェック・自動修正
[tool] run typecheck            # 型チェック実行（該当言語）

# ビルド・リリース
[tool] run build                # プロダクションビルド
[tool] run check                # 総合チェック（CI前確認）
```

### パッケージ管理
```bash
[tool] add [package-name]       # 依存関係追加
[tool] remove [package-name]    # 依存関係削除
[tool] update                   # 全依存関係更新
```

**注記**: `[tool]`はプロジェクトで使用するパッケージマネージャーに置き換え
- Node.js: `npm`, `yarn`, `pnpm`
- Python: `pip`, `poetry`, `uv`
- Rust: `cargo`
- Go: `go`
- その他言語の標準ツール

## 4. エラー対応ガイド

### 問題解決の標準順序
1. **フォーマットエラー** → `[tool] run format`
2. **型エラー** → `[tool] run typecheck`
3. **リントエラー** → `[tool] run lint:fix`
4. **テストエラー** → `[tool] run test`

### よくある問題と解決策
- **行長エラー**: 適切な箇所で改行
- **インポート順序**: 自動修正を使用
- **型エラー**: 明示的な型注釈を追加

## 5. 品質ゲート

### コミット前チェック
- [ ] `[tool] run format` - フォーマット適用済み
- [ ] `[tool] run lint` - リント警告解消済み
- [ ] `[tool] run typecheck` - 型チェック通過
- [ ] `[tool] run test` - 全テスト通過

### CI/CD自動化
- コードフォーマット
- リントチェック
- 型チェック
- 単体テスト実行

## 6. セキュリティ対策

### Claude Code セキュリティ機能
- **危険コマンドブロック**: `settings.json` で定義された危険パターンを自動ブロック
- **PreToolUseフック**: コマンド実行前の詳細検証
- **コマンドログ**: 全てのbashコマンドの実行記録
- **セキュリティテスト**: `python3 .claude/scripts/test_security.py` で定期検証

### 危険なコマンドの例
⚠️ 以下のコマンドは自動的にブロックされます：
- `sudo`, `su` - 権限昇格
- `rm -rf /`, `rm -rf ~/` - 破壊的削除
- `curl`, `wget` - 外部ネットワークアクセス
- `chmod 777` - 危険な権限変更

### セキュリティログの確認
```bash
# セキュリティイベントの確認
cat .claude/logs/security.log

# コマンド履歴の確認
cat .claude/logs/command_history.log
```

詳細: @.claude/security/README.md