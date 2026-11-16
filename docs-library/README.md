# docs-library/: your configuration documents (local RAG)

Put your organization's configuration and design documents here. The agent searches them, with citations, whenever a report touches something **environment-specific**:

- DFF / EFF definitions: context, segment, `ATTRIBUTEn` column, value set, global or context-specific
- Value sets and lookups (codes ↔ meanings)
- Custom project roles, statuses, classifications, expenditure types/categories
- Business unit / ledger / chart-of-accounts segment setup
- Existing report specs, data dictionaries, integration designs

> 🔒 **Everything in this folder except `README.md` and `samples/` is gitignored.** Your configuration documents never leave your machine through this repo.

## Use your organization's shared docs location

You don't have to copy files here. Point the agent at any folder, for example a OneDrive or SharePoint folder synced to your PC, or a network share:

```bash
# one-off
python scripts/docs_index.py --dir "D:/Shared/ERP Config Docs" ingest

# or for every command (PowerShell: $env:BIP_DOCS_DIR = "D:/Shared/ERP Config Docs")
export BIP_DOCS_DIR="D:/Shared/ERP Config Docs"
```

The index is written to `<that folder>/.index/index.json`.

## Commands

| What | Command | In Claude Code |
|---|---|---|
| Build / refresh the index | `python scripts/docs_index.py ingest` | `/ingest-docs [folder]` |
| What changed since the last ingest | `python scripts/docs_index.py status` | |
| Ask a question | `python scripts/docs_index.py search "task billing code flexfield" -k 5` | `/ask-docs <question>` |
| List DFF column mappings | `python scripts/docs_index.py dff --filter task` | |

Supported formats: `.docx`, `.pdf`, `.xlsx`/`.xlsm` (every sheet), `.csv`, `.md`, `.txt`.

## Tips for documents that index well

- **Tables beat prose.** A DFF table with columns *Context | Segment | Prompt | Table Column | Value Set | Global* is ideal. Each row becomes a searchable, citable record.
- **Name the base object** (e.g. "PJF_TASKS_V", "Project Task DFF") near the table, ideally in its heading.
- **Re-run `ingest`** whenever documents change. `status` tells you when it's needed.
- The agent **cites** every fact it takes from here (`file > section`). If two documents disagree, it raises an open question instead of choosing.

## samples/

`samples/` holds fictional examples, used by the tests and the worked example:
- `sample-ppm-dff-configuration.md`: project task DFF, project roles, statuses
- `sample-value-set-billing-codes.csv`: a value set export
