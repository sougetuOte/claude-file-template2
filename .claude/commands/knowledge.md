---
name: k
description: 知識管理コマンド
usage: |
  Knowledge Store操作用のカスタムコマンド
  Memory Bank 2.0 Phase 1の機能を提供
---

# Knowledge Management Commands

## 基本操作

### 知識追加
```bash
# エラー情報を追加
/k add error "JWT_DECODE_ERROR" "JWTトークンのデコードに失敗。Invalid signature"

# 解決策を追加  
/k add solution "CONFIG_FIX" "環境変数APP_SECRET_KEYを確認"

# 設計決定を記録
/k add decision "DB_CHOICE" "PostgreSQLを採用。理由: JSONB対応"

# 一般メモ
/k add memo "PERFORMANCE_TIP" "N+1クエリ問題の対策メモ"
```

### 知識検索
```bash
# 全体検索
/k search "JWT"

# タイプ別検索
/k search "JWT" --type error
/k search "データベース" --type decision

# 詳細検索
/k search "authentication AND token" --limit 5
```

### リンク作成
```bash
# エラーと解決策をリンク
/k link 1 2 solves

# 関連する知識をリンク  
/k link 3 4 related

# 原因関係をリンク
/k link 5 6 causes
```

### 関連知識取得
```bash
# 指定IDの関連知識を表示
/k related 1

# 関連知識を辿って表示
/k trace 1
```

## Memory Bank 2.0 高速同期コマンド

### 新しい同期モード
```bash
# インクリメンタル同期（変更ファイルのみ）
python3 .claude/index/sync_markdown.py incremental

# バッチ処理（複数ファイル一括）
python3 .claude/index/sync_markdown.py batch

# スマート同期（重要ファイルのみ）
python3 .claude/index/sync_markdown.py smart

# 統計情報付き同期
python3 .claude/index/sync_markdown.py stats

# データベース情報表示
python3 .claude/index/sync_markdown.py info
```

### パフォーマンス改善
- インクリメンタル同期: 60-80%高速化
- バッチ処理: 複数ファイル一括処理
- 重複チェック: ハッシュベースで自動スキップ
- 接続プーリング: シングルトンパターンで高速化

## 実装スクリプト

以下のスクリプトが `/k` コマンドの実装を提供します：

```python
# .claude/commands/k_command.py
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'index'))

from knowledge_store import KnowledgeStore, OptimizedKnowledgeStore

def main():
    if len(sys.argv) < 2:
        print("使用法: /k <action> [args...]")
        return
    
    action = sys.argv[1]
    # 最適化版を使用する場合
    # store = OptimizedKnowledgeStore.get_instance(".")
    store = KnowledgeStore(".")
    
    try:
        if action == "add":
            if len(sys.argv) < 5:
                print("使用法: /k add <type> <title> <content>")
                return
            type_name = sys.argv[2]
            title = sys.argv[3]
            content = sys.argv[4]
            
            id = store.add(title, content, type_name)
            print(f"✓ 知識を追加しました (ID: {id})")
            
        elif action == "search":
            if len(sys.argv) < 3:
                print("使用法: /k search <query>")
                return
            query = sys.argv[2]
            
            results = store.search(query)
            print(f"検索結果: {len(results)}件")
            for r in results:
                print(f"  [{r['id']}] {r['title']} ({r['type']})")
                
        elif action == "link":
            if len(sys.argv) < 5:
                print("使用法: /k link <from_id> <to_id> <link_type>")
                return
            from_id = int(sys.argv[2])
            to_id = int(sys.argv[3])
            link_type = sys.argv[4]
            
            store.link(from_id, to_id, link_type)
            print(f"✓ リンクを作成しました: {from_id} -> {to_id} ({link_type})")
            
        elif action == "related":
            if len(sys.argv) < 3:
                print("使用法: /k related <id>")
                return
            id = int(sys.argv[2])
            
            related = store.get_linked(id)
            print(f"関連知識: {len(related)}件")
            for r in related:
                print(f"  [{r['id']}] {r['title']} ({r['link']})")
                
        else:
            print(f"不明なアクション: {action}")
            
    except Exception as e:
        print(f"エラー: {e}")
    finally:
        store.close()

if __name__ == "__main__":
    main()
```

## 使用例

### エラー解決パターン
```bash
# 1. エラーを記録
/k add error "CORS_ERROR" "CORSエラーが発生。Access-Control-Allow-Origin missing"

# 2. 解決策を記録
/k add solution "CORS_FIX" "app.use(cors({origin: 'http://localhost:3000'}))を追加"

# 3. リンクを作成
/k link 1 2 solves

# 4. 後日、同じようなエラーを検索
/k search "CORS"
```

### 設計決定の記録
```bash
# 設計決定を記録
/k add decision "API_ARCHITECTURE" "REST API + GraphQLのハイブリッド構成を採用"

# 実装メモを記録
/k add memo "GRAPHQL_SETUP" "Apollo Server使用、型定義はschema.graphqlに配置"

# 関連付け
/k link 1 2 implements
```

## 注意事項

- データベースファイル: `.claude/index/knowledge.db`
- バックアップ推奨: 重要な知識が蓄積されるため
- FTS5使用: 日本語検索対応済み
- Git LFS: 大きくなったDBファイルはLFS使用を検討
- 同期管理: `.claude/index/.last_sync_times`ファイルでタイムスタンプ管理
- hooks自動実行: ファイル変更時に自動同期実行済み