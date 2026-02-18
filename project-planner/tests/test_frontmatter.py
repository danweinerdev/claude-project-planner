"""Tests for the YAML frontmatter parser."""

from dashboard.frontmatter import parse_frontmatter, _parse_scalar


class TestParseScalar:
    def test_true_values(self):
        assert _parse_scalar("true") is True
        assert _parse_scalar("yes") is True
        assert _parse_scalar("True") is True

    def test_false_values(self):
        assert _parse_scalar("false") is False
        assert _parse_scalar("no") is False

    def test_null_values(self):
        assert _parse_scalar("null") is None
        assert _parse_scalar("~") is None
        assert _parse_scalar("") is None

    def test_integers(self):
        assert _parse_scalar("42") == 42
        assert _parse_scalar("0") == 0
        assert _parse_scalar("-1") == -1

    def test_floats(self):
        assert _parse_scalar("3.14") == 3.14
        assert _parse_scalar("0.5") == 0.5

    def test_strings(self):
        assert _parse_scalar("hello") == "hello"
        assert _parse_scalar("some-value") == "some-value"

    def test_quoted_strings(self):
        assert _parse_scalar('"hello world"') == "hello world"
        assert _parse_scalar("'single'") == "single"


class TestParseFrontmatter:
    def test_no_frontmatter(self):
        meta, body = parse_frontmatter("Just some text\nNo frontmatter here.")
        assert meta == {}
        assert "Just some text" in body

    def test_empty_frontmatter(self):
        text = "---\n---\nBody text"
        meta, body = parse_frontmatter(text)
        assert meta == {}
        assert body == "Body text"

    def test_simple_scalars(self):
        text = """\
---
title: My Title
status: active
count: 5
enabled: true
---

Body here.
"""
        meta, body = parse_frontmatter(text)
        assert meta["title"] == "My Title"
        assert meta["status"] == "active"
        assert meta["count"] == 5
        assert meta["enabled"] is True
        assert body == "Body here."

    def test_inline_list(self):
        text = """\
---
tags: [alpha, beta, gamma]
---

Content.
"""
        meta, body = parse_frontmatter(text)
        assert meta["tags"] == ["alpha", "beta", "gamma"]

    def test_empty_inline_list(self):
        text = """\
---
tags: []
---

Content.
"""
        meta, body = parse_frontmatter(text)
        assert meta["tags"] == []

    def test_block_list(self):
        text = """\
---
items:
  - first
  - second
  - third
---

Content.
"""
        meta, body = parse_frontmatter(text)
        assert meta["items"] == ["first", "second", "third"]

    def test_nested_objects(self):
        text = """\
---
phases:
  - id: 1
    title: Setup
    status: complete
  - id: 2
    title: Build
    status: planned
---

Content.
"""
        meta, body = parse_frontmatter(text)
        assert len(meta["phases"]) == 2
        assert meta["phases"][0]["id"] == 1
        assert meta["phases"][0]["title"] == "Setup"
        assert meta["phases"][0]["status"] == "complete"
        assert meta["phases"][1]["id"] == 2
        assert meta["phases"][1]["title"] == "Build"

    def test_nested_objects_with_inline_list(self):
        text = """\
---
tasks:
  - id: "1.1"
    title: Do thing
    depends_on: [a, b]
---

Content.
"""
        meta, body = parse_frontmatter(text)
        assert meta["tasks"][0]["depends_on"] == ["a", "b"]

    def test_quoted_values(self):
        text = """\
---
title: "Hello: World"
---

Body.
"""
        meta, body = parse_frontmatter(text)
        assert meta["title"] == "Hello: World"

    def test_comments_ignored(self):
        text = """\
---
# This is a comment
title: Test
# Another comment
status: draft
---

Body.
"""
        meta, body = parse_frontmatter(text)
        assert meta["title"] == "Test"
        assert meta["status"] == "draft"

    def test_no_closing_delimiter(self):
        text = "---\ntitle: Test\nNo closing delimiter"
        meta, body = parse_frontmatter(text)
        assert meta == {}
        assert "No closing delimiter" in body

    def test_body_preserved(self):
        text = """\
---
title: Test
---

# Heading

Paragraph with **bold** and *italic*.

- List item 1
- List item 2
"""
        meta, body = parse_frontmatter(text)
        assert meta["title"] == "Test"
        assert "# Heading" in body
        assert "**bold**" in body
        assert "- List item 1" in body
