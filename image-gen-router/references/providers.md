# 生图提供方注册表

> 最后验证：2026-08-04。模型与端点以本表为准；控制台或文档变化时先更新本表再使用。

## 1. 阿里通义万相（DashScope）

- 来源：阿里云百炼（通义万相）控制台
- 取 Key：https://bailian.console.aliyun.com → 右上角「API-KEY 管理」
- 环境变量：`DASHSCOPE_API_KEY`
- Base：https://dashscope.aliyuncs.com

| 模型 | 模式 | 端点 | 参数要点 | 状态 |
| --- | --- | --- | --- | --- |
| qwen-image-2.0-pro | 同步 | POST /api/v1/services/aigc/multimodal-generation/generation | parameters.size=1024*1024 | ✅ 2026-08-04 验证 |
| z-image-turbo | 同步 | 同上 | parameters.size=1024*1024、prompt_extend=false | ✅ 2026-08-04 验证 |
| wan2.7-image-pro | 异步 | POST /api/v1/services/aigc/image-generation/generation + GET /api/v1/tasks/{id} | Header `X-DashScope-Async: enable` | ✅ 2026-08-04 验证 |
| kling-v3 / vidu-image | 异步 | 同上 | 同异步参数 | ❌ 未开通（2026-08-04 返回未开通） |

同步请求体示例：

```json
POST /api/v1/services/aigc/multimodal-generation/generation
{
  "model": "qwen-image-2.0-pro",
  "input": {"messages": [{"role": "user", "content": [{"text": "..."}]}]},
  "parameters": {"size": "1024*1024"}
}
```

## 2. 火山方舟（ARK）

- 来源：火山引擎方舟控制台
- 取 Key：https://console.volcengine.com/ark → API Key 管理
- 环境变量：`ARK_API_KEY`（备用 `ARK_API_KEY_ID`）
- Base：https://ark.cn-beijing.volces.com/api/v3

| 模型 | 模式 | 端点 | 参数要点 | 状态 |
| --- | --- | --- | --- | --- |
| doubao-seedream-5-0-pro-260628 | 同步 | POST /images/generations | size=1024x1024、watermark=false、response_format=url | ✅ 2026-08-04 验证 |
| doubao-seedream-5-0-260128 | 同步 | 同上 | 同参数 | ❌ 返回空结果（n=0） |

请求体示例：

```json
POST /images/generations
{
  "model": "doubao-seedream-5-0-pro-260628",
  "prompt": "...",
  "size": "1024x1024",
  "watermark": false,
  "response_format": "url"
}
```

响应取 `data[0].url`（2 小时有效）或 `data[0].b64_json`。

## 新增提供方模板

1. 在 `scripts/imagegen.py` 的 `PROVIDERS` 注册表追加条目：`id` / `name` / `env` / `key_url` / `models`，并为模型实现 handler（返回图片 bytes 或 URL）。
2. 在本表追加一行：来源、取 Key 位置、环境变量、端点、验证日期。
3. 在 `references/regressions.md` 记一笔「新增提供方」验证记录。

通用约定：

- 密钥只读环境变量，禁止硬编码或入库
- 输出图片保存到用户指定路径，默认当前目录
- 生图是计费操作：先用 `--dry-run` 确认路由，再真正调用
