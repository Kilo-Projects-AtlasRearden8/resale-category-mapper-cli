"""Local JSON storage for category picks and items."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .models import CategoryPick, Item


DEFAULT_DATA_DIR = Path.home() / ".resale-category-mapper"
DEFAULT_PICKS_FILE = DEFAULT_DATA_DIR / "picks.json"
DEFAULT_ITEMS_FILE = DEFAULT_DATA_DIR / "items.json"


class Storage:
    """Local JSON file storage for picks and items."""

    def __init__(self, data_dir: Path | str | None = None):
        self.data_dir = Path(data_dir) if data_dir else DEFAULT_DATA_DIR
        self.picks_file = self.data_dir / "picks.json"
        self.items_file = self.data_dir / "items.json"
        self._ensure_dir()

    def _ensure_dir(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _read_json(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        with path.open("r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}

    def _write_json(self, path: Path, data: dict[str, Any]) -> None:
        tmp_path = path.with_suffix(".tmp")
        with tmp_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        tmp_path.replace(path)

    # Picks methods
    def load_picks(self) -> dict[str, CategoryPick]:
        data = self._read_json(self.picks_file)
        return {k: CategoryPick.from_dict(v) for k, v in data.items()}

    def save_picks(self, picks: dict[str, CategoryPick]) -> None:
        data = {k: v.to_dict() for k, v in picks.items()}
        self._write_json(self.picks_file, data)

    def get_pick(self, item_id: str) -> CategoryPick | None:
        picks = self.load_picks()
        return picks.get(item_id)

    def set_pick(self, pick: CategoryPick) -> None:
        picks = self.load_picks()
        picks[pick.item_id] = pick
        self.save_picks(picks)

    def delete_pick(self, item_id: str) -> bool:
        picks = self.load_picks()
        if item_id in picks:
            del picks[item_id]
            self.save_picks(picks)
            return True
        return False

    # Items methods
    def load_items(self) -> dict[str, Item]:
        data = self._read_json(self.items_file)
        return {k: Item.from_dict(v) for k, v in data.items()}

    def save_items(self, items: dict[str, Item]) -> None:
        data = {k: v.to_dict() for k, v in items.items()}
        self._write_json(self.items_file, data)

    def get_item(self, item_id: str) -> Item | None:
        items = self.load_items()
        return items.get(item_id)

    def set_item(self, item: Item) -> None:
        items = self.load_items()
        items[item.id] = item
        self.save_items(items)

    def list_items(self) -> list[Item]:
        return list(self.load_items().values())

    def clear_all(self) -> None:
        """Clear all stored data (for testing)."""
        if self.picks_file.exists():
            self.picks_file.unlink()
        if self.items_file.exists():
            self.items_file.unlink()