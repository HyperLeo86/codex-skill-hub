# 状态机、队列与恢复

## 状态迁移

| 状态 | 进入条件 | 负责方 | 出口 |
| --- | --- | --- | --- |
| QUEUED | 拓扑排序完成 | 御前会议 | PRECHECK |
| PRECHECK | 轮到该任务 | 御前会议 | WORKING / HUMAN_GATE / FAILED |
| WORKING | worker 启动 | Worker | REVIEW / HUMAN_GATE |
| REVIEW | 交接通过 | Reviewer×2 | FIXING / VERIFYING / HUMAN_GATE |
| FIXING | 审查有应修项 | 原 Worker | REVIEW |
| VERIFYING | 审查通过 | 御前会议 | PUBLISHING / FIXING / HUMAN_GATE |
| PUBLISHING | 验证通过 | 御前会议 | CLOSING / HUMAN_GATE |
| CLOSING | 已发布 | 御前会议 | DONE / HUMAN_GATE |
| DONE | 外部事实源确认 | 御前会议 | 队列下一项 |
| HUMAN_GATE | 任一人工门 | 用户+御前会议 | 恢复原状态 |
| FAILED / BLOCKED | 协议失败/状态不安全 | 御前会议 | HUMAN_GATE |

人工门恢复后回到暂停前状态继续；FAILED 不自动重试。

## 队列文件

位置：`<workdir>/.small-council/queue.json`；由御前会议唯一写入，worker/reviewer 只读。

```json
{
  "run_id": "2026-08-07-a",
  "tasks": [
    {
      "id": "t2",
      "deps": ["t1"],
      "state": "REVIEW",
      "base": "abc123",
      "final": "",
      "review_round": 1,
      "blockers": [],
      "decisions": [],
      "evidence": ["handoff.md", "review-spec.md", "review-standards.md", "verify.log"]
    }
  ]
}
```

## 恢复规则（中断/重启）

| 外部事实 | 动作 |
| --- | --- |
| 已交付且外部确认 | DONE，跳过 |
| 已发布未收尾 | 从 CLOSING 收尾 |
| 本地产出未发布 | 从 REVIEW/VERIFYING 恢复 |
| 存在未提交修改 | fresh recovery worker 接手，或 HUMAN_GATE |
| 状态文件丢失 | 用外部事实源重建队列，只补缺失步骤 |

不假设旧 worker 可恢复；恢复执行体一律 fresh。

## 并发规则

- 每个活跃任务一个隔离工作区（git worktree 或独立目录），一个工作区永远只有一个写入者。
- 独立任务并行，默认 2，上限 = 可用写入槽位 − 审查保留槽位；依赖任务严格串行。
- 隔离不可用时降级严格串行；发布动作始终由御前会议串行执行。
