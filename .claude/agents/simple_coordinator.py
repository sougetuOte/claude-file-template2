#!/usr/bin/env python3
"""
Memory Bank 2.0 Phase 3: 簡易タスクコーディネーター
複雑なマルチエージェントではなく、役割分担の明確化による効率向上
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class TaskCoordinator:
    """タスクを適切なモードに振り分ける簡易コーディネーター"""
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        
        # モード定義（Claude Codeの既存コマンドに基づく）
        self.modes = {
            "debug": {
                "trigger_words": [
                    "error", "bug", "issue", "problem", "fix", "broken", 
                    "crash", "エラー", "バグ", "問題", "修正", "壊れ"
                ],
                "command": "/debug:start",
                "context_files": [
                    ".claude/debug/latest.md",
                    ".claude/context/history.md"
                ],
                "description": "エラー解決・デバッグに特化したモード",
                "priority": "high"
            },
            "feature": {
                "trigger_words": [
                    "implement", "add", "create", "new feature", "build",
                    "develop", "作成", "実装", "追加", "新機能", "開発"
                ],
                "command": "/feature:plan",
                "context_files": [
                    ".claude/core/overview.md",
                    ".claude/context/tech.md",
                    "docs/requirements.md"
                ],
                "description": "新機能開発・実装のモード",
                "priority": "medium"
            },
            "review": {
                "trigger_words": [
                    "review", "check", "quality", "refactor", "improve",
                    "test", "レビュー", "確認", "品質", "改善", "テスト"
                ],
                "command": "/review:check",
                "context_files": [
                    ".claude/guidelines/development.md",
                    ".claude/guidelines/testing-quality.md"
                ],
                "description": "コードレビュー・品質改善のモード",
                "priority": "medium"
            },
            "planning": {
                "trigger_words": [
                    "plan", "design", "architecture", "strategy", "organize",
                    "計画", "設計", "戦略", "整理"
                ],
                "command": "/project:plan",
                "context_files": [
                    ".claude/core/next.md",
                    ".claude/core/current.md"
                ],
                "description": "プロジェクト計画・設計のモード",
                "priority": "low"
            },
            "knowledge": {
                "trigger_words": [
                    "search", "find", "knowledge", "learn", "document",
                    "検索", "探す", "知識", "学習", "文書"
                ],
                "command": "/k",
                "context_files": [
                    ".claude/commands/knowledge.md"
                ],
                "description": "知識管理・検索のモード",
                "priority": "low"
            }
        }
    
    def suggest_mode(self, task_description: str) -> Dict:
        """タスクに最適なモードを提案"""
        
        task_lower = task_description.lower()
        mode_scores = {}
        
        # 各モードとのマッチングスコアを計算
        for mode_name, config in self.modes.items():
            score = 0
            matched_words = []
            
            for trigger in config["trigger_words"]:
                if trigger.lower() in task_lower:
                    score += 1
                    matched_words.append(trigger)
            
            if score > 0:
                mode_scores[mode_name] = {
                    "score": score,
                    "matched_words": matched_words,
                    "config": config
                }
        
        # 最高スコアのモードを選択
        if mode_scores:
            best_mode = max(mode_scores.keys(), key=lambda k: mode_scores[k]["score"])
            best_config = mode_scores[best_mode]
            
            return {
                "recommended_mode": best_mode,
                "command": best_config["config"]["command"],
                "description": best_config["config"]["description"],
                "matched_words": best_config["matched_words"],
                "suggested_context": best_config["config"]["context_files"],
                "priority": best_config["config"]["priority"],
                "confidence": min(best_config["score"] / 3.0, 1.0),  # 正規化
                "message": f"'{best_mode}'モードの使用をお勧めします"
            }
        
        # マッチしない場合は汎用モード
        return {
            "recommended_mode": "general",
            "command": "/project:plan",
            "description": "汎用的な作業モード",
            "matched_words": [],
            "suggested_context": [".claude/core/current.md"],
            "priority": "low",
            "confidence": 0.1,
            "message": "汎用モードで作業を開始します"
        }
    
    def analyze_context_files(self, mode: str) -> Dict:
        """指定されたモードの推奨コンテキストファイルを分析"""
        
        if mode not in self.modes:
            return {"error": f"Unknown mode: {mode}"}
        
        config = self.modes[mode]
        context_info = {
            "mode": mode,
            "files": [],
            "missing_files": [],
            "suggestions": []
        }
        
        for file_path in config["context_files"]:
            full_path = self.project_path / file_path
            
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    context_info["files"].append({
                        "path": file_path,
                        "size": len(content),
                        "lines": len(content.split('\n')),
                        "last_modified": datetime.fromtimestamp(
                            full_path.stat().st_mtime
                        ).isoformat()
                    })
                except Exception as e:
                    context_info["files"].append({
                        "path": file_path,
                        "error": str(e)
                    })
            else:
                context_info["missing_files"].append(file_path)
        
        # 提案生成
        if context_info["missing_files"]:
            context_info["suggestions"].append(
                f"以下のファイルが見つかりません: {', '.join(context_info['missing_files'])}"
            )
        
        if len(context_info["files"]) == 0:
            context_info["suggestions"].append(
                "コンテキストファイルが利用できません。基本的な情報から開始してください。"
            )
        
        return context_info
    
    def generate_workflow_suggestion(self, task: str, mode: str) -> Dict:
        """タスクとモードに基づいてワークフロー提案を生成"""
        
        if mode not in self.modes:
            mode = "general"
        
        config = self.modes.get(mode, {})
        workflow = {
            "task": task,
            "mode": mode,
            "steps": [],
            "estimated_time": "未定",
            "tools_needed": []
        }
        
        # モード別のワークフロー生成
        if mode == "debug":
            workflow["steps"] = [
                "1. 問題の再現と詳細な記録",
                "2. エラーログの分析",
                "3. 関連するコード箇所の特定",
                "4. 修正方法の検討と実装",
                "5. テストによる修正確認"
            ]
            workflow["tools_needed"] = ["Read", "Grep", "Edit", "Bash"]
            workflow["estimated_time"] = "30-60分"
            
        elif mode == "feature":
            workflow["steps"] = [
                "1. 機能要件の明確化",
                "2. 既存コードの調査",
                "3. 実装方法の設計",
                "4. コード実装",
                "5. テスト作成と実行"
            ]
            workflow["tools_needed"] = ["Read", "Write", "Edit", "Bash"]
            workflow["estimated_time"] = "1-3時間"
            
        elif mode == "review":
            workflow["steps"] = [
                "1. コード品質チェック",
                "2. テストカバレッジの確認",
                "3. セキュリティ要素の検証",
                "4. パフォーマンスの確認",
                "5. 改善提案の作成"
            ]
            workflow["tools_needed"] = ["Read", "Bash", "code_monitor.py"]
            workflow["estimated_time"] = "20-40分"
            
        elif mode == "planning":
            workflow["steps"] = [
                "1. 現在の状況の把握",
                "2. 目標の明確化",
                "3. タスクの分解",
                "4. 優先度の設定",
                "5. スケジュールの作成"
            ]
            workflow["tools_needed"] = ["Read", "Edit", "TodoWrite"]
            workflow["estimated_time"] = "15-30分"
            
        elif mode == "knowledge":
            workflow["steps"] = [
                "1. 検索キーワードの特定",
                "2. 知識ベースの検索",
                "3. 関連情報の収集",
                "4. 新しい知識の追加",
                "5. リンクの作成"
            ]
            workflow["tools_needed"] = ["k_command.py", "MCP tools"]
            workflow["estimated_time"] = "10-20分"
        
        return workflow
    
    def get_mode_statistics(self) -> Dict:
        """モード使用統計（簡易版）"""
        # 実際の使用統計は今後の拡張で実装
        return {
            "available_modes": list(self.modes.keys()),
            "total_modes": len(self.modes),
            "most_complex": "feature",
            "quickest": "knowledge",
            "description": "各モードの特徴と使用方法が定義されています"
        }


def main():
    """CLI インターフェース"""
    if len(sys.argv) < 2:
        print("Usage: python simple_coordinator.py <command> [args...]")
        print("Commands:")
        print("  suggest '<task_description>'  - タスクに最適なモードを提案")
        print("  analyze <mode>               - モードのコンテキスト分析")
        print("  workflow '<task>' <mode>     - ワークフロー提案生成")
        print("  stats                        - モード統計の表示")
        print("  test                         - テスト実行")
        sys.exit(1)
    
    command = sys.argv[1]
    coordinator = TaskCoordinator()
    
    try:
        if command == "suggest" and len(sys.argv) > 2:
            task = sys.argv[2]
            result = coordinator.suggest_mode(task)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        elif command == "analyze" and len(sys.argv) > 2:
            mode = sys.argv[2]
            result = coordinator.analyze_context_files(mode)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        elif command == "workflow" and len(sys.argv) > 3:
            task = sys.argv[2]
            mode = sys.argv[3]
            result = coordinator.generate_workflow_suggestion(task, mode)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        elif command == "stats":
            result = coordinator.get_mode_statistics()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        elif command == "test":
            # テスト実行
            test_tasks = [
                "Fix the authentication bug",
                "Implement user login feature", 
                "Review code quality",
                "Plan next sprint"
            ]
            
            print("✅ Task Coordinator Test:")
            for task in test_tasks:
                suggestion = coordinator.suggest_mode(task)
                print(f"\nTask: {task}")
                print(f"Suggested: {suggestion['recommended_mode']} "
                      f"(confidence: {suggestion['confidence']:.1f})")
                
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()