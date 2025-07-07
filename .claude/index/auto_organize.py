#!/usr/bin/env python3
"""
Memory Bank 2.0 Phase 3: 知識自動整理システム
蓄積された知識を定期的に整理し、古い情報の自動アーカイブと新しいパターンの抽出
"""

import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# knowledge_storeをインポート
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT / ".claude" / "index"))
from knowledge_store import KnowledgeStore


class KnowledgeOrganizer:
    """知識の自動整理とパターン抽出"""
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.store = KnowledgeStore(project_path)
        self.archive_after_days = 30  # 30日経過でアーカイブ対象
        
    def organize_knowledge(self) -> Dict:
        """全体的な知識整理を実行"""
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "actions": [],
            "statistics": {},
            "patterns": {}
        }
        
        try:
            # 1. 古いエラーの整理
            resolved_errors = self._archive_resolved_errors()
            results["actions"].append({
                "action": "archive_resolved_errors",
                "count": len(resolved_errors),
                "items": resolved_errors
            })
            
            # 2. 重複知識の統合
            duplicates = self._merge_duplicate_knowledge()
            results["actions"].append({
                "action": "merge_duplicates", 
                "count": len(duplicates),
                "items": duplicates
            })
            
            # 3. パターン抽出と記録
            patterns = self._extract_common_patterns()
            results["patterns"] = patterns
            results["actions"].append({
                "action": "extract_patterns",
                "count": len(patterns),
                "items": list(patterns.keys())
            })
            
            # 4. 統計情報の更新
            stats = self._calculate_statistics()
            results["statistics"] = stats
            
            # 5. 整理結果の記録
            self._record_organization_results(results)
            
        except Exception as e:
            results["error"] = str(e)
        
        return results
    
    def _archive_resolved_errors(self) -> List[Dict]:
        """解決済みエラーをアーカイブ"""
        
        archived = []
        errors = self.store.search("*", type="error", limit=100)
        
        for error in errors:
            error_id = error.get("id")
            if not error_id:
                continue
            
            # リンクされた解決策を確認
            linked = self.store.get_linked(error_id)
            solutions = [link for link in linked if link.get("link") == "solves"]
            
            if solutions:
                # 解決済みとしてマーク
                try:
                    resolved_title = f"[RESOLVED] {error['title']}"
                    resolved_content = f"Original Error (ID:{error_id}):\n{error['content']}\n\nSolved by: {len(solutions)} solution(s)"
                    
                    # アーカイブとして新規追加
                    archived_id = self.store.add(
                        title=resolved_title,
                        content=resolved_content,
                        type="archived_error",
                        tags=error.get("tags", []) + ["resolved", "auto_archived"],
                        source_file=error.get("source_file")
                    )
                    
                    archived.append({
                        "original_id": error_id,
                        "archived_id": archived_id,
                        "title": error["title"],
                        "solutions_count": len(solutions)
                    })
                    
                except Exception as e:
                    print(f"Error archiving {error_id}: {e}")
        
        return archived
    
    def _merge_duplicate_knowledge(self) -> List[Dict]:
        """重複する知識を統合"""
        
        merged = []
        all_knowledge = self.store.search("*", limit=200)
        
        # タイトルの類似度で重複を検出
        title_groups = defaultdict(list)
        
        for item in all_knowledge:
            title = item.get("title", "").lower()
            # 簡易的な正規化
            normalized = re.sub(r'[^\w\s]', '', title)
            normalized = re.sub(r'\s+', ' ', normalized).strip()
            
            if len(normalized) > 10:  # 短すぎるタイトルは除外
                title_groups[normalized].append(item)
        
        # 重複グループを処理
        for normalized_title, items in title_groups.items():
            if len(items) > 1:
                # 最新のものを保持、古いものの情報を統合
                items.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
                primary = items[0]
                duplicates = items[1:]
                
                try:
                    # 重複情報を統合したコンテンツを作成
                    merged_content = primary.get("content", "")
                    merged_tags = set(primary.get("tags", []))
                    
                    for dup in duplicates:
                        dup_content = dup.get("content", "")
                        if dup_content and dup_content not in merged_content:
                            merged_content += f"\n\n--- Merged from ID:{dup.get('id')} ---\n{dup_content}"
                        merged_tags.update(dup.get("tags", []))
                    
                    merged_tags.add("auto_merged")
                    
                    # 新しい統合エントリを作成
                    merged_id = self.store.add(
                        title=f"[MERGED] {primary['title']}",
                        content=merged_content,
                        type=primary.get("type", "memo"),
                        tags=list(merged_tags),
                        source_file=primary.get("source_file")
                    )
                    
                    merged.append({
                        "primary_id": primary.get("id"),
                        "merged_id": merged_id,
                        "duplicate_count": len(duplicates),
                        "title": primary["title"]
                    })
                    
                except Exception as e:
                    print(f"Error merging duplicates for '{normalized_title}': {e}")
        
        return merged
    
    def _extract_common_patterns(self) -> Dict:
        """よく使われるパターンを抽出"""
        
        patterns = {}
        all_knowledge = self.store.search("*", limit=300)
        
        # 1. タグの頻度分析
        tag_counter = Counter()
        for item in all_knowledge:
            tags = item.get("tags", [])
            tag_counter.update(tags)
        
        common_tags = tag_counter.most_common(10)
        patterns["common_tags"] = [{"tag": tag, "count": count} for tag, count in common_tags]
        
        # 2. タイプ分布
        type_counter = Counter()
        for item in all_knowledge:
            item_type = item.get("type", "unknown")
            type_counter[item_type] += 1
        
        patterns["type_distribution"] = dict(type_counter)
        
        # 3. よく使われるキーワード
        content_words = Counter()
        for item in all_knowledge:
            content = item.get("content", "").lower()
            # 簡易的なキーワード抽出
            words = re.findall(r'\b[a-zA-Z]{4,}\b', content)
            content_words.update(words)
        
        common_words = content_words.most_common(15)
        patterns["common_keywords"] = [{"word": word, "count": count} for word, count in common_words]
        
        # 4. 解決パターンの分析
        solution_patterns = self._analyze_solution_patterns()
        patterns["solution_patterns"] = solution_patterns
        
        # 新しいパターンを知識として記録
        for pattern_type, pattern_data in patterns.items():
            if pattern_type != "solution_patterns":  # solution_patternsは別途記録
                self._record_pattern(pattern_type, pattern_data)
        
        return patterns
    
    def _analyze_solution_patterns(self) -> Dict:
        """問題解決パターンの分析"""
        
        patterns = {
            "total_problems": 0,
            "solved_problems": 0,
            "common_solution_types": {},
            "resolution_time_avg": "unknown"
        }
        
        # エラーと解決策のリンクを分析
        errors = self.store.search("*", type="error", limit=50)
        solutions = self.store.search("*", type="solution", limit=50)
        
        patterns["total_problems"] = len(errors)
        
        solved_count = 0
        solution_types = Counter()
        
        for error in errors:
            error_id = error.get("id")
            if not error_id:
                continue
            
            linked = self.store.get_linked(error_id)
            error_solutions = [link for link in linked if link.get("link") == "solves"]
            
            if error_solutions:
                solved_count += 1
                
                # 解決策のタイプを分析
                for sol_link in error_solutions:
                    linked_item = sol_link.get("linked_item", {})
                    sol_content = linked_item.get("content", "").lower()
                    
                    if "config" in sol_content:
                        solution_types["configuration"] += 1
                    elif "install" in sol_content or "dependency" in sol_content:
                        solution_types["dependency"] += 1
                    elif "code" in sol_content or "function" in sol_content:
                        solution_types["code_fix"] += 1
                    else:
                        solution_types["other"] += 1
        
        patterns["solved_problems"] = solved_count
        patterns["solution_rate"] = round(solved_count / max(len(errors), 1), 2)
        patterns["common_solution_types"] = dict(solution_types)
        
        return patterns
    
    def _record_pattern(self, pattern_type: str, pattern_data):
        """抽出したパターンを知識として記録"""
        
        try:
            content = f"Auto-extracted pattern on {datetime.now().date()}\n\n"
            content += json.dumps(pattern_data, indent=2, ensure_ascii=False)
            
            self.store.add(
                title=f"Pattern: {pattern_type}",
                content=content,
                type="pattern",
                tags=["auto_extracted", "pattern", pattern_type],
                source_file="auto_organize.py"
            )
        except Exception as e:
            print(f"Error recording pattern {pattern_type}: {e}")
    
    def _calculate_statistics(self) -> Dict:
        """知識ベース全体の統計を計算"""
        
        all_knowledge = self.store.search("*", limit=500)
        
        stats = {
            "total_items": len(all_knowledge),
            "by_type": {},
            "recent_activity": {},
            "health_score": 0
        }
        
        # タイプ別統計
        type_counts = Counter()
        for item in all_knowledge:
            item_type = item.get("type", "unknown")
            type_counts[item_type] += 1
        
        stats["by_type"] = dict(type_counts)
        
        # 最近の活動
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        
        recent_count = 0
        for item in all_knowledge:
            timestamp_str = item.get("timestamp", "")
            if timestamp_str:
                try:
                    item_date = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00")).date()
                    if item_date >= week_ago:
                        recent_count += 1
                except:
                    pass
        
        stats["recent_activity"] = {
            "last_7_days": recent_count,
            "daily_average": round(recent_count / 7, 1)
        }
        
        # ヘルススコア計算（0-100）
        health_score = 50  # ベーススコア
        
        if stats["total_items"] > 10:
            health_score += 20
        if len(stats["by_type"]) > 3:
            health_score += 15
        if recent_count > 0:
            health_score += 15
        
        stats["health_score"] = min(health_score, 100)
        
        return stats
    
    def _record_organization_results(self, results: Dict):
        """整理結果を知識として記録"""
        
        try:
            summary = f"Knowledge base organization completed\n"
            summary += f"Timestamp: {results['timestamp']}\n"
            summary += f"Actions performed: {len(results.get('actions', []))}\n"
            summary += f"Health score: {results.get('statistics', {}).get('health_score', 'unknown')}"
            
            self.store.add(
                title=f"Knowledge Organization Report {datetime.now().strftime('%Y-%m-%d')}",
                content=summary + "\n\n" + json.dumps(results, indent=2, ensure_ascii=False),
                type="report",
                tags=["auto_organization", "system", "report"],
                source_file="auto_organize.py"
            )
        except Exception as e:
            print(f"Error recording organization results: {e}")
    
    def cleanup_old_patterns(self, days: int = 60) -> int:
        """古いパターン記録をクリーンアップ"""
        
        cleaned = 0
        patterns = self.store.search("*", type="pattern", limit=100)
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for pattern in patterns:
            timestamp_str = pattern.get("timestamp", "")
            if timestamp_str:
                try:
                    pattern_date = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                    if pattern_date < cutoff_date:
                        # 古いパターンは削除フラグを立てる（実際の削除は手動で）
                        tags = pattern.get("tags", [])
                        if "cleanup_candidate" not in tags:
                            tags.append("cleanup_candidate")
                            cleaned += 1
                except:
                    pass
        
        return cleaned
    
    def close(self):
        """リソースのクリーンアップ"""
        self.store.close()


def main():
    """CLI インターフェース"""
    if len(sys.argv) < 2:
        print("Usage: python auto_organize.py <command> [args...]")
        print("Commands:")
        print("  organize              - 全体的な知識整理を実行")
        print("  patterns              - パターン抽出のみ実行")
        print("  stats                 - 統計情報の表示")
        print("  cleanup [days]        - 古いパターンのクリーンアップ")
        print("  test                  - テスト実行")
        sys.exit(1)
    
    command = sys.argv[1]
    organizer = KnowledgeOrganizer(str(PROJECT_ROOT))
    
    try:
        if command == "organize":
            result = organizer.organize_knowledge()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        elif command == "patterns":
            patterns = organizer._extract_common_patterns()
            print(json.dumps(patterns, indent=2, ensure_ascii=False))
            
        elif command == "stats":
            stats = organizer._calculate_statistics()
            print(json.dumps(stats, indent=2, ensure_ascii=False))
            
        elif command == "cleanup":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 60
            cleaned = organizer.cleanup_old_patterns(days)
            result = {"cleaned_patterns": cleaned, "days_threshold": days}
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        elif command == "test":
            print("✅ Knowledge Organizer Test:")
            
            # 統計テスト
            stats = organizer._calculate_statistics()
            print(f"Total knowledge items: {stats['total_items']}")
            print(f"Health score: {stats['health_score']}")
            
            # パターン抽出テスト
            patterns = organizer._extract_common_patterns()
            print(f"Common tags found: {len(patterns.get('common_tags', []))}")
            print(f"Type distribution: {patterns.get('type_distribution', {})}")
            
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        organizer.close()


if __name__ == "__main__":
    main()