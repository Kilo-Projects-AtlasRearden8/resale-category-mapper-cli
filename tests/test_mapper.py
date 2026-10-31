"""Tests for mapper orchestration."""

import tempfile

import pytest

from resale_category_mapper.models import CategoryPick, Item
from resale_category_mapper.mapper import Mapper
from resale_category_mapper.rules import get_default_rules
from resale_category_mapper.storage import Storage


@pytest.fixture
def temp_storage():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Storage(tmpdir)


def test_map_item_uses_rule(temp_storage):
    mapper = Mapper(storage=temp_storage, dry_run=True)
    item = Item(id="1", title="Apple iPhone 13", platform="ebay", price=600.0)
    result = mapper.map_item(item)
    assert result.source == "rule"
    assert result.rule is not None
    assert "Phone" in result.final_category_path or "Phones" in result.final_category_path


def test_map_item_uses_pick_over_rule(temp_storage):
    temp_storage.set_pick(CategoryPick(
        item_id="1",
        category_id="custom-pick",
        category_path="Custom > Category",
        confidence=1.0,
        source="manual",
    ))
    mapper = Mapper(storage=temp_storage, dry_run=True)
    item = Item(id="1", title="Apple iPhone 13")
    result = mapper.map_item(item)
    assert result.source == "pick"
    assert result.final_category_path == "Custom > Category"


def test_map_item_fallback(temp_storage):
    mapper = Mapper(storage=temp_storage, dry_run=True)
    item = Item(id="1", title="xyzzy random thing unknown")
    result = mapper.map_item(item)
    assert result.source == "fallback"
    assert result.final_category_id == "uncategorized"


def test_map_items_multiple(temp_storage):
    mapper = Mapper(storage=temp_storage, dry_run=True)
    items = [
        Item(id="1", title="iPhone 13", platform="ebay"),
        Item(id="2", title="Nike running shoes", platform="amazon"),
        Item(id="3", title="Harry Potter novel", platform="ebay"),
    ]
    results = mapper.map_items(items)
    assert len(results) == 3
    assert all(r.item.id in ("1", "2", "3") for r in results)


def test_dry_run_does_not_persist(temp_storage):
    mapper = Mapper(storage=temp_storage, dry_run=True)
    item = Item(id="1", title="iPhone 13", platform="ebay")
    result = mapper.map_item(item)
    mapper.apply_results([result])
    assert temp_storage.get_pick("1") is None


def test_apply_persists_when_not_dry_run(temp_storage):
    mapper = Mapper(storage=temp_storage, dry_run=False)
    item = Item(id="1", title="iPhone 13", platform="ebay", price=600.0)
    result = mapper.map_item(item)
    mapper.apply_results([result])
    pick = temp_storage.get_pick("1")
    assert pick is not None


def test_save_pick_creates_manual_pick(temp_storage):
    mapper = Mapper(storage=temp_storage, dry_run=False)
    pick = mapper.save_pick("item-1", "custom-id", "Custom > Path", note="test note")
    assert pick.item_id == "item-1"
    assert pick.category_path == "Custom > Path"
    assert pick.source == "manual"
    assert temp_storage.get_pick("item-1") is not None


def test_save_pick_dry_run_does_not_persist(temp_storage):
    mapper = Mapper(storage=temp_storage, dry_run=True)
    mapper.save_pick("item-1", "custom-id", "Custom > Path")
    assert temp_storage.get_pick("item-1") is None
