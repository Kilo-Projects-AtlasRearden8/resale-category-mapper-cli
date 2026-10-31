"""Tests for local JSON storage."""

import os
import tempfile

import pytest

from resale_category_mapper.models import CategoryPick, Item
from resale_category_mapper.storage import Storage


@pytest.fixture
def temp_storage():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Storage(tmpdir)


def test_save_and_load_pick(temp_storage):
    pick = CategoryPick(
        item_id="item-1",
        category_id="electronics-phones",
        category_path="Electronics > Phones",
        confidence=0.9,
        source="manual",
    )
    temp_storage.set_pick(pick)
    loaded = temp_storage.get_pick("item-1")
    assert loaded is not None
    assert loaded.item_id == "item-1"
    assert loaded.category_path == "Electronics > Phones"
    assert loaded.confidence == 0.9


def test_delete_pick(temp_storage):
    pick = CategoryPick(
        item_id="item-1",
        category_id="electronics-phones",
        category_path="Electronics > Phones",
        confidence=0.9,
        source="manual",
    )
    temp_storage.set_pick(pick)
    assert temp_storage.delete_pick("item-1") is True
    assert temp_storage.get_pick("item-1") is None
    assert temp_storage.delete_pick("nonexistent") is False


def test_save_and_load_item(temp_storage):
    item = Item(
        id="item-1",
        title="iPhone 13",
        platform="ebay",
        price=500.0,
        notes="Good condition",
    )
    temp_storage.set_item(item)
    loaded = temp_storage.get_item("item-1")
    assert loaded is not None
    assert loaded.title == "iPhone 13"
    assert loaded.price == 500.0


def test_list_items(temp_storage):
    temp_storage.set_item(Item(id="a", title="A", platform="ebay"))
    temp_storage.set_item(Item(id="b", title="B", platform="amazon"))
    items = temp_storage.list_items()
    assert len(items) == 2


def test_clear_all(temp_storage):
    temp_storage.set_pick(CategoryPick(
        item_id="x", category_id="c", category_path="C",
    ))
    temp_storage.set_item(Item(id="y", title="Y"))
    temp_storage.clear_all()
    assert temp_storage.get_pick("x") is None
    assert temp_storage.get_item("y") is None


def test_pick_persists_across_instances(tmp_path):
    storage_dir = tmp_path / "data"
    s1 = Storage(storage_dir)
    s1.set_pick(CategoryPick(
        item_id="item-1",
        category_id="electronics-phones",
        category_path="Electronics > Phones",
    ))
    s2 = Storage(storage_dir)
    loaded = s2.get_pick("item-1")
    assert loaded is not None
    assert loaded.category_path == "Electronics > Phones"
