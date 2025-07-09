#!/usr/bin/env node
/**
 * Vibe Logger TypeScript/Node.js使用例
 * AI支援開発のための構造化ログの実践的な使い方
 */

import { createFileLogger, Logger } from 'vibelogger';

// ロガーの作成
const logger: Logger = createFileLogger('claude_project_ts');

/**
 * 基本的なログ記録の例
 */
function exampleBasicLogging(): void {
    console.log('=== 基本的なログ記録 ===');
    
    // 情報ログ
    logger.info({
        operation: 'user.login',
        message: 'ユーザーログイン成功',
        context: {
            userId: 'user_123',
            loginMethod: 'oauth2',
            ipAddress: '192.168.1.100',
            userAgent: 'Mozilla/5.0...'
        },
        humanNote: 'AI-TODO: ログイン成功率の統計を実装'
    });
    
    // 警告ログ
    logger.warning({
        operation: 'api.rate_limit',
        message: 'APIレート制限に近づいています',
        context: {
            currentRequests: 950,
            limit: 1000,
            resetTime: new Date('2024-01-01T12:00:00Z').toISOString(),
            endpoint: '/api/v1/users'
        },
        humanNote: 'AI-REVIEW: レート制限の緩和戦略を検討'
    });
    
    // エラーログ
    logger.error({
        operation: 'database.connection',
        message: 'データベース接続エラー',
        context: {
            errorCode: 'ECONNREFUSED',
            host: 'localhost',
            port: 5432,
            retryAttempts: 3,
            lastSuccess: new Date('2024-01-01T11:30:00Z').toISOString()
        },
        humanNote: 'AI-FIXME: 接続プールの設定を見直し、自動リトライを実装'
    });
}

/**
 * 非同期操作のログ記録
 */
async function exampleAsyncLogging(): Promise<void> {
    console.log('\n=== 非同期操作のログ ===');
    
    const operationId = crypto.randomUUID();
    
    // 非同期操作開始
    logger.info({
        operation: 'async.task.start',
        message: '非同期タスク開始',
        context: {
            operationId,
            taskType: 'data_processing',
            expectedDuration: '5-10 seconds'
        }
    });
    
    try {
        // 非同期処理のシミュレーション
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        logger.info({
            operation: 'async.task.complete',
            message: '非同期タスク完了',
            context: {
                operationId,
                duration: 1000,
                result: 'success'
            }
        });
    } catch (error) {
        logger.error({
            operation: 'async.task.failed',
            message: `非同期タスク失敗: ${error}`,
            context: {
                operationId,
                error: error instanceof Error ? error.message : String(error),
                stack: error instanceof Error ? error.stack : undefined
            },
            humanNote: 'AI-DEBUG: 非同期エラーの原因を調査'
        });
    }
}

/**
 * Express.jsミドルウェアの例
 */
function createLoggingMiddleware() {
    return (req: any, res: any, next: any) => {
        const startTime = Date.now();
        const requestId = crypto.randomUUID();
        
        // リクエスト開始ログ
        logger.info({
            operation: 'http.request.start',
            message: 'HTTPリクエスト受信',
            context: {
                requestId,
                method: req.method,
                path: req.path,
                query: req.query,
                ip: req.ip
            }
        });
        
        // レスポンス完了時のログ
        res.on('finish', () => {
            const duration = Date.now() - startTime;
            
            logger.info({
                operation: 'http.request.complete',
                message: 'HTTPリクエスト完了',
                context: {
                    requestId,
                    statusCode: res.statusCode,
                    duration,
                    contentLength: res.get('content-length')
                },
                humanNote: duration > 1000 ? 'AI-OPTIMIZE: レスポンスタイムが遅い' : undefined
            });
        });
        
        next();
    };
}

/**
 * エラーバウンダリーの例
 */
class VibeErrorBoundary {
    static wrap<T extends (...args: any[]) => any>(
        fn: T,
        operation: string
    ): T {
        return (async (...args: Parameters<T>): Promise<ReturnType<T>> => {
            try {
                return await fn(...args);
            } catch (error) {
                logger.error({
                    operation: `${operation}.error`,
                    message: error instanceof Error ? error.message : String(error),
                    context: {
                        functionName: fn.name,
                        arguments: args.slice(0, 3), // 最初の3つの引数のみ
                        errorType: error?.constructor?.name,
                        stack: error instanceof Error ? error.stack : undefined
                    },
                    humanNote: 'AI-FIXME: このエラーの修正方法を提案してください'
                });
                throw error;
            }
        }) as T;
    }
}

/**
 * パフォーマンス計測の例
 */
class PerformanceLogger {
    private operations = new Map<string, number>();
    
    start(operation: string, context?: any): void {
        this.operations.set(operation, Date.now());
        
        logger.debug({
            operation: `${operation}.start`,
            message: `${operation}開始`,
            context
        });
    }
    
    end(operation: string, context?: any): void {
        const startTime = this.operations.get(operation);
        if (!startTime) {
            logger.warning({
                operation: `${operation}.timing_error`,
                message: '開始時刻が記録されていません',
                context
            });
            return;
        }
        
        const duration = Date.now() - startTime;
        this.operations.delete(operation);
        
        logger.info({
            operation: `${operation}.complete`,
            message: `${operation}完了`,
            context: {
                ...context,
                durationMs: duration,
                performance: duration < 100 ? 'fast' : duration < 1000 ? 'normal' : 'slow'
            },
            humanNote: duration > 1000 ? 'AI-OPTIMIZE: パフォーマンス改善の余地あり' : undefined
        });
    }
}

/**
 * WebSocketログの例
 */
function exampleWebSocketLogging(): void {
    console.log('\n=== WebSocketログ ===');
    
    const connectionId = crypto.randomUUID();
    
    // 接続イベント
    logger.info({
        operation: 'websocket.connect',
        message: 'WebSocket接続確立',
        context: {
            connectionId,
            protocol: 'wss',
            endpoint: '/ws/chat'
        }
    });
    
    // メッセージ受信
    logger.debug({
        operation: 'websocket.message.received',
        message: 'メッセージ受信',
        context: {
            connectionId,
            messageType: 'chat',
            size: 256
        }
    });
    
    // エラーハンドリング
    logger.error({
        operation: 'websocket.error',
        message: '接続エラー',
        context: {
            connectionId,
            code: 1006,
            reason: 'Abnormal Closure'
        },
        humanNote: 'AI-DEBUG: WebSocket切断の原因を調査'
    });
}

/**
 * 実用的なヘルパー関数
 */
const vibeLog = {
    request: (method: string, url: string, context?: any) => {
        logger.info({
            operation: 'http.client.request',
            message: `${method} ${url}`,
            context: { method, url, ...context }
        });
    },
    
    database: (query: string, params?: any[], duration?: number) => {
        logger.info({
            operation: 'database.query',
            message: 'データベースクエリ実行',
            context: {
                query: query.substring(0, 100), // 最初の100文字
                paramCount: params?.length || 0,
                duration
            }
        });
    },
    
    cache: (action: 'hit' | 'miss' | 'set', key: string, context?: any) => {
        logger.debug({
            operation: `cache.${action}`,
            message: `キャッシュ${action}`,
            context: { key, ...context }
        });
    }
};

// メイン実行
async function main(): Promise<void> {
    console.log('=== Vibe Logger TypeScript 使用例 ===\n');
    
    // 基本的なログ記録
    exampleBasicLogging();
    
    // 非同期操作
    await exampleAsyncLogging();
    
    // WebSocketログ
    exampleWebSocketLogging();
    
    // パフォーマンス計測
    const perf = new PerformanceLogger();
    perf.start('heavy_computation');
    await new Promise(resolve => setTimeout(resolve, 500));
    perf.end('heavy_computation', { result: 'completed' });
    
    // ヘルパー関数の使用
    vibeLog.request('GET', 'https://api.example.com/users');
    vibeLog.database('SELECT * FROM users WHERE id = ?', [123], 45);
    vibeLog.cache('hit', 'user:123');
    
    console.log('\n✅ すべての例が完了しました！');
    console.log('ログは ./claude_project_ts_logs/ ディレクトリに保存されています。');
}

// エラーハンドリング付きで実行
if (require.main === module) {
    main().catch(error => {
        logger.error({
            operation: 'main.error',
            message: 'メインプロセスエラー',
            context: {
                error: error.message,
                stack: error.stack
            },
            humanNote: 'AI-FIXME: アプリケーション起動エラーを修正'
        });
        process.exit(1);
    });
}