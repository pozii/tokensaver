"""Tests for summarize_file tool."""
import tempfile
from pathlib import Path

from tokensaver.tools.summarizer import summarize_file


def test_summarize_text_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write("This is a test document. It contains important information about AI. Machine learning is great.")
        path = f.name

    result = summarize_file(path, max_tokens=200)
    assert result["type"] == "file"
    assert result["files_processed"] == 1
    assert len(result["summary"]) > 0


def test_summarize_directory():
    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "readme.md").write_text("# Project\nThis is the main readme.", encoding="utf-8")
        (Path(tmpdir) / "main.py").write_text("def main(): pass", encoding="utf-8")
        (Path(tmpdir) / "image.png").write_bytes(b"\x89PNG\r\n")

        result = summarize_file(tmpdir, max_tokens=500, mode="structure")
        assert result["type"] == "directory"
        assert result["files_processed"] >= 2
        assert "readme.md" in result["summary"] or "main.py" in result["summary"]


def test_nonexistent_path():
    result = summarize_file("/nonexistent/path/xyz")
    assert result["type"] == "error"


def test_file_extension_filter():
    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "file.py").write_text("print('hello')", encoding="utf-8")
        (Path(tmpdir) / "file.js").write_text("console.log('hi')", encoding="utf-8")

        result = summarize_file(tmpdir, file_extensions=[".py"], mode="structure")
        assert result["type"] == "directory"


def test_token_budget_respected():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(" ".join(["word"] * 5000))
        path = f.name

    result = summarize_file(path, max_tokens=100)
    assert result["token_count"] <= 110  # small tolerance
