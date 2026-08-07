# 证据契约

## 交接格式（worker 返回，禁止只给散文）

```text
changed: [路径...]
commands: [{cmd, exit_code, output_path}]
acceptance_map: [{criterion, evidence, pass|fail}]
unfinished: []
risks: []
pending_questions: []
```

御前会议用事实源（git status/diff、远端状态、命令输出）逐项核对；不一致 → HUMAN_GATE。

## 证据类型

| 类型 | 例子 | 可替代 |
| --- | --- | --- |
| diff | git diff base...head | 否 |
| 命令输出 | 测试/类型检查日志 + 退出码 | 否 |
| 远端状态 | 推送后 SHA、Issue/PR 状态 | 否 |
| 产物 | 构建物/报告路径 | 仅辅助 |

## 验收映射

- 每个验收标准必须在 acceptance_map 中有对应行：criterion + evidence + pass/fail。
- 「完成」= 全部验收行 pass + 至少 3 类证据存在 + 外部事实源一致。
- 无法生成证据时标「待验证」，禁止声称完成；reviewer 的「完成」不是证据。

## 证据纪律

- 只记录真实运行输出；禁止编造命令结果、SHA 或状态。
- 证据路径写入队列记录，随状态文件持久化。
- 发布前御前会议亲自运行最终验证并检查输出，不委托给 worker 自报。
