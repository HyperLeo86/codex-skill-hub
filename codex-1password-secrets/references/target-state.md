# 目标状态 · 差距映射 · 动作表 · 验收清单

## 1. 目标状态（TO-BE）

所有凭据（网站密码、GitHub、API Key、SSH 私钥）统一存于 1Password；Codex 通过本地 MCP Server、`op` CLI、Shell Plugins、SSH Agent 按需获取；密钥值不进入模型上下文，明文不落盘；每次访问有桌面端授权。

| 组件 | 目标状态 |
| --- | --- |
| 1Password 桌面端 | 已安装；内置 `onepassword-mcp`、`op-ssh-sign` |
| `op` CLI | 已安装（≥2.33.0-beta.02 才支持 Environments 命令；稳定版可注入与插件）；CLI 集成开启 |
| SSH Agent | `~/.ssh/config` 的 `IdentityAgent` 指向 1Password；SSH Key 均为 1Password 条目 |
| Codex MCP | 桌面端 Labs MCP Server 开启；Codex 配置 `onepassword-mcp`；官方插件/技能已装 |
| CLI 认证 | `gh` 通过 Shell Plugin 或 `op run` 注入，无明文 Token 文件 |
| 环境变量 | 项目 `.env` 由 Environments 本地挂载；`.env.tpl` 只含 `op://` 引用；`.env` 不入库 |
| Codex 加固 | `~/.codex/config.toml` 含 `[shell_environment_policy]`（见 §4） |

## 2. 差距映射表

| 审计输出 | 差距 |
| --- | --- |
| A1 无 `1Password.app` 或无可执行二进制 | G1 |
| A2 `MISSING` 或版本 < 2.33.0-beta.02 | G2 |
| A3 无 `IdentityAgent` 或 `agent has no identities` | G3 |
| A4 `MISSING` 或未登录 | G5 |
| A5 `codex mcp list` 无 `1password` | G4 |
| A5 无 `shell_environment_policy` | G7 |
| A6 `.env` 存在且非挂载 / 检出明文密钥 | G6 / G8 |

## 3. 动作表（G1-G8）

- **G1**：安装 1Password 8 并登录；验证 `ls /Applications/1Password.app/Contents/MacOS/onepassword-mcp`。
- **G2**：`brew install 1password-cli`；桌面端 `Settings > Developer > Integrate with 1Password CLI`；验证 `op vault list` 弹授权。
- **G3**：桌面端启用 SSH Agent；新建 `SSH Key` 条目（Ed25519）；公钥上传 GitHub/服务器；验证 `ssh -T git@github.com`。服务器清单缺失时输出待办，不猜测。
- **G4**：桌面端 `Labs > MCP Server` 开启 + `Developer > Integrate with MCP clients`；Codex 配置：
  `[mcp_servers.1password] command = "/Applications/1Password.app/Contents/MacOS/onepassword-mcp"`；安装官方插件 `1Password/1password-codex-plugin`；自定义指令声明优先使用；验证 `codex mcp list`。
- **G5**：`op plugin init` 选择 gh/codex；`source ~/.config/op/plugins.sh` 写入 `~/.zshrc`；字段对齐 `Token→GH_TOKEN`、`API Key→OPENAI_API_KEY`；验证 `op plugin run gh auth status`。
- **G6**：桌面端 `Developer > Environments` 新建 Environment（命名 `<项目>-<环境>`）；导入 `.env`/加变量；`Destinations > Local .env file` 挂载；仓库保留 `.env.tpl`；验证应用可读到变量。
- **G7**：向 `~/.codex/config.toml` 写入 §4 配置块（先备份，禁止覆盖既有键）；重启 Codex；验证 `rg shell_environment_policy ~/.codex/config.toml`。
- **G8**：旋转曾明文/入库的密钥；`git rm --cached .env`；补 `.gitignore`（`.env`、`.env.*`、`!.env.tpl`、`*.local`、`.codex/`、`.claude/`）；删除 shell 配置中的明文 `export`；验证搜索无命中。

## 4. 目标配置块（~/.codex/config.toml）

```toml
[shell_environment_policy]
inherit = "core"
ignore_default_excludes = false

[shell_environment_policy.filters]
"AWS_*" = "exclude"
"AZURE_*" = "exclude"
"*_TOKEN" = "exclude"
"*_KEY" = "exclude"
"*_SECRET*" = "exclude"
```

注意：`[shell_environment_policy]` 父表键必须写在 `[shell_environment_policy.set]` 等子表之前，否则 TOML 非法；改完用 `python3 -c "import tomllib; tomllib.load(open('...'))"` 验证。

## 5. 验收清单

| # | 检查项 | 通过标准 |
| --- | --- | --- |
| 1 | `op --version` | ≥ 2.33.0-beta.02（或稳定版已装） |
| 2 | `op vault list` | 弹 1Password 授权并列出 Vault |
| 3 | `ssh -T git@github.com` | 返回 `Hi <name>!` |
| 4 | `codex mcp list` | 含 `1password` |
| 5 | MCP `list_variables` | 只返回变量名 |
| 6 | `op plugin run gh auth status` | 已登录且无明文 Token 文件 |
| 7 | `.env` 挂载 | 应用能读到变量 |
| 8 | `rg shell_environment_policy ~/.codex/config.toml` | 有命中 |
| 9 | shell/config 明文搜索 | 无命中 |
| 10 | `git ls-files` | 无 `.env` |

## 6. 已知限制

- 稳定版 `op`（2.38.x）无 `op environment` 命令（beta CLI 才有）；Environments 操作以桌面端/MCP 为准。
- 本地 `.env` 挂载（FIFO）不支持并发读取；Vite 等 watch 工具需忽略 `**/.env`；每设备最多 10 个挂载。
- `op plugin run -- gh` 在非交互子进程可能报 interactive IO 错误（1Password/shell-plugins#575）。
- MCP Server 为 beta：需 Labs 开关 + 账户的 Developer Environments 权限；仅 macOS/Linux。
