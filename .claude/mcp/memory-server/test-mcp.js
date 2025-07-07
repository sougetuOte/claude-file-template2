#!/usr/bin/env node
/**
 * Memory Bank MCP Server テスト
 */

import { spawn } from 'child_process';

async function testMCPServer() {
  console.log('🧪 Memory Bank MCP Server テスト開始...');
  
  // MCPサーバーを起動
  const server = spawn('node', ['index.js'], {
    cwd: process.cwd(),
    env: { ...process.env, PROJECT_PATH: '../../..' }
  });
  
  let responses = [];
  
  // レスポンスを収集
  server.stdout.on('data', (data) => {
    const lines = data.toString().split('\n').filter(line => line.trim());
    for (const line of lines) {
      try {
        const response = JSON.parse(line);
        responses.push(response);
        console.log('📨 Response:', JSON.stringify(response, null, 2));
      } catch (e) {
        console.log('📝 Raw output:', line);
      }
    }
  });
  
  server.stderr.on('data', (data) => {
    console.log('🔍 Server log:', data.toString().trim());
  });
  
  // テストリクエストを送信
  const tests = [
    // 1. Initialization
    {
      id: 1,
      method: 'initialize',
      params: {}
    },
    
    // 2. List tools
    {
      id: 2,
      method: 'tools/list',
      params: {}
    },
    
    // 3. Search knowledge
    {
      id: 3,
      method: 'tools/call',
      params: {
        name: 'knowledge_search',
        arguments: {
          query: 'JWT'
        }
      }
    },
    
    // 4. Add knowledge
    {
      id: 4,
      method: 'tools/call',
      params: {
        name: 'knowledge_add',
        arguments: {
          title: 'MCP_SERVER_TEST',
          content: 'MCPサーバー動作テスト',
          type: 'memo'
        }
      }
    }
  ];
  
  // テストリクエストを順次送信
  for (let i = 0; i < tests.length; i++) {
    const test = tests[i];
    console.log(`\n🚀 Test ${i + 1}: ${test.method}`);
    
    server.stdin.write(JSON.stringify(test) + '\n');
    
    // 少し待機
    await new Promise(resolve => setTimeout(resolve, 500));
  }
  
  // テスト終了
  setTimeout(() => {
    console.log('\n✅ テスト完了');
    server.kill();
    process.exit(0);
  }, 2000);
}

testMCPServer().catch(console.error);