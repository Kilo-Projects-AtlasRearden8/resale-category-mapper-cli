"""Tests for category rules matching logic."""

import pytest

from resale_category_mapper.rules import (
    CategoryRule,
    find_best_match,
    get_default_rules,
)


def test_default_rules_load():
    rules = get_default_rules()
    assert len(rules) > 0
    assert any("electronics" in r.category_id for r in rules)
    assert any("clothing" in r.category_id for r in rules)
    assert any("books" in r.category_id for r in rules)


def test_rule_matches_keyword():
    rule = CategoryRule(
        category_id="test-category",
        category_path="Test > Category",
        keywords=["iphone", "galaxy", "smartphone"],
        confidence=0.9,
    )
    assert rule.matches("Apple iPhone 13") == 0.9
    assert rule.matches("Samsung Galaxy S21") == 0.9
    assert rule.matches("Generic smartphone") == 0.9


def test_rule_case_insensitive():
    rule = CategoryRule(
        category_id="test-category",
        category_path="Test > Category",
        keywords=["iphone"],
        confidence=0.9,
    )
    assert rule.matches("IPHONE 13") == 0.9
    assert rule.matches("iPhone") == 0.9


def test_rule_no_match():
    rule = CategoryRule(
        category_id="test-category",
        category_path="Test > Category",
        keywords=["iphone"],
        confidence=0.9,
    )
    assert rule.matches("Nike running shoes") == 0.0
    assert rule.matches("") == 0.0


def test_rule_platform_filter():
    rule = CategoryRule(
        category_id="test-category",
        category_path="Test > Category",
        keywords=["iphone"],
        platforms=["ebay"],
        confidence=0.9,
    )
    assert rule.matches("iPhone 13", platform="ebay") == 0.9
    assert rule.matches("iPhone 13", platform="amazon") == 0.0
    assert rule.matches("iPhone 13", platform="") == 0.9


def test_rule_price_range():
    rule = CategoryRule(
        category_id="test-category",
        category_path="Test > Category",
        keywords=["laptop"],
        min_price=500.0,
        max_price=2000.0,
        confidence=0.9,
    )
    assert rule.matches("Gaming Laptop", price=1000.0) == 0.9
    assert rule.matches("Laptop", price=300.0) == 0.0  # below min
    assert rule.matches("Laptop", price=3000.0) == 0.0  # above max


def test_find_best_match_returns_highest_confidence():
    rules = [
        CategoryRule("a", "A Path", ["phone"], confidence=0.5),
        CategoryRule("b", "B Path", ["iphone"], confidence=0.95),
    ]
    rule, conf = find_best_match(rules, "Apple iPhone 13")
    assert rule is not None
    assert rule.category_id == "b"
    assert conf == 0.95


def test_find_best_match_no_match():
    rules = [
        CategoryRule("a", "A Path", ["iphone"], confidence=0.9),
    ]
    rule, conf = find_best_match(rules, "Nike running shoes")
    assert rule is None
    assert conf == 0.0


def test_default_rules_cover_common_items():
    rules = get_default_rules()
    # Electronics
    rule, conf = find_best_match(rules, "Apple iPhone 14")
    assert rule is not None and conf > 0
    # Clothing
    rule, conf = find_best_match(rules, "Nike running shoes")
    assert rule is not None and conf > 0
    # Books
    rule, conf = find_best_match(rules, "Harry Potter paperback novel")
    assert rule is not None and conf > 0


def test_rule_from_dict_roundtrip():
    rule = CategoryRule(
        category_id="x",
        category_path="X > Y",
        keywords=["a", "b"],
        platforms=["amazon"],
        min_price=10.0,
        max_price=100.0,
        confidence=0.5,
    )
    data = rule.to_dict()
    restored = CategoryRule.from_dict(data)
    assert restored == rule
    assert restored.keywords == ["a", "b"]
    assert restored.platforms == ["amazon"]
    assert restored.min_price == 10.0
