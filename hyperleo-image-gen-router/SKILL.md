---
name: hyperleo-image-gen-router
description: >-
  统一路由并调用用户已开通的生图 API（阿里通义万相 DashScope、火山方舟 ARK），按可用 Key 与任务类型自动选择模型，未来新增提供方只需扩展注册表。当用户说「帮我生成一张图片」「用我的生图 API 画一张」「帮我生图/做图/出图」「我的生图能力有哪些，怎么调用」「哪个生图模型适合这个需求」「新增一个生图提供方或 API」「用通义万相/火山方舟/Seedream 画图」时使用；不用于视频生成、音频/TTS、技术示意图（用 scientific-schematics）、科学数据图表。
---

# Image Gen Router

**版本**：2.0（2026-08-07）

## 定位

统一入口调用用户已开通的生图能力，自动选择可用提供方与模型；用户只需给一句图片需求。能力来源、配对环境变量与取 Key 位置见 [references/providers.md](references/providers.md)。

## 触发与反触发

- 触发：帮我生成一张图片；用我的生图 API 画一张；帮我生图/做图/出图；我的生图能力有哪些，怎么调用；哪个生图模型适合这个需求；新增一个生图提供方或 API；用通义万相/火山方舟/Seedream 画图
- 反触发：视频生成、音频/TTS、技术示意图（用 scientific-schematics）、科学数据图表

## 决定权（自由度 medium）

- 按脚本与路由表执行；prompt 措辞、输出文件名允许合理调整
- 用户显式指定 provider/model 时以用户为准，不做隐式替换

## 快速开始

```bash
# 自动路由生成（默认：qwen-image-2.0-pro）
python3 scripts/imagegen.py "书架上的橘猫，扁平卡通风"

# 显式指定提供方 / 模型
python3 scripts/imagegen.py "黄昏下的山景，写实摄影" --provider ark
python3 scripts/imagegen.py "卡通小狗" --model z-image-turbo -o dog.png

# 只看可用能力（不调用任何计费接口）
python3 scripts/imagegen.py --list

# 只看路由结果，不真正出图
python3 scripts/imagegen.py "照片级人像" --dry-run
```

输出：图片绝对路径 + 实际 provider/model + 路由理由。

## 路由决策

1. 显式 `--provider` / `--model` 优先。
2. 过滤出已配置 Key 的提供方；全部缺失 → 打印取 Key 指引并退出。
3. 任务类型命中规则（按顺序）：
   - 快 / 便宜 / 草稿 → `z-image-turbo`
   - 写实 / 照片 / 摄影 → `doubao-seedream-5-0-pro-260628`（ARK），无 ARK 则 `qwen-image-2.0-pro`
   - 卡通 / 插画 / 扁平 / 动漫 → `qwen-image-2.0-pro`
   - 高清 / 专业 / 高质量 → `wan2.7-image-pro` 或 `doubao-seedream-5-0-pro-260628`
   - 默认 → `qwen-image-2.0-pro`
4. 调用失败时自动降级到下一个可用提供方（显式指定时不降级）。

## 提供方来源（取 Key 位置）

| 提供方 | 控制台 | 环境变量 |
| --- | --- | --- |
| 阿里通义万相（DashScope） | https://bailian.console.aliyun.com → API-KEY 管理 | `DASHSCOPE_API_KEY` |
| 火山方舟（ARK） | https://console.volcengine.com/ark → API Key 管理 | `ARK_API_KEY`（备用 `ARK_API_KEY_ID`） |

详细端点、已验证模型、新增提供方模板见 [references/providers.md](references/providers.md)。

## 工作流

1. 解析需求：主题、风格、比例、用途；需要时补充 prompt 细节（主体/风格/构图/避免项）。
2. 运行 `scripts/imagegen.py` 自动路由；可用 `--dry-run` 先看选择。
3. 查看输出图片：构图、文字、比例是否符合要求；不合格则改 prompt 重跑或换模型。
4. 把结果绝对路径交给用户；说明实际使用的 provider/model。
5. 新增/变更提供方后，更新 `references/providers.md` 并在 `references/regressions.md` 记账。

## 验收

- 未显式指定 provider/model 时，脚本按「可用 Key × 任务类型」自动路由并输出原因
- 至少一个提供方可用时成功产出图片文件，返回绝对路径
- `--list` 只打印已注册提供方与模型，不发起计费请求
- 全部提供方缺 Key 时，逐项给出控制台取 Key 路径，不崩溃

## 失败降级

- 所有 API Key 缺失 → 打印控制台路径与所需环境变量，停止
- 首选提供方调用失败（401/配额/模型不可用）→ 自动降级到下一个可用提供方并记录原因
- 模型返回无图片或异步任务失败 → 明确报错与重试建议，不静默成功
- 新增提供方 → 按 providers.md 模板追加 handler，路由逻辑不变

## 资源

- `scripts/imagegen.py`：路由 + 调用 + 下载，只依赖 Python 标准库
- `references/providers.md`：提供方/模型/端点/取 Key 位置/新增模板
- `references/regressions.md`：回归账本

## Token 预算（契约：220 行 / 2000 token）
