"""Tests for CLI command behavior using subprocess invocation."""

import subprocess
import sys
import tempfile
from pathlib import Path


def run_cli(*args, dry_run=False, data_dir=None):
    """Run the resale-map CLI via subprocess and return CompletedProcess."""
    cmd = [sys.executable, "-m", "resale_category_mapper.cli"]
    if dry_run:
        cmd.append("--dry-run")
    if data_dir:
        cmd.extend(["--data-dir", str(data_dir)])
    cmd.extend(args)
    return subprocess.run(cmd, capture_output=True, text=True)


def test_rules_command():
    result = run_cli("rules")
    assert result.returncode == 0
    assert "Electronics" in result.stdout
    assert "Total rules:" in result.stdout


def test_rules_search_filter():
    result = run_cli("rules", "--search", "iphone")
    assert result.returncode == 0


def test_save_command(tmp_path):
    result = run_cli(
        "save", "ITEM123", "Electronics > Phones > Smartphones",
        data_dir=tmp_path,
    )
    assert result.returncode == 0
    assert "Saved pick" in result.stdout


def test_save_dry_run(tmp_path):
    result = run_cli(
        "--dry-run", "save", "ITEM123", "Electronics > Phones",
        data_dir=tmp_path,
    )
    assert result.returncode == 0
    assert "DRY RUN" in result.stdout


def test_map_command_missing_file():
    result = run_cli("map", "/nonexistent/path.csv")
    assert result.returncode != 0


def test_map_csv(tmp_path):
    # Create input CSV
    input_csv = tmp_path / "items.csv"
    input_csv.write_text(
        "id,title,platform,price,notes\n"
        "1,Apple iPhone 13,ebay,550,Good condition\n"
        "2,Nike running shoes,amazon,85,Size 10\n"
        "3,Harry Potter paperback,ebay,12,Fiction\n"
    )
    output_csv = tmp_path / "mapped.csv"
    result = run_cli(
        "map", str(input_csv), "-o", str(output_csv), "--apply",
        data_dir=tmp_path,
    )
    assert result.returncode == 0
    assert output_csv.exists()
    content = output_csv.read_text()
    assert "iPhone" in content
    assert "Electronics" in content


def test_list_no_picks(tmp_path):
    result = run_cli("list", data_dir=tmp_path)
    assert result.returncode == 0


def test_export(tmp_path):
    # First import an item (export works on items, not picks)
    input_csv = tmp_path / "import.csv"
    input_csv.write_text("id,title,platform,price,notes\n1,Test Item,ebay,10,test\n")
    run_cli("import", str(input_csv), data_dir=tmp_path)
    output_csv = tmp_path / "export.csv"
    result = run_cli("export", "-o", str(output_csv), data_dir=tmp_path)
    assert result.returncode == 0
    assert output_csv.exists()


def test_import(tmp_path):
    input_csv = tmp_path / "import.csv"
    input_csv.write_text(
        "id,title,platform,price,notes\n"
        "1,Test Item,ebay,10,test\n"
    )
    result = run_cli("import", str(input_csv), data_dir=tmp_path)
    assert result.returncode == 0
    assert "Imported" in result.stdout
