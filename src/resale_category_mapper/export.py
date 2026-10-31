"""CSV export for mapped items."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from .models import Item
from .mapper import MappingResult


EXPORT_FIELDNAMES = [
    "item_id",
    "title",
    "platform",
    "price",
    "category_id",
    "category_path",
    "confidence",
    "source",
    "notes",
]


def export_to_csv(results: list[MappingResult], output_path: Path | str) -> int:
    """Export mapping results to CSV. Returns number of rows written."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    for r in results:
        rows.append({
            "item_id": r.item.id,
            "title": r.item.title,
            "platform": r.item.platform,
            "price": r.item.price if r.item.price is not None else "",
            "category_id": r.final_category_id,
            "category_path": r.final_category_path,
            "confidence": round(r.confidence, 3),
            "source": r.source,
            "notes": r.item.notes,
        })

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=EXPORT_FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    return len(rows)


def export_items_to_csv(items: list[Item], output_path: Path | str) -> int:
    """Export items directly to CSV (without mapping results)."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    for item in items:
        rows.append({
            "item_id": item.id,
            "title": item.title,
            "platform": item.platform,
            "price": item.price if item.price is not None else "",
            "category_id": item.category_id,
            "category_path": item.category_path,
            "confidence": "",
            "source": item.status,
            "notes": item.notes,
        })

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=EXPORT_FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    return len(rows)


def import_items_from_csv(input_path: Path | str) -> list[Item]:
    """Import items from a CSV file. Expected columns: id, title, platform, price, notes."""
    input_path = Path(input_path)
    items: list[Item] = []

    with input_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            item_id = row.get("id") or row.get("item_id") or ""
            if not item_id:
                continue
            price_str = row.get("price", "").strip()
            price = float(price_str) if price_str else None
            item = Item(
                id=item_id,
                title=row.get("title", ""),
                platform=row.get("platform", ""),
                price=price,
                notes=row.get("notes", ""),
            )
            items.append(item)

    return items