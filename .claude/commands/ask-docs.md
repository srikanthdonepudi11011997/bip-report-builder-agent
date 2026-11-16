---
description: Ask a question against your configuration documents (cited answers)
argument-hint: <question>
---

Answer from the configuration documents: **$ARGUMENTS**

Delegate to the `config-docs-researcher` sub-agent. Give me the answer with **file > section** citations and the confidence (CONFIG_DOC / INFERRED / NOT FOUND). If it's NOT FOUND, suggest the discovery query I could run in DEV instead. If the question is about a standard table or column rather than our setup, also ask the `oracle-docs-researcher`.
