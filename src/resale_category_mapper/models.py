"""Data models for items, category picks, and the category tree."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class Category:
    """A node in the category tree."""

    id: str
    name: str
    path: str
    children: list["Category"] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "path": self.path,
            "children": [c.to_dict() for c in self.children],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Category":
        return cls(
            id=data["id"],
            name=data["name"],
            path=data["path"],
            children=[cls.from_dict(c) for c in data.get("children", [])],
        )


@dataclass
class Item:
    """A resale item to be categorized."""

    id: str
    title: str
    platform: str = ""
    price: float | None = None
    notes: str = ""
    category_id: str = ""
    category_path: str = ""
    status: str = "unmapped"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Item":
        return cls(
            id=str(data.get("id", "")),
            title=str(data.get("title", "")),
            platform=str(data.get("platform", "")),
            price=data.get("price"),
            notes=str(data.get("notes", "")),
            category_id=str(data.get("category_id", "")),
            category_path=str(data.get("category_path", "")),
            status=str(data.get("status", "unmapped")),
        )


@dataclass
class CategoryPick:
    """A saved category selection for an item."""

    item_id: str
    category_id: str
    category_path: str
    confidence: float = 0.0
    source: str = "manual"
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CategoryPick":
        return cls(
            item_id=str(data.get("item_id", "")),
            category_id=str(data.get("category_id", "")),
            category_path=str(data.get("category_path", "")),
            confidence=float(data.get("confidence", 0.0)),
            source=str(data.get("source", "manual")),
            note=str(data.get("note", "")),
        )


def flatten_categories(root: Category) -> list[Category]:
    """Return every leaf and internal node in the tree, breadth-first."""
    out: list[Category] = []
    stack: list[Category] = [root]
    while stack:
        node = stack.pop(0)
        out.append(node)
        stack.extend(node.children)
    return out


def find_category(root: Category, category_id: str) -> Category | None:
    """Find a category node by id in the tree."""
    for node in flatten_categories(root):
        if node.id == category_id:
            return node
    return None