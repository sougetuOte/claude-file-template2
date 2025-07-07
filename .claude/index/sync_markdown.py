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
from pathlib import Path

# knowledge_storeモジュールをインポート
sys.path.append(os.path.dirname(__file__))
from knowledge_store import KnowledgeStore

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

def sync_all():
    """すべてのMarkdownファイルを同期"""
    store = KnowledgeStore(".")
    total_synced = 0
    
    try:
        # デバッグファイル同期
        debug_items = sync_debug_file()
        for item in debug_items:
            id = store.add(
                title=item["title"],
                content=item["content"],
                type=item["type"],
                tags=item.get("tags", []),
                source_file=item["source_file"]
            )
            print(f"✓ Debug同期: {item['title']} (ID: {id})")
            total_synced += 1
        
        # 履歴ファイル同期
        history_items = sync_history_file()
        for item in history_items:
            id = store.add(
                title=item["title"],
                content=item["content"],
                type=item["type"],
                tags=item.get("tags", []),
                source_file=item["source_file"]
            )
            print(f"✓ History同期: {item['title']} (ID: {id})")
            total_synced += 1
        
        # 現在状況ファイル同期
        current_items = sync_current_file()
        for item in current_items:
            id = store.add(
                title=item["title"],
                content=item["content"],
                type=item["type"],
                tags=item.get("tags", []),
                source_file=item["source_file"]
            )
            print(f"✓ Current同期: {item['title']} (ID: {id})")
            total_synced += 1
        
        if total_synced > 0:
            print(f"\n🎉 Markdown同期完了: {total_synced}件の知識を追加しました")
        else:
            print("📝 同期対象となる新しい情報はありませんでした")
            
    except Exception as e:
        print(f"❌ 同期エラー: {e}")
    finally:
        store.close()

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
        else:
            print("Usage: sync_markdown.py [debug|history|current]")
            print("引数なしで実行すると全ファイルを同期します")
    else:
        sync_all()

if __name__ == "__main__":
    main()