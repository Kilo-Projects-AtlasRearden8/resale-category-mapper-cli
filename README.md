# Resale Category Mapper CLI

A local-first Python CLI for eBay/Amazon resellers to map items to categories,
save category picks, and export CSV. Built by **Asdale Dynamics, LLC** — no
network access, no API keys, no secrets. All data stays on your machine as
local JSON files.

## What it does

- **Map** items from a CSV to eBay/Amazon-style categories using keyword rules
- **Save** manual category picks for items (overrides automatic rules)
- **Export** mapped items to CSV for listing or relisting
- **Dry-run mode** to preview changes without writing anything
- **Local JSON storage** — your data never leaves your computer

## Who this is for

This tool is for eBay and Amazon resellers who want a simple, private way to
categorize inventory without signing up for another cloud service. It's part of
Asdale Dynamics, LLC's focus on practical, beginner-friendly tools for small
business owners, authors, and resellers.

## Install

```bash
# Clone or download this repository, then:
pip install -e .
```

This installs the `resale-map` command on your PATH.

## Quick start

```bash
# Create a sample items.csv
cat > items.csv << 'EOF'
id,title,platform,price,notes
1,Apple iPhone 13,ebay,550,Good condition
2,Nike running shoes,amazon,85,Size 10
3,Harry Potter paperback,ebay,12,Fiction
EOF

# Map items and preview (dry-run)
resale-map map items.csv --dry-run

# Map and save results to CSV
resale-map map items.csv -o mapped.csv

# Save a manual pick
resale-map save ITEM123 "Electronics > Phones > Smartphones"

# List saved picks
resale-map list

# Export all saved items to CSV
resale-map export -o all_items.csv
```

## Commands

| Command | Purpose |
|---------|---------|
| `map` | Map items from CSV to categories |
| `save` | Save a manual category pick |
| `list` | List saved category picks |
| `rules` | List available category rules |
| `export` | Export saved items to CSV |
| `import` | Import items from CSV to storage |

## Options

| Option | Description |
|--------|-------------|
| `--data-dir DIR` | Custom directory for JSON storage (default: `~/.resale-category-mapper`) |
| `--dry-run` | Preview changes without writing to storage |
| `-v, --verbose` | Verbose output |

## Data storage

All data is stored locally as JSON in `~/.resale-category-mapper/` (or your
custom `--data-dir`):

- `picks.json` — saved category picks
- `items.json` — imported items and their categories

No cloud, no accounts, no API keys.

## Category rules

The mapper uses keyword-based rules to suggest categories. Rules match keywords
in item titles (case-insensitive). You can view all rules with:

```bash
resale-map rules
```

Manual picks always take priority over automatic rules.

## Tests

```bash
pip install pytest
pytest
```

## License

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC.

## Credit

Built by **Asdale Dynamics, LLC** (Indiana, formed Oct 2026) — beginner-friendly
AI education, books, and practical tools for small business owners, authors, and
resellers. Hub: dylanasdale.github.io
