# Identity Anchor（身份）

问题：它到底是什么？是否只有一个清晰 Job？

## Positive
一个 Skill：搜索 GitHub 项目 → 排序 → 输出候选项目。搜索、排序、输出全部服务「发现项目」，所以是一个 Job。

## Negative
一个 Skill：搜索 GitHub + 修改代码 + 发布 GitHub Release。三个步骤各有独立输入、输出与价值，是多个 Job。

## Borderline
搜索 GitHub + 生成结构化比较表。若比较表只是搜索任务的标准交付物，仍是一个 Job；若比较表本身是独立可复用能力，则为两个 Job。

## 判定规则
- identity_clear = YES：One Job 可一句话陈述，且 description / trigger / workflow / output 指向同一 Job。
- identity_clear = NO：存在可识别的第二 Job 或身份漂移。
- 无法从证据判断 → UNKNOWN。
