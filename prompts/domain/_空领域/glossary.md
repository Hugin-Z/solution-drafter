# 领域插件 / _空领域（默认空领域 / 占位）

本文件是 solution-drafter L3 领域插件层的空占位实现。

## 用法

`templates/<doc_type>/outline.yaml` 的 `generation.domain_plugin` 字段指向本文件时，section prompt 在 生成阶段不引入领域术语 / 行业话术 / 合规字典。

所有文档类型默认绑定本文件。接入真实领域时，新建 `prompts/domain/<vendor>/` 多文件（`company-profile.md` 含 own_* 字段 + `glossary.md` / `client-logic.md` / `compliance.md`），在 run.py 内拼接为 `domain_plugin` 字面注入（不改 outline.yaml）。详见 `SKILL.md` 的"自定义领域插件 howto"。

## 当前内容

空 / 无术语注入。绑定本文件时，依赖公司主体字段（own_*）的 sales 类 section（如"公司实力"）输出整段【待补充】，不虚构。
