# Purity Anchor（职责纯粹性）

问题：这个 Skill 的职责边界是否干净？

## Positive
Workflow 每一步都服务于 One Job，输出不含其他领域承诺，没有「顺带做」的步骤。

## Negative
审计类 Skill 在检索时顺带生成营销报告；或输出里混入「顺便教你用法」的承诺。

## Borderline
一个步骤同时服务两个 Job，但该步骤本身可参数化拆分；此时 single_primary_job 应判 NO。

## 判定规则
- single_primary_job = YES：只存在一个主要 Job。
- multiple_independent_jobs = YES：存在 ≥2 个可独立存在的 Job。
- 判断必须基于 Workflow 步骤与输出结构，不依据 Token 数或 Trigger 数量。
