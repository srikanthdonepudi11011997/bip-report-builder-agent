---
description: Index your configuration documents (DFFs, value sets, lookups, setup) for RAG
argument-hint: [folder]  (default: $BIP_DOCS_DIR or docs-library/)
---

Index the configuration-docs library: **$ARGUMENTS**

1. If a folder was given, run `python scripts/docs_index.py --dir "<folder>" ingest`; otherwise run `python scripts/docs_index.py ingest`.
2. Report the files and chunks indexed, plus any files that were skipped and why.
3. Run `python scripts/docs_index.py dff` (with the same `--dir`) and summarize the DFF mappings found as *object/flexfield → context → segment → ATTRIBUTEn*. Flag context-dependent columns (the same ATTRIBUTEn under several contexts).
4. Compare them with `private/environment.md`. Propose token values that are missing or different, each with its citation. **Don't edit `private/environment.md` without my OK.**

If Python isn't available, tell me what to install (`pip install -r requirements.txt`).
