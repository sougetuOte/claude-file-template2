#!/usr/bin/env node
/**
 * Memory Bank 2.0 MCP Server
 * セキュアなMCPサーバー実装 (CVE-2025-49596対策)
 */

import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

/**
 * セキュリティマネージャー
 * CVE-2025-49596対策
 */
class SecurityManager {
  static MAX_REQUEST_SIZE = 10 * 1024; // 10KB
  static RATE_LIMIT = 100; // requests per minute
  
  constructor() {
    this.requestCount = new Map();
  }
  
  validateRequest(request) {
    // サイズチェック
    const requestStr = JSON.stringify(request);
    if (requestStr.length > SecurityManager.MAX_REQUEST_SIZE) {
      return false;
    }
    
    // レート制限（簡易版）
    const clientId = request.clientId || 'default';
    const count = this.requestCount.get(clientId) || 0;
    if (count > SecurityManager.RATE_LIMIT) {
      return false;
    }
    
    this.requestCount.set(clientId, count + 1);
    
    // 1分後にリセット
    setTimeout(() => {
      this.requestCount.delete(clientId);
    }, 60000);
    
    return true;
  }
}

/**
 * Memory Bank MCPサーバー
 */
class MemoryBankMCP {
  constructor(projectPath = '.') {
    this.projectPath = projectPath;
    this.bridgeScript = join(__dirname, 'bridge.py');
    this.security = new SecurityManager();
    this.serverInfo = {
      name: 'memory-bank',
      version: '2.0.0'
    };
    
    console.error('Memory Bank MCP Server 2.0 initializing...');
  }
  
  /**
   * Python Bridgeを呼び出し
   */
  async callPython(method, args) {
    return new Promise((resolve, reject) => {
      const python = spawn('python3', [
        this.bridgeScript,
        method,
        JSON.stringify(args)
      ]);
      
      let output = '';
      let errorOutput = '';
      
      python.stdout.on('data', (data) => {
        output += data.toString();
      });
      
      python.stderr.on('data', (data) => {
        errorOutput += data.toString();
      });
      
      python.on('close', (code) => {
        if (code !== 0) {
          reject(new Error(`Python bridge failed: ${errorOutput}`));
          return;
        }
        
        try {
          const result = JSON.parse(output);
          resolve(result);
        } catch (e) {
          reject(new Error(`Failed to parse Python response: ${output}`));
        }
      });
      
      python.on('error', (err) => {
        reject(new Error(`Failed to spawn Python: ${err.message}`));
      });
    });
  }
  
  /**
   * MCP Request Handler
   */
  async handleRequest(request) {
    // セキュリティ検証
    if (!this.security.validateRequest(request)) {
      return {
        error: {
          code: -32600,
          message: 'Security validation failed'
        }
      };
    }
    
    try {
      const { method, params } = request;
      
      switch (method) {
        case 'initialize':
          return {
            result: {
              serverInfo: this.serverInfo,
              capabilities: {
                tools: {}
              }
            }
          };
          
        case 'tools/list':
          return {
            result: {
              tools: [
                {
                  name: 'knowledge_search',
                  description: 'Memory Bank内を検索',
                  inputSchema: {
                    type: 'object',
                    properties: {
                      query: { type: 'string' },
                      type: { 
                        type: 'string', 
                        enum: ['error', 'solution', 'decision', 'memo', 'code', 'concept'] 
                      },
                      limit: { type: 'number', default: 10 }
                    },
                    required: ['query']
                  }
                },
                {
                  name: 'knowledge_add',
                  description: '知識を追加',
                  inputSchema: {
                    type: 'object',
                    properties: {
                      title: { type: 'string' },
                      content: { type: 'string' },
                      type: { 
                        type: 'string',
                        enum: ['error', 'solution', 'decision', 'memo', 'code', 'concept']
                      },
                      tags: { type: 'array', items: { type: 'string' } },
                      source_file: { type: 'string' }
                    },
                    required: ['title', 'content', 'type']
                  }
                },
                {
                  name: 'knowledge_link',
                  description: '知識間のリンクを作成',
                  inputSchema: {
                    type: 'object',
                    properties: {
                      from_id: { type: 'number' },
                      to_id: { type: 'number' },
                      link_type: { 
                        type: 'string',
                        enum: ['solves', 'causes', 'related', 'implements', 'references']
                      }
                    },
                    required: ['from_id', 'to_id', 'link_type']
                  }
                },
                {
                  name: 'knowledge_related',
                  description: '関連する知識を取得',
                  inputSchema: {
                    type: 'object',
                    properties: {
                      id: { type: 'number' }
                    },
                    required: ['id']
                  }
                }
              ]
            }
          };
          
        case 'tools/call':
          return await this.handleToolCall(params);
          
        default:
          return {
            error: {
              code: -32601,
              message: `Method not found: ${method}`
            }
          };
      }
    } catch (error) {
      console.error('Request handling error:', error);
      return {
        error: {
          code: -32603,
          message: `Internal error: ${error.message}`
        }
      };
    }
  }
  
  /**
   * ツール呼び出しハンドラー
   */
  async handleToolCall(params) {
    const { name, arguments: args } = params;
    
    try {
      let result;
      
      switch (name) {
        case 'knowledge_search':
          result = await this.callPython('search', args);
          break;
          
        case 'knowledge_add':
          result = await this.callPython('add', args);
          break;
          
        case 'knowledge_link':
          result = await this.callPython('link', args);
          break;
          
        case 'knowledge_related':
          result = await this.callPython('related', args);
          break;
          
        default:
          return {
            error: {
              code: -32602,
              message: `Unknown tool: ${name}`
            }
          };
      }
      
      // Python Bridgeからのエラーをチェック
      if (result.error) {
        return {
          error: {
            code: -32603,
            message: result.error
          }
        };
      }
      
      return {
        result: {
          content: [{
            type: 'text',
            text: JSON.stringify(result, null, 2)
          }]
        }
      };
      
    } catch (error) {
      return {
        error: {
          code: -32603,
          message: `Tool execution failed: ${error.message}`
        }
      };
    }
  }
  
  /**
   * Stdio Transport (MCPプロトコル)
   */
  async run() {
    console.error('Memory Bank MCP Server 2.0 started');
    console.error('Waiting for requests on stdin...');
    
    let buffer = '';
    
    process.stdin.on('data', async (chunk) => {
      buffer += chunk.toString();
      
      // JSON-RPC メッセージの完成をチェック
      const lines = buffer.split('\n');
      buffer = lines.pop(); // 未完成の行を保持
      
      for (const line of lines) {
        if (line.trim()) {
          try {
            const request = JSON.parse(line);
            const response = await this.handleRequest(request);
            
            // レスポンスにIDを追加
            if (request.id !== undefined) {
              response.id = request.id;
            }
            
            console.log(JSON.stringify(response));
          } catch (error) {
            console.error('Failed to parse request:', error);
            console.log(JSON.stringify({
              error: {
                code: -32700,
                message: 'Parse error'
              }
            }));
          }
        }
      }
    });
    
    process.stdin.on('end', () => {
      console.error('Memory Bank MCP Server shutting down');
      process.exit(0);
    });
  }
}

// サーバー起動
const projectPath = process.env.PROJECT_PATH || '.';
const server = new MemoryBankMCP(projectPath);
server.run().catch(console.error);