# Boundary & Dependency Anchor（边界与依赖）

问题：触发边界是否干净？依赖是否健康？

## Positive
Trigger 覆盖真实 Intent Space，anti-trigger 明确排除相邻技能；依赖显式、可替换、无循环。

## Negative
与邻居 Trigger 大量同义重复、无 anti-trigger、存在隐藏依赖；删除依赖后核心定义无法成立。

## Borderline
少量 Trigger 词与邻居重叠，但 Decision 与 Output 不同 → 不算重复，属 COMPLEMENTARY 或 ALTERNATIVE。

## 判定规则
- dependency_healthy = YES：依赖显式、可替换、无循环依赖、无隐藏依赖。
- Structural Coupling：失去某 Skill 后自身核心定义无法成立 → dependency_healthy = NO。
- Trigger 好坏不按数量判断，只判断覆盖、重复、错误触发区域与 anti-trigger。
