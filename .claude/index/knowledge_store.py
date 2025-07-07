"""
Memory Bank 2.0 - Phase 1: SQLite知識管理システム

シンプルで実用的な知識管理システム
- SQLite + FTS5による全文検索
- 簡易リンクシステム
- Markdownファイルとの統合
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

class KnowledgeStore:
    """シンプルで実用的な知識管理システム"""
    
    def __init__(self, project_path: str):
        self.db_path = Path(project_path) / ".claude/index/knowledge.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self._init_schema()
        
    def _init_schema(self):
        """必要最小限のスキーマ"""
        
        # FTS5による全文検索
        self.conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_fts USING fts5(
            title, content, tags, source_file
        )
        """)
        
        # メタデータ
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_meta (
            id INTEGER PRIMARY KEY,
            type TEXT,  -- 'error', 'solution', 'decision', 'memo'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            context TEXT
        )
        """)
        
        # 簡易リンク
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_links (
            from_id INTEGER,
            to_id INTEGER,
            link_type TEXT  -- 'solves', 'causes', 'related'
        )
        """)
        
        self.conn.commit()
    
    def add(self, title: str, content: str, type: str, 
            tags: List[str] = None, source_file: str = None) -> int:
        """知識を追加"""
        cursor = self.conn.execute(
            "INSERT INTO knowledge_fts (title, content, tags, source_file) VALUES (?, ?, ?, ?)",
            (title, content, json.dumps(tags or []), source_file or "")
        )
        
        fts_id = cursor.lastrowid
        
        self.conn.execute(
            "INSERT INTO knowledge_meta (id, type) VALUES (?, ?)",
            (fts_id, type)
        )
        
        self.conn.commit()
        return fts_id
    
    def search(self, query: str, type: str = None, limit: int = 10) -> List[Dict]:
        """全文検索"""
        
        # 全件検索の場合は別のSQLを使用
        if query == "*" or query == "":
            sql = """
            SELECT f.rowid, f.title, f.content, m.type, m.created_at
            FROM knowledge_fts f
            JOIN knowledge_meta m ON f.rowid = m.id
            """
            params = []
            
            if type:
                sql += " WHERE m.type = ?"
                params.append(type)
                
            sql += " ORDER BY m.created_at DESC LIMIT ?"
            params.append(limit)
            
        else:
            # 通常のFTS検索
            sql = """
            SELECT f.rowid, f.title, f.content, m.type, m.created_at
            FROM knowledge_fts f
            JOIN knowledge_meta m ON f.rowid = m.id
            WHERE knowledge_fts MATCH ?
            """
            
            params = [query]
            if type:
                sql += " AND m.type = ?"
                params.append(type)
                
            sql += " ORDER BY rank LIMIT ?"
            params.append(limit)
        
        cursor = self.conn.execute(sql, params)
        
        return [{
            "id": row[0],
            "title": row[1],
            "content": row[2],
            "type": row[3],
            "created_at": row[4]
        } for row in cursor]
    
    def link(self, from_id: int, to_id: int, link_type: str):
        """知識間のリンク作成"""
        self.conn.execute(
            "INSERT INTO knowledge_links VALUES (?, ?, ?)",
            (from_id, to_id, link_type)
        )
        self.conn.commit()
    
    def get_linked(self, id: int) -> List[Dict]:
        """リンクされた知識を取得"""
        cursor = self.conn.execute("""
        SELECT f.rowid, f.title, l.link_type
        FROM knowledge_links l
        JOIN knowledge_fts f ON l.to_id = f.rowid
        WHERE l.from_id = ?
        """, (id,))
        
        return [{"id": row[0], "title": row[1], "link": row[2]} for row in cursor]

    def close(self):
        """データベース接続を閉じる"""
        if self.conn:
            self.conn.close()

def test_knowledge_store():
    """基本的なテスト"""
    print("🔧 KnowledgeStore テスト開始...")
    
    # テスト用インスタンス作成
    store = KnowledgeStore(".")
    
    # 1. エラーを追加
    error_id = store.add(
        title="JWT_DECODE_ERROR",
        content="JWTトークンのデコードに失敗。Invalid signature エラー",
        type="error",
        tags=["jwt", "auth", "error"],
        source_file="src/auth.py"
    )
    print(f"✓ エラー追加完了 (ID: {error_id})")
    
    # 2. 解決策を追加
    solution_id = store.add(
        title="JWT_DECODE_ERROR_FIX", 
        content="環境変数APP_SECRET_KEYが未設定。設定ファイルを確認してください",
        type="solution",
        tags=["jwt", "auth", "fix"]
    )
    print(f"✓ 解決策追加完了 (ID: {solution_id})")
    
    # 3. リンクを作成
    store.link(error_id, solution_id, "solves")
    print("✓ エラー-解決策リンク作成完了")
    
    # 4. 検索テスト
    results = store.search("JWT")
    print(f"✓ 検索結果: {len(results)}件")
    for result in results:
        print(f"  - {result['title']} ({result['type']})")
    
    # 5. 関連知識取得
    related = store.get_linked(error_id)
    print(f"✓ 関連知識: {len(related)}件")
    for rel in related:
        print(f"  - {rel['title']} ({rel['link']})")
    
    store.close()
    print("🎉 テスト完了！")

if __name__ == "__main__":
    test_knowledge_store()