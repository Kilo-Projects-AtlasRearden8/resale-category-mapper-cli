"""Command-line interface for resale-category-mapper."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from .models import CategoryPick, Item
from .rules import CategoryRule, get_default_rules
from .storage import Storage
from .mapper import Mapper, MappingResult
from .export import export_to_csv, export_items_to_csv, import_items_from_csv


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="resale-map",
        description="Local-first CLI for eBay/Amazon resellers to map items to categories, save picks, and export CSV.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Map items from CSV and export results
  resale-map map items.csv -o mapped.csv

  # Dry-run to preview mappings without saving
  resale-map map items.csv --dry-run

  # Save a manual category pick
  resale-map save ITEM123 "Electronics > Phones > Smartphones"

  # List all saved picks
  resale-map list

  # Show category rules
  resale-map rules

  # Export all saved items to CSV
  resale-map export -o all_items.csv

Data is stored locally in ~/.resale-category-mapper/ (JSON files).
No network access, no API keys required.
""",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="Data directory for JSON storage (default: ~/.resale-category-mapper)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing to storage",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # map command
    map_parser = subparsers.add_parser("map", help="Map items from CSV to categories")
    map_parser.add_argument("input", type=Path, help="Input CSV file with items")
    map_parser.add_argument("-o", "--output", type=Path, help="Output CSV file for results")
    map_parser.add_argument("--apply", action="store_true", help="Save high-confidence mappings to storage")

    # save command
    save_parser = subparsers.add_parser("save", help="Save a manual category pick for an item")
    save_parser.add_argument("item_id", help="Item ID")
    save_parser.add_argument("category_path", help="Full category path (e.g., 'Electronics > Phones > Smartphones')")
    save_parser.add_argument("--category-id", help="Category ID (optional, derived from path if omitted)")
    save_parser.add_argument("--note", default="", help="Optional note for this pick")

    # list command
    list_parser = subparsers.add_parser("list", help="List saved category picks")
    list_parser.add_argument("--all", action="store_true", help="Show all items including unmapped")

    # rules command
    rules_parser = subparsers.add_parser("rules", help="List category rules")
    rules_parser.add_argument("--search", help="Filter rules by keyword in path or keywords")

    # export command
    export_parser = subparsers.add_parser("export", help="Export saved items to CSV")
    export_parser.add_argument("-o", "--output", type=Path, required=True, help="Output CSV file")
    export_parser.add_argument("--mapped-only", action="store_true", help="Only export mapped items")

    # import command
    import_parser = subparsers.add_parser("import", help="Import items from CSV to storage")
    import_parser.add_argument("input", type=Path, help="Input CSV file")

    return parser


def format_table(headers: list[str], rows: list[list[str]], max_col_width: int = 50) -> str:
    """Format a simple text table."""
    if not rows:
        return "(no data)"

    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], min(len(cell), max_col_width))

    # Truncate cells
    def truncate(cell: str, width: int) -> str:
        return cell if len(cell) <= width else cell[:width - 1] + "…"

    # Header
    header_line = " | ".join(h.ljust(w) for h, w in zip(headers, col_widths))
    sep_line = "-+-".join("-" * w for w in col_widths)

    # Rows
    row_lines = []
    for row in rows:
        row_lines.append(" | ".join(truncate(cell, w).ljust(w) for cell, w in zip(row, col_widths)))

    return "\n".join([header_line, sep_line, *row_lines])


def cmd_map(args: argparse.Namespace, storage: Storage, dry_run: bool, verbose: bool) -> int:
    """Map items from CSV to categories."""
    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        return 1

    items = import_items_from_csv(args.input)
    if not items:
        print("No items found in input file", file=sys.stderr)
        return 1

    if verbose:
        print(f"Loaded {len(items)} items from {args.input}")

    mapper = Mapper(storage=storage, dry_run=dry_run)
    results = mapper.map_items(items)

    # Print results table
    headers = ["Item ID", "Title", "Platform", "Category", "Confidence", "Source"]
    rows = []
    for r in results:
        title = r.item.title[:40] + "…" if len(r.item.title) > 40 else r.item.title
        rows.append([
            r.item.id,
            title,
            r.item.platform or "-",
            r.final_category_path,
            f"{r.confidence:.2f}",
            r.source,
        ])

    print(format_table(headers, rows))

    # Export if output specified
    if args.output:
        count = export_to_csv(results, args.output)
        if verbose:
            print(f"Exported {count} rows to {args.output}")

    # Apply mappings if --apply and not dry-run
    if args.apply and not dry_run:
        mapper.apply_results(results)
        if verbose:
            print("Applied mappings to storage")

    return 0


def cmd_save(args: argparse.Namespace, storage: Storage, dry_run: bool, verbose: bool) -> int:
    """Save a manual category pick."""
    # Derive category_id from path if not provided
    category_id = args.category_id
    if not category_id:
        category_id = args.category_path.lower().replace(" > ", "-").replace(" ", "-")

    pick = CategoryPick(
        item_id=args.item_id,
        category_id=category_id,
        category_path=args.category_path,
        confidence=1.0,
        source="manual",
        note=args.note,
    )

    if dry_run:
        print(f"[DRY RUN] Would save pick: {pick.item_id} -> {pick.category_path}")
    else:
        storage.set_pick(pick)
        print(f"Saved pick: {args.item_id} -> {args.category_path}")

    return 0


def cmd_list(args: argparse.Namespace, storage: Storage, dry_run: bool, verbose: bool) -> int:
    """List saved category picks."""
    picks = storage.load_picks()
    items = storage.load_items()

    if not picks and not args.all:
        print("No saved picks. Use 'resale-map save' to add picks.")
        return 0

    headers = ["Item ID", "Title", "Category", "Source", "Confidence"]
    rows = []

    # Show picks first
    for pick in picks.values():
        item = items.get(pick.item_id)
        title = item.title[:40] + "…" if item and len(item.title) > 40 else (item.title if item else "-")
        rows.append([
            pick.item_id,
            title,
            pick.category_path,
            pick.source,
            f"{pick.confidence:.2f}",
        ])

    # Show unmapped items if --all
    if args.all:
        for item in items.values():
            if item.id not in picks:
                title = item.title[:40] + "…" if len(item.title) > 40 else item.title
                rows.append([item.id, title, "-", "unmapped", "0.00"])

    print(format_table(headers, rows))
    return 0


def cmd_rules(args: argparse.Namespace, storage: Storage, dry_run: bool, verbose: bool) -> int:
    """List category rules."""
    rules = get_default_rules()

    if args.search:
        search = args.search.lower()
        rules = [
            r for r in rules
            if search in r.category_path.lower()
            or any(search in kw.lower() for kw in r.keywords)
        ]

    headers = ["Category ID", "Category Path", "Keywords", "Platforms", "Confidence"]
    rows = []
    for rule in rules:
        keywords = ", ".join(rule.keywords[:3])
        if len(rule.keywords) > 3:
            keywords += f" (+{len(rule.keywords) - 3} more)"
        rows.append([
            rule.category_id,
            rule.category_path,
            keywords,
            ", ".join(rule.platforms),
            f"{rule.confidence:.2f}",
        ])

    print(format_table(headers, rows))
    print(f"\nTotal rules: {len(rules)}")
    return 0


def cmd_export(args: argparse.Namespace, storage: Storage, dry_run: bool, verbose: bool) -> int:
    """Export saved items to CSV."""
    items = storage.load_items()

    if args.mapped_only:
        items = [i for i in items if i.category_id]

    if not items:
        print("No items to export")
        return 0

    count = export_items_to_csv(list(items.values()), args.output)
    print(f"Exported {count} items to {args.output}")
    return 0


def cmd_import(args: argparse.Namespace, storage: Storage, dry_run: bool, verbose: bool) -> int:
    """Import items from CSV to storage."""
    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        return 1

    items = import_items_from_csv(args.input)
    if not items:
        print("No items found in input file")
        return 1

    if dry_run:
        print(f"[DRY RUN] Would import {len(items)} items")
        for item in items[:5]:
            print(f"  {item.id}: {item.title[:50]}")
        if len(items) > 5:
            print(f"  ... and {len(items) - 5} more")
    else:
        for item in items:
            storage.set_item(item)
        print(f"Imported {len(items)} items to storage")

    return 0


def main(argv: list[str] | None = None) -> int:
    parser = create_parser()
    args = parser.parse_args(argv)

    storage = Storage(args.data_dir)
    dry_run = args.dry_run
    verbose = args.verbose

    if dry_run and verbose:
        print("[DRY RUN MODE] No changes will be persisted")

    commands = {
        "map": cmd_map,
        "save": cmd_save,
        "list": cmd_list,
        "rules": cmd_rules,
        "export": cmd_export,
        "import": cmd_import,
    }

    cmd_func = commands.get(args.command)
    if not cmd_func:
        parser.print_help()
        return 1

    return cmd_func(args, storage, dry_run, verbose)


if __name__ == "__main__":
    sys.exit(main())