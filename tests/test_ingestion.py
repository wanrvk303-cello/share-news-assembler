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


def test_dedupe_key_special_chars():
    key = compute_dedupe_key("Title with special chars: @#$%", "https://example.com?q=1&b=2")
    assert isinstance(key, str)
    assert len(key) == 64


def test_clean_html_links():
    assert _clean_html('<a href="https://example.com">Link</a>') == "Link"


def test_clean_html_images():
    assert _clean_html('<img src="test.jpg" alt="Image">') == ""


def test_clean_html_multiple_spaces():
    assert _clean_html("Hello    world") == "Hello world"


def test_clean_html_newlines():
    assert _clean_html("Hello\n\nworld") == "Hello world"


def test_dedupe_key_unicode():
    key = compute_dedupe_key("日本語タイトル", "https://example.com")
    assert isinstance(key, str)
    assert len(key) == 64
