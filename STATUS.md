# STATUS — resale-category-mapper-cli

## What was built

A local-first Python CLI for eBay/Amazon resellers to map items to categories,
save category picks, and export CSV. All data stays on the user's machine as
local JSON files. No network access, no API keys, no secrets.

### Components

| File | Purpose |
|------|---------|
| `src/resale_category_mapper/__init__.py` | Package init, version |
| `src/resale_category_mapper/models.py` | Data models: Item, Category, CategoryPick |
| `src/resale_category_mapper/rules.py` | Keyword-based category rules engine (~60 rules) |
| `src/resale_category_mapper/storage.py` | Local JSON file storage (picks + items) |
| `src/resale_category_mapper/mapper.py` | Mapping orchestration (rules, picks, fallback, dry-run) |
| `src/resale_category_mapper/export.py` | CSV import/export |
| `src/resale_category_mapper/cli.py` | argparse CLI (map, save, list, rules, export, import) |
| `tests/test_rules.py` | Tests for category rules matching |
| `tests/test_storage.py` | Tests for local JSON storage |
| `tests/test_mapper.py` | Tests for mapper orchestration |
| `tests/test_cli.py` | Tests for CLI commands via subprocess |
| `LICENSE` | MIT License (Copyright (c) 2026 Asdale Dynamics, LLC) |
| `README.md` | Documentation with usage examples |
| `pyproject.toml` | Packaging config |

### CLI commands

- `resale-map map <input.csv> [-o output.csv] [--apply] [--dry-run]` — map items from CSV to categories
- `resale-map save <item_id> <category_path>` — save a manual category pick
- `resale-map list [--all]` — list saved category picks
- `resale-map rules [--search <term>]` — list category rules
- `resale-map export -o <output.csv>` — export saved items to CSV
- `resale-map import <input.csv>` — import items from CSV to storage

Global options: `--data-dir`, `--dry-run`, `-v/--verbose`

## How to run it

```bash
# From the project directory
PYTHONPATH=src python3 -m resale_category_mapper.cli --help

# Or install
pip install -e .
resale-map --help

# Example workflow
echo 'id,title,platform,price,notes
1,Apple iPhone 13,ebay,550,Good condition
2,Nike running shoes,amazon,85,Size 10' > items.csv

resale-map map items.csv --dry-run
resale-map map items.csv -o mapped.csv --apply
resale-map save ITEM123 "Electronics > Phones > Smartphones"
resale-map list
resale-map export -o all_items.csv
```

## Verification results

- **Tests**: 33/33 passed (test_rules, test_storage, test_mapper, test_cli)
- **CLI smoke test**: `resale-map rules` displays category table correctly
- **CSV map/export**: verified end-to-end via test_map_csv and test_export
- **Dry-run mode**: verified no writes occur (test_dry_run_does_not_persist, test_save_pick_dry_run_does_not_persist)
- **Storage persistence**: verified data persists across Storage instances (test_pick_persists_across_instances)

## Known gaps

- No `.github/workflows` files (intentionally omitted per requirements)
- No separate lint/typecheck configuration beyond pyproject.toml classifiers
- Category rules are keyword-based only; no ML or fuzzy matching
- No undo/rollback for saved picks (use `delete_pick` via storage API)
- Default data dir is `~/.resale-category-mapper`; no environment variable override
- Price range filtering on rules is supported but not exposed via CLI flags
- No Windows/Mac-specific packaging beyond the universal Python wheel

## Credits

Built by **Asdale Dynamics, LLC** (Indiana, formed Oct 2026). MIT License.
Copyright (c) 2026 Asdale Dynamics, LLC.
