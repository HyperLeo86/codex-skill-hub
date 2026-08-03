#!/usr/bin/env bash
# codex-1password-secrets 只读审计脚本（不修改任何状态）
set -uo pipefail

echo '== A1 1Password 桌面端 =='
ls -d /Applications/1Password.app 2>/dev/null || echo 'MISSING'
ls /Applications/1Password.app/Contents/MacOS/ 2>/dev/null | rg -i 'mcp|op-ssh' || echo 'NO mcp/ssh binaries'

echo '== A2 op CLI =='
command -v op && op --version || echo 'MISSING'

echo '== A3 SSH =='
rg 'IdentityAgent' ~/.ssh/config 2>/dev/null || echo 'NO IdentityAgent'
ssh-add -l 2>&1 | head -3

echo '== A4 gh =='
command -v gh && gh --version | head -1 || echo 'MISSING'
gh auth status 2>&1 | head -4 || true

echo '== A5 Codex =='
command -v codex && codex --version || echo 'MISSING'
codex mcp list 2>&1 | head -12
rg -n 'shell_environment_policy' ~/.codex/config.toml 2>/dev/null || echo 'NO shell_environment_policy'

echo '== A6 项目环境与明文 =='
rg -n '\.env' .gitignore 2>/dev/null || echo 'NO .env in .gitignore'
ls .env .env.tpl 2>/dev/null || true
rg -i '(api[_-]?key|secret|token)\s*=' ~/.zshrc ~/.bashrc ~/.codex/config.toml 2>/dev/null || echo 'NO plaintext secrets found'
