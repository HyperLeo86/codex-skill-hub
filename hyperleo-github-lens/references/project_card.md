# 项目卡模板 v0.2（hyperleo-github-lens 输出格式）

## 头部

```markdown
id: YYYY-MM-DD-owner-repo
url: https://github.com/owner/repo
分析日期: YYYY-MM-DD
目的标签: 学习 / 采用 / 选型 / 对标
卡片版本: v0.2
```

## 1. L1 确定性信号与红旗

| 信号 | 值 | 来源 |
|---|---|---|
| stars / forks / watchers | | GitHub API |
| license / archived | | GitHub API |
| last push / created | | GitHub API |
| open issues / language / topics | | GitHub API |
| OpenSSF Scorecard | unavailable 则标「待验证」 | scorecard.dev |
| deps.dev dependents | | deps.dev |
| Star/Fork、Star/Issue、Fork 率 | | 由 repo_meta.sh 计算 |
| 最近提交日期 | | GitHub API |

红旗清单 + 判定（过 / 条件过 / 不过）。

## 2. 价值判断（Why）

- 一句话定位 / 受众与场景 / 为什么是现在 / 采用信号与社区真实度（≥1 第三方）/ 商业模式（可选）/ 风险预判

## 3. 机制拆解（How）

- 技术栈 / 目录职责 / 入口·核心模块·数据流 / 设计取舍（Why > What）/ 可借鉴模式 / 深读覆盖率（Quick/Standard/Deep）

## 4. 评分（锚点校准 + 目的权重）

### L1 客观维度

| 客观维度 | 基础分 | L1 证据 |
|---|---|---|
| 近期增长与活跃 | | |
| 维护与社区（客观部分） | | |

### L2 语义维度（相对锚点）

| 维度 | 得分 | 相对锚点解释 | 锚点 |
|---|---|---|---|
| 价值与定位 | | | |
| 技术趋势 | | | |
| 产品完成度 | | | |
| 架构与代码质量 | | | |
| 学习价值 | | | |
| 采用/商用价值（语义） | | | |

权重表：目的标签（学习/采用/选型/对标）
加权总分：____；风险扣分：-____；一票否决：无 / 命中（____）

```
Verdict: <学它|用它|对标它|放弃|观察> — <项目名> — <核心证据>
置信度: HIGH|MEDIUM|LOW
```

## 5. 同类对比（Compare）

| 项目 | 定位 | 架构/技术路线 | License | 活跃 | 上手 | 适用场景 | 学习点 | 来源（历史/新增） |
|---|---|---|---|---|---|---|---|---|
| 本仓库 | | | | | | | | |
| 同类 A | | | | | | | | |

一句话定位差异：

## 6. 版本 diff（重复分析时必填；首次标「首次，无 diff」）

- L1 信号变化：
- 锚点选择变化：
- 加权总分变化：
- 对比集变化：
- Verdict 是否翻转：

## 7. 再评估与归档

- 再评估触发器（时间或版本事件）：
- 归档位置：
