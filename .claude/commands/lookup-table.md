---
description: Look up an Oracle Fusion table/view on Oracle Docs (source of truth) and cache it
argument-hint: <OBJECT_NAME> [COLUMN ...] [release e.g. 25D]
---

Look up on Oracle Docs: **$ARGUMENTS**

Delegate to the `oracle-docs-researcher` sub-agent with the object name, any columns listed and the release (from the arguments, else `FUSION_RELEASE` in `private/environment.md`, else latest).

Show me the verdict table with URLs, plus useful neighbors (`_VL` views, base tables, FKs/join paths). Then tell me whether `knowledge/tables/<module>.md` should be updated. If a VERIFY item there is now confirmed, propose the edit.
