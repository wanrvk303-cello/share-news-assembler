import pytest
from app.ingestion import compute_dedupe_key, _clean_html


def test_dedupe_key_consistency():
    key1 = compute_dedupe_key("Test Title", "https://example.com")
    key2 = compute_dedupe_key("Test Title", "https://example.com")
    assert key1 == key2


def test_dedupe_key_different():
    key1 = compute_dedupe_key("Title A", "https://a.com")
    key2 = compute_dedupe_key("Title B", "https://b.com")
    assert key1 != key2


def test_clean_html():
    assert _clean_html("<p>Hello <b>world</b></p>") == "Hello world"


def test_clean_html_empty():
    assert _clean_html("") == ""


def test_clean_html_no_tags():
    assert _clean_html("No tags here") == "No tags here"


def test_clean_html_nested():
    assert _clean_html("<div><span>Text</span></div>") == "Text"
