# テスト・品質・技術負債管理

## テスト要件（段階的TDD学習パス）

### TDD学習ステップ
#### Phase 1 (Week 1-2): TDD体験なし
- 既存コードの理解・修正に集中
- 実装後のテスト追加でもOK
- Claude Codeの基本操作習得

#### Phase 2 (Week 3-4): TDD体験開始
- 小さな機能でTDD体験（Claudeがテスト作成サポート）
- 「まず失敗するテストを書いて」→実装→リファクタリング
- Red-Green-Refactorサイクルを体験

#### Phase 3 (Month 2-3): TDD習得
- 新機能開発時にTDD適用
- 自己デバッグループ（`claude test --fix`）活用
- TDDパターンが自然に身につく

### テスト基準
- **テストフレームワーク**: プロジェクトで統一されたものを使用
- **カバレッジ目標**: 重要な機能は80%以上（段階的に向上）
- **推奨テストケース**: 
  - エッジケース（境界値・異常値）
  - エラーハンドリング
  - 新機能には対応するテスト（TDD習得後は先行作成）
  - バグ修正には回帰テスト

## 技術負債トラッキング

### 基本運用
- **負債ログ**: @.claude/context/debt.md
- **優先度分類**: 高🔥 / 中⚠️ / 低📝
- **コスト試算**: 時間単位で推定、実績記録
- **影響範囲**: ファイル・機能レベルで記載

### キャッシュ影響分析
- **削除必要変更**: 推定追加コストを算出
- **最適化改善**: コスト削減効果を測定
- **TTL管理**: 5分失効を考慮した計画

### 運用ルール
- **新機能開発時**: 潜在的負債を事前予測・記録
- **スプリント終了時**: 発生した負債の優先度付け
- **月1回**: 負債全体の見直し・アーカイブ

### 継続的改善
- **自動検知**: CI/CDでの負債発生監視
- **メトリクス**: 週次での負債増減確認
- **予防策**: コードレビュー・リファクタリングの習慣化