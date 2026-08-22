#!/usr/bin/env node
/**
 * marketic-mcp - JS wrapper that invokes the Python MCP server
 * Sets PYTHONPATH so the bundled marketic/ package is found
 */
const { spawn } = require('child_process');
const path = require('path');

const scriptDir = __dirname;
const scriptPath = path.join(scriptDir, 'mcp_server.py');

// Set PYTHONPATH to include the npm package directory (where marketic/ lives)
process.env.PYTHONPATH = scriptDir;

const proc = spawn('python3', [scriptPath], {
  cwd: scriptDir,
  stdio: ['pipe', 'pipe', 'pipe']
});

proc.stdout.pipe(process.stdout);
proc.stderr.pipe(process.stderr);
process.stdin.pipe(proc.stdin);

proc.on('exit', (code) => process.exit(code || 0));
