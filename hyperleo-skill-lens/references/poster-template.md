# 海报模板与渲染规范（v0.2）

## 铁律

- 输出是「一张说明图片」，禁止 Mermaid、SVG、流程图、架构图、结构图
- 默认画布 1200×1600（3:4），交付单文件 PNG + 可复现的 HTML 源
- 正文必须由 HTML/CSS 渲染（文字清晰），AI 生图只允许做背景/装饰插画，不允许承载正文文字

## 渲染命令

```bash
scripts/render_poster.sh <poster.html> <out.png> 1200 1600
```

本机 Chrome 路径：`/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`

## 海报版式（自上而下）

1. 顶栏：来源标签（GitHub / 本地 / 名称）+ 生成日期
2. 标题区：skill 名称 + 一句话定位（大字，≤25 字）
3. 比喻卡：像什么 + 哪像 + 哪不像（三行，配一个 emoji 或插画）
4. 要点区：3–5 张要点卡（好处 / 适用场景 / 注意事项各 1，其余按需）
5. 模块标签：可替换（绿）/ 难替换（黄）/ 不可替换（红）chips
6. 脚注：证据来源 + 目标 skill 版本 + lens 版本

## 样式基线

- 白底卡片 + 主色 `#2F5BE7` 或温和暖色；中文用 `system-ui / PingFang SC`
- 字号层级：标题 64px / 定位 34px / 要点 26px / 脚注 18px
- 禁止把正文排成表格；要点用短句，每点 ≤20 字

## 可选 AI 插画

- 通过 hyperleo-image-gen-router 生成比喻插画（如「医生听诊」「地图望远镜」风格），嵌入背景层或装饰角
- 生成失败不阻塞；正文文字永远用 HTML/CSS

## 证据规则

- 海报内每个判断标来源（如 [SKILL.md 工作流]）
- 未实证内容标「待验证」，禁止编造
