#!/usr/bin/env python3
"""
Vibe Logger使用例
AI支援開発のための構造化ログの実践的な使い方
"""

# vibeloggerがインストールされていない場合の警告
try:
    from vibelogger import create_file_logger
except ImportError:
    print("vibeloggerをインストールしてください: pip install vibelogger")
    exit(1)

from sync_vibe_logs import vibe_log, vibe_error_handler, VibeMemoryBankSync


# 基本的な使い方
def example_basic_logging():
    """基本的なログ記録の例"""
    # 通常の情報ログ
    vibe_log(
        level="INFO",
        operation="user.login",
        message="ユーザーログイン成功",
        context={
            "user_id": "user_123",
            "login_method": "oauth2",
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0..."
        },
        human_note="AI-TODO: ログイン成功率の統計を実装"
    )
    
    # 警告ログ
    vibe_log(
        level="WARNING",
        operation="api.rate_limit",
        message="APIレート制限に近づいています",
        context={
            "current_requests": 950,
            "limit": 1000,
            "reset_time": "2024-01-01T12:00:00Z",
            "endpoint": "/api/v1/users"
        },
        human_note="AI-REVIEW: レート制限の緩和戦略を検討"
    )
    
    # エラーログ
    vibe_log(
        level="ERROR",
        operation="database.connection",
        message="データベース接続エラー",
        context={
            "error_code": "ECONNREFUSED",
            "host": "localhost",
            "port": 5432,
            "retry_attempts": 3,
            "last_success": "2024-01-01T11:30:00Z"
        },
        human_note="AI-FIXME: 接続プールの設定を見直し、自動リトライを実装"
    )


# エラーハンドリングの例
@vibe_error_handler
def risky_operation(data):
    """エラーが発生する可能性のある処理"""
    if not data:
        raise ValueError("データが空です")
    
    # 何か危険な処理
    result = 10 / data.get('divisor', 0)
    return result


# 実践的な使用例：API呼び出しのログ
def example_api_logging():
    """API呼び出しの詳細なログ記録"""
    import time
    import requests
    
    # リクエスト開始
    start_time = time.time()
    
    vibe_log(
        level="INFO",
        operation="external_api.request.start",
        message="外部API呼び出し開始",
        context={
            "endpoint": "https://api.example.com/v1/users",
            "method": "GET",
            "params": {"limit": 100, "offset": 0},
            "headers": {"Authorization": "Bearer [MASKED]"}
        }
    )
    
    try:
        # 実際のAPI呼び出し（シミュレーション）
        # response = requests.get(...)
        response_time = time.time() - start_time
        
        vibe_log(
            level="INFO",
            operation="external_api.request.success",
            message="外部API呼び出し成功",
            context={
                "status_code": 200,
                "response_time_ms": round(response_time * 1000, 2),
                "response_size_bytes": 4096,
                "rate_limit_remaining": 450
            },
            human_note="AI-OPTIMIZE: レスポンスタイムが遅い場合の最適化案を提案"
        )
        
    except Exception as e:
        response_time = time.time() - start_time
        
        vibe_log(
            level="ERROR",
            operation="external_api.request.failed",
            message=f"外部API呼び出し失敗: {str(e)}",
            context={
                "error_type": type(e).__name__,
                "response_time_ms": round(response_time * 1000, 2),
                "retry_possible": True,
                "fallback_available": False
            },
            human_note="AI-FIXME: エラーハンドリングとリトライロジックの改善"
        )


# データ処理パイプラインの例
def example_pipeline_logging():
    """データ処理パイプラインでの構造化ログ"""
    
    # パイプライン開始
    pipeline_id = "pipeline_20240101_120000"
    
    vibe_log(
        level="INFO",
        operation="data_pipeline.start",
        message="データ処理パイプライン開始",
        context={
            "pipeline_id": pipeline_id,
            "input_files": ["data1.csv", "data2.csv"],
            "total_size_mb": 150.5,
            "steps": ["validate", "transform", "aggregate", "export"]
        }
    )
    
    # 各ステップのログ
    steps = [
        ("validate", "データ検証", {"invalid_records": 5, "total_records": 10000}),
        ("transform", "データ変換", {"transformed_records": 9995, "skipped": 5}),
        ("aggregate", "データ集計", {"groups": 50, "metrics": ["sum", "avg", "count"]}),
        ("export", "データエクスポート", {"output_file": "result.parquet", "size_mb": 45.2})
    ]
    
    for step_name, step_desc, step_context in steps:
        vibe_log(
            level="INFO",
            operation=f"data_pipeline.step.{step_name}",
            message=f"{step_desc}完了",
            context={
                "pipeline_id": pipeline_id,
                "step": step_name,
                **step_context
            }
        )


# 検索とサマリーの例
def example_search_and_summary():
    """ログの検索とサマリー機能の例"""
    sync = VibeMemoryBankSync()
    
    # エラーログを検索
    print("\n=== エラーログの検索 ===")
    error_logs = sync.search_logs("error", level="ERROR")
    for log in error_logs[:5]:  # 最初の5件
        print(f"- {log['title']}")
    
    # 特定の操作のログを検索
    print("\n=== API関連ログの検索 ===")
    api_logs = sync.search_logs("api", operation="external_api")
    for log in api_logs[:5]:
        print(f"- {log['title']}")
    
    # エラーサマリー
    print("\n=== エラーサマリー（過去7日間） ===")
    summary = sync.get_error_summary(days=7)
    for operation, count in summary.items():
        print(f"  {operation}: {count}件")


# パフォーマンス計測の例
def example_performance_logging():
    """パフォーマンス計測を含むログ"""
    import time
    
    # 処理時間を計測するコンテキストマネージャー
    class TimedOperation:
        def __init__(self, operation_name):
            self.operation_name = operation_name
            self.start_time = None
            
        def __enter__(self):
            self.start_time = time.time()
            vibe_log(
                level="DEBUG",
                operation=f"{self.operation_name}.start",
                message=f"{self.operation_name}開始",
                context={"timestamp": self.start_time}
            )
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            duration = time.time() - self.start_time
            
            if exc_type is None:
                vibe_log(
                    level="INFO",
                    operation=f"{self.operation_name}.complete",
                    message=f"{self.operation_name}完了",
                    context={
                        "duration_ms": round(duration * 1000, 2),
                        "success": True
                    },
                    human_note="AI-OPTIMIZE: 処理時間が1秒を超える場合は最適化を検討" if duration > 1 else None
                )
            else:
                vibe_log(
                    level="ERROR",
                    operation=f"{self.operation_name}.failed",
                    message=f"{self.operation_name}失敗: {exc_val}",
                    context={
                        "duration_ms": round(duration * 1000, 2),
                        "error_type": exc_type.__name__,
                        "error_message": str(exc_val)
                    },
                    human_note="AI-FIXME: エラーの原因を調査し、修正案を提示"
                )
    
    # 使用例
    with TimedOperation("heavy_calculation"):
        # 重い処理のシミュレーション
        time.sleep(0.5)
        result = sum(range(1000000))


# メイン実行
if __name__ == "__main__":
    print("=== Vibe Logger 使用例 ===\n")
    
    print("1. 基本的なログ記録")
    example_basic_logging()
    
    print("\n2. API呼び出しのログ")
    example_api_logging()
    
    print("\n3. データパイプラインのログ")
    example_pipeline_logging()
    
    print("\n4. パフォーマンス計測")
    example_performance_logging()
    
    print("\n5. エラーハンドリング（エラーが発生します）")
    try:
        risky_operation({})  # エラーを意図的に発生させる
    except ValueError:
        print("  エラーがvibe-loggerで記録されました")
    
    print("\n6. ログの検索とサマリー")
    example_search_and_summary()
    
    print("\n✅ すべての例が完了しました！")
    print("ログは .claude/vibe/logs/ ディレクトリに保存されています。")