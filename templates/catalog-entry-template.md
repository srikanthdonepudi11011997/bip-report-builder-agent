# Metadata Catalog Entry (Alation-style): {{REPORT_ID}}

> Paste these fields into your data catalog (Alation, Collibra, or a wiki). The YAML block below can be loaded by a script.

```yaml
name: "{{REPORT_ID}} {{TITLE}}"
type: "BI Publisher Report"
system: "Oracle Fusion Cloud: {{MODULE}}"
catalog_path: "/Shared Folders/Custom/{{MODULE}}/{{REPORT_ID}}/{{REPORT_ID}}_RPT.xdo"
description: >
  {{PURPOSE}}
business_owner: "<role, not a person's name>"
technical_owner: "<team>"
refresh: "On demand"
output_formats: [Excel, PDF]
grain: "One row per {{GRAIN}}"
parameters:
  - label: ""
    bind: ""
    type: ""
    multi_select: false
    required: false
columns:
  - name: ""
    description: ""
source_tables: []
tags: [bip, oracle-fusion, "{{MODULE}}"]
data_classification: "Internal"   # raise if personal data is present
known_limitations: []
related_documents: [FSD, TSD]
```

## Description (rich text)
**What it answers:** …
**Who uses it:** …
**How to run:** Reports and Analytics → Browse Catalog → Shared Folders → Custom → {{MODULE}} → {{REPORT_ID}}.
**Caveats:** …
