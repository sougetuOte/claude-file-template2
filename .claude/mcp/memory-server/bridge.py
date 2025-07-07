#!/usr/bin/env python3
"""
Memory Bank 2.0 MCP Python Bridge
MCPサーバーとSQLite KnowledgeStoreの橋渡し

Usage: python bridge.py <method> <args_json>
"""

import sys
import json
import os
from pathlib import Path

# knowledge_storeをインポート
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.append(str(PROJECT_ROOT / ".claude" / "index"))
from knowledge_store import KnowledgeStore

def validate_input(args: dict) -> bool:
    """入力検証 - CVE-2025-49596対策"""
    # JSONサイズ制限（10KB）
    json_str = json.dumps(args)
    if len(json_str) > 10240:
        return False
    
    # 必要なフィールドの型チェック
    if 'query' in args and not isinstance(args['query'], str):
        return False
    if 'title' in args and not isinstance(args['title'], str):
        return False
    if 'content' in args and not isinstance(args['content'], str):
        return False
    if 'type' in args and not isinstance(args['type'], str):
        return False
    
    return True

def search_knowledge(args: dict) -> dict:
    """知識検索"""
    query = args.get('query', '')
    type_filter = args.get('type')
    limit = args.get('limit', 10)
    
    if not query:
        return {"error": "Query is required"}
    
    store = KnowledgeStore(str(PROJECT_ROOT))  # プロジェクトルートを指定
    try:
        results = store.search(query, type_filter, limit)
        return {
            "success": True,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        store.close()

def add_knowledge(args: dict) -> dict:
    """知識追加"""
    title = args.get('title')
    content = args.get('content')
    type_name = args.get('type')
    tags = args.get('tags', [])
    source_file = args.get('source_file')
    
    if not all([title, content, type_name]):
        return {"error": "title, content, and type are required"}
    
    # 有効なタイプをチェック
    valid_types = ["error", "solution", "decision", "memo", "code", "concept"]
    if type_name not in valid_types:
        return {"error": f"Invalid type. Must be one of: {', '.join(valid_types)}"}
    
    store = KnowledgeStore(str(PROJECT_ROOT))
    try:
        knowledge_id = store.add(title, content, type_name, tags, source_file)
        return {
            "success": True,
            "id": knowledge_id,
            "message": f"Knowledge added with ID: {knowledge_id}"
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        store.close()

def link_knowledge(args: dict) -> dict:
    """知識リンク作成"""
    from_id = args.get('from_id')
    to_id = args.get('to_id')
    link_type = args.get('link_type')
    
    if not all([from_id, to_id, link_type]):
        return {"error": "from_id, to_id, and link_type are required"}
    
    # 有効なリンクタイプをチェック
    valid_links = ["solves", "causes", "related", "implements", "references"]
    if link_type not in valid_links:
        return {"error": f"Invalid link_type. Must be one of: {', '.join(valid_links)}"}
    
    store = KnowledgeStore(str(PROJECT_ROOT))
    try:
        store.link(from_id, to_id, link_type)
        return {
            "success": True,
            "message": f"Link created: {from_id} -> {to_id} ({link_type})"
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        store.close()

def get_related(args: dict) -> dict:
    """関連知識取得"""
    knowledge_id = args.get('id')
    
    if not knowledge_id:
        return {"error": "id is required"}
    
    store = KnowledgeStore(str(PROJECT_ROOT))
    try:
        related = store.get_linked(knowledge_id)
        return {
            "success": True,
            "related": related,
            "count": len(related)
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        store.close()

def main():
    """メイン処理"""
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: python bridge.py <method> <args_json>"}))
        sys.exit(1)
    
    method = sys.argv[1]
    
    try:
        args = json.loads(sys.argv[2])
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {e}"}))
        sys.exit(1)
    
    # 入力検証
    if not validate_input(args):
        print(json.dumps({"error": "Input validation failed"}))
        sys.exit(1)
    
    # メソッド実行
    try:
        if method == "search":
            result = search_knowledge(args)
        elif method == "add":
            result = add_knowledge(args)
        elif method == "link":
            result = link_knowledge(args)
        elif method == "related":
            result = get_related(args)
        else:
            result = {"error": f"Unknown method: {method}"}
        
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(json.dumps({"error": f"Execution error: {e}"}))
        sys.exit(1)

if __name__ == "__main__":
    main()