"""Mapper orchestration: match items to categories, apply picks, dry-run support."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .models import CategoryPick, Item
from .rules import CategoryRule, find_best_match, get_default_rules
from .storage import Storage


@dataclass
class MappingResult:
    """Result of mapping an item to a category."""
    item: Item
    rule: CategoryRule | None
    confidence: float
    pick: CategoryPick | None
    final_category_id: str
    final_category_path: str
    source: str  # "pick", "rule", "fallback"

    def to_dict(self) -> dict[str, Any]:
        return {
            "item_id": self.item.id,
            "title": self.item.title,
            "platform": self.item.platform,
            "price": self.item.price,
            "category_id": self.final_category_id,
            "category_path": self.final_category_path,
            "confidence": round(self.confidence, 3),
            "source": self.source,
        }


class Mapper:
    """Orchestrates category mapping with rules, picks, and dry-run."""

    def __init__(
        self,
        storage: Storage | None = None,
        rules: list[CategoryRule] | None = None,
        dry_run: bool = False,
    ):
        self.storage = storage or Storage()
        self.rules = rules or get_default_rules()
        self.dry_run = dry_run

    def map_item(self, item: Item) -> MappingResult:
        """Map a single item to a category."""
        # 1. Check for saved pick (highest priority)
        pick = self.storage.get_pick(item.id)
        if pick:
            return MappingResult(
                item=item,
                rule=None,
                confidence=1.0,
                pick=pick,
                final_category_id=pick.category_id,
                final_category_path=pick.category_path,
                source="pick",
            )

        # 2. Match against rules
        rule, confidence = find_best_match(self.rules, item.title, item.platform, item.price)
        if rule:
            return MappingResult(
                item=item,
                rule=rule,
                confidence=confidence,
                pick=None,
                final_category_id=rule.category_id,
                final_category_path=rule.category_path,
                source="rule",
            )

        # 3. Fallback
        return MappingResult(
            item=item,
            rule=None,
            confidence=0.0,
            pick=None,
            final_category_id="uncategorized",
            final_category_path="Uncategorized",
            source="fallback",
        )

    def map_items(self, items: list[Item]) -> list[MappingResult]:
        """Map multiple items."""
        return [self.map_item(item) for item in items]

    def save_pick(self, item_id: str, category_id: str, category_path: str, note: str = "") -> CategoryPick:
        """Save a manual category pick for an item."""
        pick = CategoryPick(
            item_id=item_id,
            category_id=category_id,
            category_path=category_path,
            confidence=1.0,
            source="manual",
            note=note,
        )
        if not self.dry_run:
            self.storage.set_pick(pick)
        return pick

    def apply_results(self, results: list[MappingResult]) -> None:
        """Apply mapping results to items and persist if not dry-run."""
        if self.dry_run:
            return

        for result in results:
            if result.source == "rule" and result.confidence > 0.5:
                # Auto-save high-confidence rule matches
                pick = CategoryPick(
                    item_id=result.item.id,
                    category_id=result.final_category_id,
                    category_path=result.final_category_path,
                    confidence=result.confidence,
                    source="auto",
                )
                self.storage.set_pick(pick)

            # Update item with final category
            item = result.item
            item.category_id = result.final_category_id
            item.category_path = result.final_category_path
            item.status = "mapped" if result.source != "fallback" else "unmapped"
            self.storage.set_item(item)