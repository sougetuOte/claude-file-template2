"""
Memory Bank 2.0 - Phase 1: SQLite知識管理システム

シンプルで実用的な知識管理システム
- SQLite + FTS5による全文検索
- 簡易リンクシステム
- Markdownファイルとの統合
"""

import sqlite3
import json
import hashlib
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
    
    def get_content_hash(self, content: str) -> str:
        """コンテンツのハッシュ値を計算"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def content_exists(self, content: str) -> bool:
        """同じコンテンツが既に存在するかチェック"""
        content_hash = self.get_content_hash(content)
        cursor = self.conn.execute(
            "SELECT 1 FROM knowledge_fts WHERE content LIKE ? LIMIT 1",
            (f"%{content_hash}%",)
        )
        return cursor.fetchone() is not None


class OptimizedKnowledgeStore:
    """最適化された知識管理システム（接続プーリング・バッチ処理対応）"""
    
    _instance = None
    _connection = None
    _db_path = None
    
    def __new__(cls, project_path: str):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, project_path: str):
        if self._initialized:
            return
        
        self._db_path = Path(project_path) / ".claude/index/knowledge.db"
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(str(self._db_path))
        self._init_schema()
        self._initialized = True
    
    def _init_schema(self):
        """必要最小限のスキーマ（従来と同じ）"""
        
        # FTS5による全文検索
        self._connection.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_fts USING fts5(
            title, content, tags, source_file
        )
        """)
        
        # メタデータ
        self._connection.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_meta (
            id INTEGER PRIMARY KEY,
            type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            context TEXT,
            content_hash TEXT
        )
        """)
        
        # 簡易リンク
        self._connection.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_links (
            from_id INTEGER,
            to_id INTEGER,
            link_type TEXT
        )
        """)
        
        # インデックス追加（パフォーマンス向上）
        # 先にテーブルとカラムが作成されていることを確認
        self._connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_knowledge_meta_type 
        ON knowledge_meta(type)
        """)
        
        # content_hashカラムが存在する場合のみインデックスを作成
        try:
            self._connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_knowledge_meta_hash 
            ON knowledge_meta(content_hash)
            """)
        except sqlite3.OperationalError:
            # content_hashカラムが存在しない場合は無視
            pass
        
        self._connection.commit()
    
    @classmethod
    def get_instance(cls, project_path: str = "."):
        """シングルトンインスタンスを取得"""
        return cls(project_path)
    
    def get_content_hash(self, content: str) -> str:
        """コンテンツのハッシュ値を計算"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def content_exists(self, content: str) -> Optional[int]:
        """同じコンテンツが既に存在するかチェック（IDを返す）"""
        content_hash = self.get_content_hash(content)
        cursor = self._connection.execute(
            "SELECT id FROM knowledge_meta WHERE content_hash = ? LIMIT 1",
            (content_hash,)
        )
        result = cursor.fetchone()
        return result[0] if result else None
    
    def add(self, title: str, content: str, type: str, 
            tags: List[str] = None, source_file: str = None,
            skip_duplicates: bool = True) -> int:
        """知識を追加（重複チェック機能付き）"""
        
        # 重複チェック
        if skip_duplicates:
            existing_id = self.content_exists(content)
            if existing_id:
                return existing_id
        
        # 新規追加
        cursor = self._connection.execute(
            "INSERT INTO knowledge_fts (title, content, tags, source_file) VALUES (?, ?, ?, ?)",
            (title, content, json.dumps(tags or []), source_file or "")
        )
        
        fts_id = cursor.lastrowid
        content_hash = self.get_content_hash(content)
        
        self._connection.execute(
            "INSERT INTO knowledge_meta (id, type, content_hash) VALUES (?, ?, ?)",
            (fts_id, type, content_hash)
        )
        
        self._connection.commit()
        return fts_id
    
    def add_batch(self, items: List[Dict], skip_duplicates: bool = True) -> List[int]:
        """バッチ処理で複数の知識を追加"""
        added_ids = []
        
        for item in items:
            try:
                id = self.add(
                    title=item["title"],
                    content=item["content"],
                    type=item["type"],
                    tags=item.get("tags", []),
                    source_file=item.get("source_file", ""),
                    skip_duplicates=skip_duplicates
                )
                added_ids.append(id)
            except Exception as e:
                print(f"Warning: バッチ処理中にエラー - {item.get('title', 'Unknown')}: {e}")
        
        return added_ids
    
    def search(self, query: str, type: str = None, limit: int = 10) -> List[Dict]:
        """全文検索（最適化済み）"""
        
        # 全件検索の場合
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
        
        cursor = self._connection.execute(sql, params)
        
        return [{
            "id": row[0],
            "title": row[1],
            "content": row[2],
            "type": row[3],
            "created_at": row[4]
        } for row in cursor]
    
    def link(self, from_id: int, to_id: int, link_type: str):
        """知識間のリンク作成"""
        self._connection.execute(
            "INSERT INTO knowledge_links VALUES (?, ?, ?)",
            (from_id, to_id, link_type)
        )
        self._connection.commit()
    
    def get_linked(self, id: int) -> List[Dict]:
        """リンクされた知識を取得"""
        cursor = self._connection.execute("""
        SELECT f.rowid, f.title, l.link_type
        FROM knowledge_links l
        JOIN knowledge_fts f ON l.to_id = f.rowid
        WHERE l.from_id = ?
        """, (id,))
        
        return [{"id": row[0], "title": row[1], "link": row[2]} for row in cursor]
    
    def get_stats(self) -> Dict:
        """データベースの統計情報を取得"""
        cursor = self._connection.execute("SELECT type, COUNT(*) FROM knowledge_meta GROUP BY type")
        type_counts = dict(cursor.fetchall())
        
        cursor = self._connection.execute("SELECT COUNT(*) FROM knowledge_fts")
        total_count = cursor.fetchone()[0]
        
        return {
            "total_items": total_count,
            "by_type": type_counts,
            "db_path": str(self._db_path)
        }
    
    def close(self):
        """データベース接続を閉じる"""
        if self._connection:
            self._connection.close()
            self._connection = None
            OptimizedKnowledgeStore._instance = None
    
    def __del__(self):
        """デストラクタ"""
        self.close()

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

def test_optimized_knowledge_store():
    """最適化版のテスト"""
    print("🚀 OptimizedKnowledgeStore テスト開始...")
    
    # テスト用インスタンス作成
    store = OptimizedKnowledgeStore.get_instance(".")
    
    # 1. バッチ処理テスト
    batch_items = [
        {
            "title": "Python Import Error",
            "content": "ModuleNotFoundError: No module named 'requests'",
            "type": "error",
            "tags": ["python", "import", "error"],
            "source_file": "src/main.py"
        },
        {
            "title": "Python Import Fix",
            "content": "pip install requests で解決",
            "type": "solution",
            "tags": ["python", "import", "fix"]
        }
    ]
    
    added_ids = store.add_batch(batch_items)
    print(f"✓ バッチ処理完了: {len(added_ids)}件追加")
    
    # 2. 重複チェックテスト
    duplicate_id = store.add(
        title="Python Import Error (重複)",
        content="ModuleNotFoundError: No module named 'requests'",  # 同じコンテンツ
        type="error",
        tags=["python", "duplicate"]
    )
    print(f"✓ 重複チェック: {'スキップされました' if duplicate_id == added_ids[0] else '新規追加されました'}")
    
    # 3. 統計情報取得
    stats = store.get_stats()
    print(f"✓ 統計情報: 総件数={stats['total_items']}, タイプ別={stats['by_type']}")
    
    # 4. 検索テスト
    results = store.search("Python")
    print(f"✓ 検索結果: {len(results)}件")
    for result in results[:3]:  # 最大3件表示
        print(f"  - {result['title']} ({result['type']})")
    
    # 接続は自動的に管理されるため、明示的にcloseしない
    print("🎉 最適化版テスト完了！")

if __name__ == "__main__":
    # 従来版のテスト
    test_knowledge_store()
    print("")
    # 最適化版のテスト
    test_optimized_knowledge_store()