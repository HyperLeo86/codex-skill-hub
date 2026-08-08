# Behavior Anchor（行为）

问题：文档写得好，实际是不是也好用？

## Positive
Golden / Boundary / Regression 案例全部通过，且 Regression 以机器可执行文件（tests/regressions/*.json 或 *.yaml）存在。

## Negative
文档声称会做但实际不做（Declared vs Actual 偏离），或 Regression 未通过。

## Borderline
行为测试部分自动化、部分依赖人工；此时行为证据 coverage 有限，不得把「看起来能用」当作通过。

## 判定规则
- behavior_failure = YES：存在可复现的行为失败、回归未通过或声明-行为漂移。
- 行为测试能自动化的部分必须由脚本执行；开放式质量判断由 Judge 完成但必须留证据。
- Regression 失败应沉淀为：Failure → Root Cause → Fix → Regression Case。
