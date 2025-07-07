#!/usr/bin/env python3
"""
Knowledge Management Command Implementation
Memory Bank 2.0 Phase 1

Usage: python k_command.py <action> [args...]
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'index'))

from knowledge_store import KnowledgeStore

def print_usage():
    """使用方法を表示"""
    print("""
Knowledge Management Commands:

  add <type> <title> <content>  - 知識を追加
    types: error, solution, decision, memo
    
  search <query> [--type <type>] [--limit <n>] - 知識を検索
  
  link <from_id> <to_id> <link_type> - 知識をリンク
    link_types: solves, causes, related, implements
    
  related <id>  - 関連知識を表示
  
  list [--type <type>] [--limit <n>] - 知識一覧を表示

Examples:
  python k_command.py add error "JWT_ERROR" "Invalid token signature"
  python k_command.py search "JWT" --type error
  python k_command.py link 1 2 solves
  python k_command.py related 1
""")

def main():
    if len(sys.argv) < 2:
        print_usage()
        return
    
    action = sys.argv[1]
    store = KnowledgeStore(".")
    
    try:
        if action == "add":
            if len(sys.argv) < 5:
                print("エラー: 引数が不足しています")
                print("使用法: add <type> <title> <content>")
                return
                
            type_name = sys.argv[2]
            title = sys.argv[3]
            content = sys.argv[4]
            
            # 有効なタイプをチェック
            valid_types = ["error", "solution", "decision", "memo", "code", "concept"]
            if type_name not in valid_types:
                print(f"エラー: 無効なタイプ '{type_name}'")
                print(f"有効なタイプ: {', '.join(valid_types)}")
                return
            
            id = store.add(title, content, type_name)
            print(f"✓ 知識を追加しました")
            print(f"  ID: {id}")
            print(f"  タイトル: {title}")
            print(f"  タイプ: {type_name}")
            
        elif action == "search":
            if len(sys.argv) < 3:
                print("エラー: 検索クエリが必要です")
                print("使用法: search <query> [--type <type>] [--limit <n>]")
                return
                
            query = sys.argv[2]
            type_filter = None
            limit = 10
            
            # オプション解析
            i = 3
            while i < len(sys.argv):
                if sys.argv[i] == "--type" and i + 1 < len(sys.argv):
                    type_filter = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == "--limit" and i + 1 < len(sys.argv):
                    limit = int(sys.argv[i + 1])
                    i += 2
                else:
                    i += 1
            
            results = store.search(query, type_filter, limit)
            print(f"🔍 検索結果: {len(results)}件 (クエリ: '{query}')")
            if type_filter:
                print(f"   タイプフィルタ: {type_filter}")
            print()
            
            for r in results:
                print(f"  [{r['id']}] {r['title']}")
                print(f"      タイプ: {r['type']} | 作成: {r['created_at']}")
                print(f"      内容: {r['content'][:100]}{'...' if len(r['content']) > 100 else ''}")
                print()
                
        elif action == "link":
            if len(sys.argv) < 5:
                print("エラー: 引数が不足しています")
                print("使用法: link <from_id> <to_id> <link_type>")
                return
                
            from_id = int(sys.argv[2])
            to_id = int(sys.argv[3])
            link_type = sys.argv[4]
            
            # 有効なリンクタイプをチェック
            valid_links = ["solves", "causes", "related", "implements", "references"]
            if link_type not in valid_links:
                print(f"エラー: 無効なリンクタイプ '{link_type}'")
                print(f"有効なリンクタイプ: {', '.join(valid_links)}")
                return
            
            store.link(from_id, to_id, link_type)
            print(f"✓ リンクを作成しました: {from_id} -> {to_id} ({link_type})")
            
        elif action == "related":
            if len(sys.argv) < 3:
                print("エラー: IDが必要です")
                print("使用法: related <id>")
                return
                
            id = int(sys.argv[2])
            
            related = store.get_linked(id)
            print(f"🔗 関連知識: {len(related)}件 (ID: {id})")
            print()
            
            for r in related:
                print(f"  [{r['id']}] {r['title']} ({r['link']})")
                
        elif action == "list":
            type_filter = None
            limit = 20
            
            # オプション解析
            i = 2
            while i < len(sys.argv):
                if sys.argv[i] == "--type" and i + 1 < len(sys.argv):
                    type_filter = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == "--limit" and i + 1 < len(sys.argv):
                    limit = int(sys.argv[i + 1])
                    i += 2
                else:
                    i += 1
            
            # 全件検索（空文字で全てマッチ）
            results = store.search("*", type_filter, limit)
            print(f"📋 知識一覧: {len(results)}件")
            if type_filter:
                print(f"   タイプフィルタ: {type_filter}")
            print()
            
            for r in results:
                print(f"  [{r['id']}] {r['title']} ({r['type']})")
                
        else:
            print(f"エラー: 不明なアクション '{action}'")
            print_usage()
            
    except ValueError as e:
        print(f"エラー: 数値の変換に失敗しました - {e}")
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
    finally:
        store.close()

if __name__ == "__main__":
    main()