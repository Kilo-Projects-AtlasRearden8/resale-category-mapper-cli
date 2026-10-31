"""Test fixtures and helpers for resale_category_mapper tests."""

from pathlib import Path
import json

from resale_category_mapper.models import Item
from resale_category_mapper.rules import CategoryRule, get_default_rules
from resale_category_mapper.storage import Storage


def make_item(item_id: str, title: str = "", platform: str = "", price=None, notes: str = "") -> Item:
    return Item(id=item_id, title=title, platform=platform, price=price, notes=notes)


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))
