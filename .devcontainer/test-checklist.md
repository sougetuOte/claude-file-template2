# DevContainer 動作確認チェックリスト

## 事前準備
- [ ] Docker Desktopが起動している
- [ ] VS Codeがインストールされている
- [ ] Dev Containers拡張機能がインストールされている
- [ ] プロジェクトがgit cloneされている

## 初回起動テスト

### 1. コンテナビルド
- [ ] VS Codeでプロジェクトを開く
- [ ] 「Reopen in Container」通知が表示される
- [ ] コンテナのビルドが成功する（約3-5分）
- [ ] エラーなくコンテナが起動する

### 2. 基本環境確認
```bash
# ターミナルで実行
- [ ] echo $USER  # "vscode"が表示される
- [ ] pwd         # "/workspace"が表示される
- [ ] python --version  # Python 3.11.xが表示される
- [ ] node --version    # v20.x.xが表示される
- [ ] sqlite3 --version # SQLiteバージョンが表示される
```

### 3. 開発ツール確認
```bash
# Python関連
- [ ] black --version
- [ ] flake8 --version
- [ ] mypy --version
- [ ] pytest --version
- [ ] pip list  # インストール済みパッケージ確認

# その他ツール
- [ ] git --version
- [ ] rg --version  # ripgrep
- [ ] jq --version
```

## Memory Bank機能テスト

### 1. 初期化確認
```bash
- [ ] ls -la .claude/index/  # knowledge.dbが存在する
- [ ] python3 -c "from .claude.index.OptimizedKnowledgeStore import OptimizedKnowledgeStore; print('OK')"
```

### 2. 同期機能テスト
```bash
# インクリメンタル同期
- [ ] python3 .claude/index/sync_markdown.py incremental
      # エラーなく完了する

# スマート同期
- [ ] python3 .claude/index/sync_markdown.py smart
      # 重要ファイルが同期される

# 統計情報表示
- [ ] python3 .claude/index/sync_markdown.py info
      # データベース情報が表示される
```

### 3. 知識検索テスト
```bash
# 検索コマンド
- [ ] python3 .claude/commands/k_command.py search "memory bank"
      # 検索結果が表示される

# リンク追加（オプション）
- [ ] python3 .claude/commands/k_command.py link "test1.md" "test2.md"
      # リンクが作成される
```

## VS Code統合テスト

### 1. 拡張機能確認
- [ ] 拡張機能タブで以下が「インストール済み」になっている：
  - [ ] Python
  - [ ] Pylance
  - [ ] Black Formatter
  - [ ] ESLint
  - [ ] Prettier
  - [ ] GitLens
  - [ ] Markdown All in One

### 2. 言語サポート確認
```python
# test.pyを作成
- [ ] def test():  # 入力時に自動補完が効く
- [ ]     pass     # 自動インデントされる
- [ ] # 保存時に自動フォーマットされる
```

```javascript
// test.jsを作成
- [ ] const test = () => {  // 構文ハイライトが効く
- [ ]   console.log('test') // 自動補完が効く
- [ ] }  // 保存時にPrettierが動作
```

### 3. Markdownサポート
```markdown
# test.mdを作成
- [ ] プレビューが表示できる（Ctrl+Shift+V）
- [ ] リントエラーが表示される
- [ ] 目次が自動生成される
```

## セキュリティ機能テスト

### 1. Hooks動作確認
```bash
# 危険なコマンドのブロック
- [ ] rm -rf /  # ブロックされる
- [ ] sudo apt-get install  # 警告が表示される

# ログ確認
- [ ] ls .claude/logs/  # command_history.logが存在
- [ ] tail .claude/logs/command_history.log  # コマンド履歴が記録されている
```

### 2. ファイル権限確認
```bash
- [ ] ls -la ~/.ssh/  # 読み取り専用でマウントされている
- [ ] touch ~/.ssh/test  # Permission deniedエラー
```

## パフォーマンステスト

### 1. 起動時間測定
- [ ] コンテナ再起動: 30秒以内に利用可能
- [ ] フルリビルド: 5分以内に完了

### 2. メモリ使用量確認
```bash
- [ ] docker stats  # メモリ使用量が2GB以下
```

### 3. ファイル操作速度
```bash
- [ ] time find . -name "*.py" | wc -l  # 1秒以内
- [ ] time rg "test" --type py  # 0.5秒以内
```

## 環境変数・シークレットテスト

### 1. 環境変数確認
```bash
- [ ] echo $CLAUDE_HOOKS_ENABLED  # "true"
- [ ] echo $CLAUDE_PROJECT_ROOT    # "/workspace"
- [ ] echo $NODE_ENV              # "development"
```

### 2. .envファイルテスト
```bash
# .envファイル作成
- [ ] cp .devcontainer/.env.example .devcontainer/.env
- [ ] # .envを編集してテスト値を設定
- [ ] # コンテナ再起動後、値が反映される
```

## 統合テスト

### 1. 開発フロー全体
- [ ] ファイル編集 → 自動保存 → フォーマット適用
- [ ] Pythonファイル作成 → 型チェック → テスト実行
- [ ] Markdownファイル編集 → Memory Bank自動同期
- [ ] Git操作 → pre-commitフック動作

### 2. チーム開発シミュレーション
- [ ] 別のマシンでも同じ環境が再現できる
- [ ] 設定ファイルの共有で同じ開発体験

## トラブルシューティング確認

### エラー時の対処
- [ ] コンテナログが確認できる
- [ ] エラーメッセージが分かりやすい
- [ ] リカバリー手順が明確

## 最終確認

### 総合評価
- [ ] 開発に必要なツールが全て揃っている
- [ ] パフォーマンスが実用的なレベル
- [ ] セキュリティが適切に設定されている
- [ ] チーム開発に適している

## テスト完了後の作業

1. **問題があった場合**
   - ログを収集: `docker logs > devcontainer-test.log`
   - 設定を見直し: `devcontainer.json`の調整
   - ドキュメント更新: 解決方法を記録

2. **成功した場合**
   - チームに展開方法を共有
   - CI/CDへの統合を検討
   - 定期的な更新計画を立てる

---

テスト実施日: ____年____月____日
テスト実施者: ________________
結果: □ 合格 / □ 不合格
備考: _________________________