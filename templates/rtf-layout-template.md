# RTF Layout Guidance: {{REPORT_ID}}

## Page setup
- Orientation: Landscape (if > 8 columns) / Portrait
- Header: report title, run date `<?xdoxslt:sysdate('DD-MON-YYYY HH24:MI')?>`, parameter echo
- Footer: page `<?xdofo:page-number?>` of `<?xdofo:total-page-number?>`

## Parameter echo (header)
| Label | Field |
|---|---|
| … | `<?$p_x?>` |

## Grouping
- Outer group: `<?for-each-group:G_1;./GROUP_COL?>` … `<?end for-each-group?>`
- Detail rows: `<?for-each:current-group()?>` … `<?end for-each?>`
- Sort: `<?sort:SORT_COL;'ascending';data-type='text'?>`

## Columns
| # | Header | XML element | Width | Align | Format mask |
|---|---|---|---|---|---|
| 1 | | | | Left | text |

Format masks:
- Dates: `<?format-date:ELEMENT;'DD-MON-YYYY'?>`. BIP data needs canonical dates; the data model returns DATE types.
- Numbers: `<?format-number:ELEMENT;'#,##0.00'?>`
- Currency: format the number and show the currency code in its own column.

## Excel output
- Avoid merged cells in the detail table.
- One header row; no blank spacer rows inside the table.
- Keep text-like IDs (e.g. project numbers with leading zeros) as text.

## No-data message
`<?if:count(.//ROW_ELEMENT)=0?>No data found for the selected parameters.<?end if?>`
