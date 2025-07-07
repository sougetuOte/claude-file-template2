#!/usr/bin/env python3
"""
Memory Bank 2.0 Phase 3: AI生成コード品質モニター
AST解析による重複コード検出と品質改善提案
"""

import ast
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# knowledge_storeをインポート
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT / ".claude" / "index"))
from knowledge_store import KnowledgeStore


class SimpleCodeMonitor:
    """AI生成コードの重複検出と品質監視（軽量版）"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.store = KnowledgeStore(project_path)
        
    def check_code_duplication(self, file_path: str, new_code: str) -> Dict:
        """コードの重複をチェック"""
        
        try:
            # Python以外のファイルは簡易チェック
            if not file_path.endswith('.py'):
                return self._check_text_similarity(file_path, new_code)
            
            # PythonファイルのAST解析
            tree = ast.parse(new_code)
            structure = self._extract_structure(tree)
            complexity = self._calculate_complexity(tree)
            
        except SyntaxError:
            return {
                "status": "syntax_error",
                "message": "構文エラーがあります。コードを確認してください。"
            }
        except Exception as e:
            return {
                "status": "error", 
                "message": f"解析エラー: {str(e)}"
            }
            
        # 構造のハッシュを計算
        structure_hash = hashlib.md5(str(structure).encode()).hexdigest()[:8]
        
        # 類似コードを検索（タグベース）
        similar = self.store.search(structure_hash, type="code", limit=5)
        
        result = {
            "file_path": file_path,
            "structure_hash": structure_hash,
            "complexity": complexity,
            "duplicate_found": False,
            "suggestions": []
        }
        
        if similar:
            result.update({
                "duplicate_found": True,
                "similar_files": [s.get("source_file", "unknown") for s in similar],
                "suggestions": [
                    "既存のコードを再利用することを検討してください",
                    f"類似パターン: {len(similar)}件"
                ]
            })
        else:
            # 新しいパターンとして記録
            self._record_code_pattern(file_path, new_code, structure_hash, complexity)
            result["suggestions"].append("新しいコードパターンとして記録されました")
        
        # 複雑度チェック
        if complexity > 10:
            result["suggestions"].append(f"複雑度が高めです({complexity}): リファクタリングを検討")
        
        return result
    
    def _extract_structure(self, tree: ast.AST) -> List[str]:
        """ASTから構造情報を抽出（改良版）"""
        structure = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 関数名と引数の数
                args_count = len(node.args.args)
                structure.append(f"func:{node.name}:{args_count}")
                
            elif isinstance(node, ast.ClassDef):
                # クラス名とメソッド数
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                structure.append(f"class:{node.name}:{len(methods)}")
                
            elif isinstance(node, ast.ImportFrom):
                # インポート文
                structure.append(f"import:{node.module}")
        
        return sorted(structure)
    
    def _calculate_complexity(self, tree: ast.AST) -> int:
        """簡易的な循環的複雑度を計算"""
        complexity = 1  # ベース複雑度
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Try)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity
    
    def _check_text_similarity(self, file_path: str, content: str) -> Dict:
        """非Pythonファイルの文字列類似度チェック"""
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        
        # 類似内容を検索（タグベース）
        similar = self.store.search(content_hash, limit=3)
        
        result = {
            "file_path": file_path,
            "content_hash": content_hash,
            "duplicate_found": bool(similar),
            "suggestions": []
        }
        
        if similar:
            result["suggestions"].append("類似ファイルが見つかりました")
        else:
            # 記録
            self.store.add(
                title=f"File: {Path(file_path).name}",
                content=f"Content hash: {content_hash}\n{content[:300]}...",
                type="code",
                tags=["file_content", content_hash],
                source_file=file_path
            )
        
        return result
    
    def _record_code_pattern(self, file_path: str, code: str, structure_hash: str, complexity: int):
        """新しいコードパターンを知識DBに記録"""
        
        # コード要約を作成
        lines = code.split('\n')
        summary = '\n'.join(lines[:10])  # 最初の10行
        if len(lines) > 10:
            summary += f"\n... ({len(lines)} lines total)"
        
        self.store.add(
            title=f"Code Pattern: {Path(file_path).name}",
            content=f"Structure hash: {structure_hash}\nComplexity: {complexity}\n\n{summary}",
            type="code",
            tags=["ai_generated", "code_pattern", structure_hash, f"complexity_{complexity}"],
            source_file=file_path
        )
    
    def analyze_project_patterns(self) -> Dict:
        """プロジェクト全体のコードパターンを分析"""
        
        all_code = self.store.search("*", type="code", limit=100)
        
        patterns = {}
        complexity_stats = []
        
        for code_item in all_code:
            content = code_item.get("content", "")
            
            # 複雑度統計
            for line in content.split('\n'):
                if line.startswith('Complexity:'):
                    try:
                        complexity = int(line.split(':')[1].strip())
                        complexity_stats.append(complexity)
                    except (ValueError, IndexError):
                        continue
            
            # パターン集計
            tags = code_item.get("tags", [])
            for tag in tags:
                if tag.startswith("complexity_"):
                    level = tag.replace("complexity_", "")
                    patterns[f"complexity_{level}"] = patterns.get(f"complexity_{level}", 0) + 1
        
        avg_complexity = sum(complexity_stats) / len(complexity_stats) if complexity_stats else 0
        
        return {
            "total_code_items": len(all_code),
            "average_complexity": round(avg_complexity, 2),
            "patterns": patterns,
            "suggestions": self._generate_project_suggestions(patterns, avg_complexity)
        }
    
    def _generate_project_suggestions(self, patterns: Dict, avg_complexity: float) -> List[str]:
        """プロジェクト全体の改善提案を生成"""
        suggestions = []
        
        # 複雑度が高い場合
        if avg_complexity > 8:
            suggestions.append(f"平均複雑度が高めです({avg_complexity}): 関数の分割を検討")
        
        # 高複雑度コードが多い場合
        high_complexity_count = patterns.get("complexity_10", 0) + patterns.get("complexity_15", 0)
        if high_complexity_count > 3:
            suggestions.append(f"複雑なコードが{high_complexity_count}件: リファクタリング推奨")
        
        # パターンの多様性
        if len(patterns) < 3:
            suggestions.append("コードパターンが少なめ: より多様な実装手法を試してみてください")
        
        return suggestions
    
    def close(self):
        """リソースのクリーンアップ"""
        self.store.close()


def main():
    """CLI インターフェース"""
    if len(sys.argv) < 2:
        print("Usage: python code_monitor.py <command> [args...]")
        print("Commands:")
        print("  check <file_path>     - ファイルの重複チェック")
        print("  analyze              - プロジェクト全体の分析")
        print("  test                 - テスト実行")
        sys.exit(1)
    
    command = sys.argv[1]
    monitor = SimpleCodeMonitor(str(PROJECT_ROOT))
    
    try:
        if command == "check" and len(sys.argv) > 2:
            file_path = sys.argv[2]
            
            if not Path(file_path).exists():
                print(f"Error: File not found: {file_path}")
                sys.exit(1)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            result = monitor.check_code_duplication(file_path, content)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        elif command == "analyze":
            result = monitor.analyze_project_patterns()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        elif command == "test":
            # テスト用のサンプルコード
            test_code = '''
def hello_world():
    """テスト用関数"""
    print("Hello, World!")
    return "success"

class TestClass:
    def __init__(self):
        self.value = 42
    
    def get_value(self):
        return self.value
'''
            result = monitor.check_code_duplication("test.py", test_code)
            print("✅ Code Monitor Test:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        monitor.close()


if __name__ == "__main__":
    main()