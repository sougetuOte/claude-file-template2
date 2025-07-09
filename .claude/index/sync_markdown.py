#!/usr/bin/env python3
"""
Markdown Sync for Memory Bank 2.0
既存のMarkdownファイルと知識DBを同期

.claude/debug/latest.md → エラー情報を抽出
.claude/context/history.md → 決定事項を抽出  
.claude/core/current.md → 学習内容を抽出
"""

import sys
import os
import re
import time
import json
from pathlib import Path
from typing import List, Dict, Set

# knowledge_storeモジュールをインポート
sys.path.append(os.path.dirname(__file__))
from knowledge_store import KnowledgeStore, OptimizedKnowledgeStore

def extract_section(content: str, section_name: str) -> str:
    """マークダウンからセクションを抽出"""
    # "## セクション名" または "**セクション名**:" のパターンを探す
    patterns = [
        rf"##\s*{re.escape(section_name)}.*?\n(.*?)(?=\n##|\n$)",
        rf"\*\*{re.escape(section_name)}\*\*:\s*(.*?)(?=\n\*\*|\n$)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return ""

def sync_debug_file():
    """debug/latest.mdからエラー情報を抽出"""
    debug_file = Path(".claude/debug/latest.md")
    if not debug_file.exists():
        return []
        
    content = debug_file.read_text(encoding='utf-8')
    extracted = []
    
    # 問題セクションを抽出
    problem = extract_section(content, "問題")
    if problem:
        extracted.append({
            "title": "Debug: " + problem.split('\n')[0][:50],
            "content": problem,
            "type": "error",
            "source_file": str(debug_file)
        })
    
    # 原因セクションを抽出  
    cause = extract_section(content, "原因")
    if cause:
        extracted.append({
            "title": "Debug Cause: " + cause.split('\n')[0][:50],
            "content": cause,
            "type": "memo",
            "source_file": str(debug_file)
        })
    
    # 解決策セクションを抽出
    solution = extract_section(content, "解決策")
    if solution:
        extracted.append({
            "title": "Debug Solution: " + solution.split('\n')[0][:50],
            "content": solution,
            "type": "solution",
            "source_file": str(debug_file)
        })
    
    return extracted

def sync_history_file():
    """context/history.mdから決定事項を抽出"""
    history_file = Path(".claude/context/history.md")
    if not history_file.exists():
        return []
        
    content = history_file.read_text(encoding='utf-8')
    extracted = []
    
    # ADR（Architecture Decision Record）を抽出
    adr_pattern = r"### \[(\d{4}-\d{2}-\d{2})\] (.+?)\n.*?- \*\*決定\*\*:\s*(.+?)\n.*?- \*\*理由\*\*:\s*(.+?)\n"
    
    for match in re.finditer(adr_pattern, content, re.DOTALL):
        date = match.group(1)
        title = match.group(2)
        decision = match.group(3)
        reason = match.group(4)
        
        extracted.append({
            "title": f"ADR: {title}",
            "content": f"決定: {decision}\n理由: {reason}",
            "type": "decision",
            "source_file": str(history_file),
            "tags": ["adr", date]
        })
    
    return extracted

def sync_current_file():
    """core/current.mdから学習内容を抽出"""
    current_file = Path(".claude/core/current.md") 
    if not current_file.exists():
        return []
        
    content = current_file.read_text(encoding='utf-8')
    extracted = []
    
    # 学習内容セクションを抽出
    learning = extract_section(content, "今週学んだこと")
    if learning:
        # 各学習項目を分割
        for line in learning.split('\n'):
            if line.strip().startswith('- '):
                item = line.strip()[2:]  # "- "を除去
                if ':' in item:
                    tech, effect = item.split(':', 1)
                    extracted.append({
                        "title": f"Learning: {tech.strip()}",
                        "content": effect.strip(),
                        "type": "memo",
                        "source_file": str(current_file),
                        "tags": ["learning"]
                    })
    
    return extracted

def get_file_timestamp(file_path: str) -> float:
    """ファイルのタイムスタンプを取得"""
    try:
        return os.path.getmtime(file_path)
    except OSError:
        return 0.0

def get_last_sync_times() -> Dict[str, float]:
    """最終同期時刻を取得"""
    sync_file = Path(".claude/index/.last_sync_times")
    if not sync_file.exists():
        return {}
    
    try:
        with open(sync_file, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def update_sync_times(file_times: Dict[str, float]):
    """最終同期時刻を更新"""
    sync_file = Path(".claude/index/.last_sync_times")
    sync_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(sync_file, 'w') as f:
        json.dump(file_times, f, indent=2)

def is_file_changed(file_path: str, last_sync_times: Dict[str, float]) -> bool:
    """ファイルが変更されたかチェック"""
    current_time = get_file_timestamp(file_path)
    last_time = last_sync_times.get(file_path, 0.0)
    return current_time > last_time

def sync_file_by_type(file_path: str) -> List[Dict]:
    """ファイルタイプに応じて同期処理を実行"""
    file_path_obj = Path(file_path)
    
    if file_path_obj.name == "latest.md" and "debug" in file_path:
        return sync_debug_file()
    elif file_path_obj.name == "history.md" and "context" in file_path:
        return sync_history_file()
    elif file_path_obj.name == "current.md" and "core" in file_path:
        return sync_current_file()
    else:
        return []

def sync_incremental(file_paths: List[str] = None) -> int:
    """インクリメンタル同期（変更されたファイルのみ）"""
    if file_paths is None:
        file_paths = [
            ".claude/debug/latest.md",
            ".claude/context/history.md",
            ".claude/core/current.md"
        ]
    
    last_sync_times = get_last_sync_times()
    changed_files = []
    
    for file_path in file_paths:
        if os.path.exists(file_path) and is_file_changed(file_path, last_sync_times):
            changed_files.append(file_path)
    
    if not changed_files:
        print("📝 変更されたファイルはありません")
        return 0
    
    return sync_batch(changed_files)

def sync_batch(file_paths: List[str]) -> int:
    """バッチ処理（複数ファイルを一括処理）"""
    store = OptimizedKnowledgeStore.get_instance(".")
    total_synced = 0
    last_sync_times = get_last_sync_times()
    
    try:
        # バッチ処理用のアイテムリスト
        batch_items = []
        
        for file_path in file_paths:
            if not os.path.exists(file_path):
                continue
                
            items = sync_file_by_type(file_path)
            batch_items.extend(items)
            
            # 同期時刻を更新
            last_sync_times[file_path] = get_file_timestamp(file_path)
        
        # バッチ処理で一括追加
        if batch_items:
            added_ids = store.add_batch(batch_items, skip_duplicates=True)
            total_synced = len(added_ids)
            
            # 結果表示
            for i, item in enumerate(batch_items):
                if i < len(added_ids):
                    file_name = Path(item["source_file"]).name if item["source_file"] else "unknown"
                    print(f"✓ {file_name}同期: {item['title']} (ID: {added_ids[i]})")
        
        # 同期時刻をファイルに保存
        update_sync_times(last_sync_times)
        
        if total_synced > 0:
            print(f"\n🎉 バッチ同期完了: {total_synced}件の知識を追加しました")
        else:
            print("📝 同期対象となる新しい情報はありませんでした")
            
    except Exception as e:
        print(f"❌ 同期エラー: {e}")
    finally:
        # OptimizedKnowledgeStoreはシングルトンなので、明示的に閉じない
        pass
    
    return total_synced

def sync_smart(file_paths: List[str] = None) -> int:
    """スマート同期（重要なファイルのみ、変更チェック付き）"""
    if file_paths is None:
        # 重要なファイルのみ対象
        file_paths = [
            ".claude/core/current.md",
            ".claude/core/next.md",
            ".claude/context/history.md",
            ".claude/debug/latest.md"
        ]
    
    return sync_incremental(file_paths)

def sync_all():
    """すべてのMarkdownファイルを同期（従来の動作）"""
    file_paths = [
        ".claude/debug/latest.md",
        ".claude/context/history.md",
        ".claude/core/current.md"
    ]
    
    return sync_batch(file_paths)

def sync_with_stats() -> Dict:
    """統計情報付きで同期実行"""
    start_time = time.time()
    
    # 同期実行
    synced_count = sync_all()
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    # 統計情報取得
    store = OptimizedKnowledgeStore.get_instance(".")
    stats = store.get_stats()
    
    return {
        "synced_count": synced_count,
        "elapsed_time": elapsed,
        "total_items": stats["total_items"],
        "by_type": stats["by_type"]
    }

def main():
    """メイン関数"""
    if len(sys.argv) > 1:
        action = sys.argv[1]
        
        if action == "debug":
            items = sync_debug_file()
            print(f"Debug抽出: {len(items)}件")
            for item in items:
                print(f"  - {item['title']}")
                
        elif action == "history":
            items = sync_history_file()
            print(f"History抽出: {len(items)}件")
            for item in items:
                print(f"  - {item['title']}")
                
        elif action == "current":
            items = sync_current_file()
            print(f"Current抽出: {len(items)}件")
            for item in items:
                print(f"  - {item['title']}")
                
        elif action == "incremental":
            # インクリメンタル同期
            file_paths = sys.argv[2:] if len(sys.argv) > 2 else None
            if file_paths:
                # 引数で指定されたファイルのみ
                sync_incremental(file_paths)
            else:
                # デフォルトの重要ファイル
                sync_incremental()
                
        elif action == "batch":
            # バッチ処理
            file_paths = sys.argv[2:] if len(sys.argv) > 2 else [
                ".claude/debug/latest.md",
                ".claude/context/history.md",
                ".claude/core/current.md"
            ]
            sync_batch(file_paths)
            
        elif action == "smart":
            # スマート同期
            file_paths = sys.argv[2:] if len(sys.argv) > 2 else None
            sync_smart(file_paths)
            
        elif action == "stats":
            # 統計情報付き同期
            result = sync_with_stats()
            print(f"\n📊 同期統計:")
            print(f"  同期件数: {result['synced_count']}件")
            print(f"  実行時間: {result['elapsed_time']:.2f}秒")
            print(f"  総件数: {result['total_items']}件")
            print(f"  タイプ別: {result['by_type']}")
            
        elif action == "info":
            # データベース情報表示
            store = OptimizedKnowledgeStore.get_instance(".")
            stats = store.get_stats()
            print(f"\n📊 Memory Bank 情報:")
            print(f"  データベース: {stats['db_path']}")
            print(f"  総件数: {stats['total_items']}件")
            print(f"  タイプ別件数:")
            for type_name, count in stats['by_type'].items():
                print(f"    {type_name}: {count}件")
            
        else:
            print("Usage: sync_markdown.py [debug|history|current|incremental|batch|smart] [file_paths...]")
            print("")
            print("同期モード:")
            print("  incremental - 変更されたファイルのみ同期")
            print("  batch       - 指定されたファイルを一括同期")
            print("  smart       - 重要なファイルのみ変更チェック付き同期")
            print("  stats       - 統計情報付きで同期実行")
            print("  info        - データベース情報表示")
            print("抽出モード:")
            print("  debug       - デバッグファイルのみ抽出")
            print("  history     - 履歴ファイルのみ抽出")
            print("  current     - 現在状況ファイルのみ抽出")
            print("")
            print("引数なしで実行すると全ファイルを同期します")
    else:
        sync_all()

if __name__ == "__main__":
    main()