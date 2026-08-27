# Visual Assets

All artifacts render natively in GitHub Flavored Markdown — no images, no dependencies.

## Mermaid Diagrams (render in GitHub, VS Code, any GFM viewer)

| File | Description |
|---|---|
| [`architecture.mmd`](architecture.mmd) | SENSE → THINK → HANDOFF → LEARN flow |
| [`calibration.mmd`](calibration.mmd) | Signal calibration by source (pie chart) |
| [`tools.mmd`](tools.mmd) | 55 tools across 4 groups |

## Text Artifacts (always render, even in terminals)

| File | Description |
|---|---|
| [`monday_problem.txt`](monday_problem.txt) | The before/after Monday illustration |
| [`sample_brief.txt`](sample_brief.txt) | Full campaign brief in ASCII box format |
| [`calibration_table.txt`](calibration_table.txt) | Brier scores with interpretation |
| [`comparison_table.txt`](comparison_table.txt) | Before/after time and decision comparison |

## Embed in README

Mermaid: copy `.mmd` content into a ````mermaid``` fenced code block.
Text: copy `.txt` content into a ```` ``` ```` fenced code block.

## Regenerate
```bash
python3 docs/assets/generate_assets.py
```
