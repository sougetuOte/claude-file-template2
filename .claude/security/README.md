# Claude Code セキュリティガイド

## 概要
このプロジェクトでは、Claude Code の `--dangerously-skip-permissions` オプションを安全に使用するためのセキュリティ対策を実装しています。

## 実装済みセキュリティ機能

### 1. 包括的なコマンド制御 (`settings.json`)

#### Allow + Deny方式によるバランス設定
```json
{
  "permissions": {
    "allow": [
      // 開発で頻繁に使用する安全なコマンド
      "Bash(git status)", "Bash(git log*)", "Bash(git diff*)",
      "Bash(npm run*)", "Bash(python -m*)", "Bash(pip list)",
      "Bash(docker ps*)", "Bash(docker logs*)",
      "Bash(ls*)", "Bash(cat*)", "Bash(grep*)", "Bash(find*)",
      "Bash(rg*)", "Bash(fd*)", "Bash(batcat*)", "Bash(eza*)",
      "Bash(curl -s*)", "Bash(wget -q*)", // 読み取り専用
      "Bash(tmux*)", "Bash(screen*)", // 対話的使用
      // ... 200+の開発用コマンド
    ],
    "deny": [
      // 特定の危険なパターンのみをブロック
      "Bash(sudo *)", "Bash(rm -rf /*)", "Bash(chmod 777 *)",
      "Bash(curl -X POST*)", "Bash(curl -d*)", // 書き込み操作
      "Bash(wget -O*)", "Bash(wget --post-data*)",
      "Bash(git config --global *)", "Bash(systemctl *)",
      "Bash(pkill -9*)", "Bash(kill -9 *)", // 強制終了
      "Bash(nohup * &)", // バックグラウンド実行
      // ... 危険パターンのみ
    ]
  }
}
```

#### 設計思想
- **Allow優先**: よく使うコマンドは許可リストで高速処理
- **Deny補完**: 許可リスト内の危険なパターンのみブロック
- **UX最適化**: 開発者の作業を阻害しない設定
- **セキュリティ**: 破壊的・悪意のある操作は確実にブロック

### 2. PreToolUseフック (`bash_security_validator.py`)
- コマンド実行前の詳細検証
- 段階的なセキュリティレベル（BLOCK/WARNING/INFO/ALLOW）
- 日本語でのわかりやすい警告メッセージ

### 3. コマンドログ記録 (`hooks.yaml`)
- 全てのbashコマンドの実行ログ
- 危険なコマンドの特別なアラート
- セキュリティイベントの詳細記録

## セキュリティレベル

### 🚫 BLOCK (実行禁止)
以下のコマンドは実行がブロックされます：
- `sudo`, `su` - 権限昇格
- `rm -rf /`, `rm -rf ~/` - 破壊的削除
- `chmod 777` - 危険な権限変更
- `curl`, `wget` - 外部ネットワークアクセス
- `systemctl`, `service` - システムサービス操作
- `crontab`, `at` - スケジュール操作

### ⚠️ WARNING (注意が必要)
以下のコマンドは警告付きで実行されます：
- `git push --force` - 強制プッシュ
- `git reset --hard` - ハードリセット
- `docker rm`, `docker rmi` - コンテナ/イメージ削除
- `npm uninstall`, `pip uninstall` - パッケージ削除

### 💡 INFO (改善提案)
以下のコマンドに対して推奨コマンドを提案します：
- `grep` → `rg` (ripgrep)
- `find -name` → `fd`
- `cat` → `batcat`
- `ls` → `eza --icons --git`

## セキュリティテスト

### テストの実行
```bash
python3 .claude/scripts/test_security.py
```

### 手動テスト例
```bash
# 安全なコマンドのテスト
echo '{"tool": "Bash", "command": "echo hello"}' | python3 .claude/scripts/bash_security_validator.py

# 危険なコマンドのテスト
echo '{"tool": "Bash", "command": "sudo rm -rf /"}' | python3 .claude/scripts/bash_security_validator.py
```

## ログファイル

### セキュリティログ
- **場所**: `.claude/logs/security.log`
- **内容**: セキュリティイベントの詳細記録
- **形式**: `[TIMESTAMP] [LEVEL] MESSAGE`

### コマンド履歴ログ
- **場所**: `.claude/logs/command_history.log`
- **内容**: 全てのbashコマンドの実行記録
- **形式**: `[TIMESTAMP] [EXIT_CODE] COMMAND`

## 緊急時の対応

### セキュリティフックの無効化
```bash
# 一時的に無効化
export CLAUDE_HOOKS_ENABLED=false

# 設定ファイルで無効化
# .claude/settings.json から hooks セクションを削除
```

### 問題のあるコマンドが実行された場合
1. すぐに実行を中止（Ctrl+C）
2. セキュリティログを確認
3. 必要に応じてシステムの状態を確認
4. インシデントレポートを作成

## カスタマイズ

### 独自のセキュリティルール追加
`bash_security_validator.py` の以下の配列を編集：
- `dangerous_patterns`: ブロックするパターン
- `warning_patterns`: 警告するパターン
- `improvement_suggestions`: 改善提案パターン
- `whitelist_patterns`: 明示的に許可するパターン

### 新しいセキュリティチェックの追加
1. `.claude/scripts/` にスクリプトを作成
2. `hooks.yaml` に新しいフックを追加
3. `test_security.py` にテストケースを追加

## ベストプラクティス

### 開発時
1. 定期的にセキュリティログを確認
2. 新しいコマンドパターンが安全か事前に検証
3. テストは隔離された環境で実行

### 本番環境
1. セキュリティフックは必ず有効化
2. ログの定期的な監視
3. 異常なコマンド実行の即座の調査

## 参考リンク
- [Claude Code 公式セキュリティドキュメント](https://docs.anthropic.com/en/docs/claude-code/security)
- [wasabeef.jp - Claude Code Secure Bash](https://wasabeef.jp/blog/claude-code-secure-bash)
- [Claude Code Hooks ドキュメント](https://docs.anthropic.com/en/docs/claude-code/hooks)

## 更新履歴
- 2025-07-09: 初版作成、基本的なセキュリティ機能実装