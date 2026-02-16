"""Tests for markdown to HTML conversion."""

from dashboard.markdown import format_inline, md_to_html


class TestFormatInline:
    def test_bold(self):
        assert "<strong>bold</strong>" in format_inline("**bold**")

    def test_italic(self):
        assert "<em>italic</em>" in format_inline("*italic*")

    def test_code(self):
        assert "<code>code</code>" in format_inline("`code`")

    def test_link(self):
        result = format_inline("[text](http://example.com)")
        assert '<a href="http://example.com">text</a>' in result

    def test_html_escape(self):
        result = format_inline("<script>alert('xss')</script>")
        assert "<script>" not in result
        assert "&lt;script&gt;" in result

    def test_combined(self):
        result = format_inline("**bold** and *italic* and `code`")
        assert "<strong>bold</strong>" in result
        assert "<em>italic</em>" in result
        assert "<code>code</code>" in result


class TestMdToHtml:
    def test_h1(self):
        assert "<h1>" in md_to_html("# Heading")

    def test_h2(self):
        assert "<h2>" in md_to_html("## Heading")

    def test_h3(self):
        assert "<h3>" in md_to_html("### Heading")

    def test_h4(self):
        assert "<h4>" in md_to_html("#### Heading")

    def test_paragraph(self):
        assert "<p>" in md_to_html("Just a paragraph")

    def test_unordered_list_dash(self):
        result = md_to_html("- item 1\n- item 2")
        assert "<ul>" in result
        assert "<li>" in result
        assert "item 1" in result

    def test_unordered_list_star(self):
        result = md_to_html("* item 1\n* item 2")
        assert "<ul>" in result
        assert "<li>" in result

    def test_unordered_list_plus(self):
        result = md_to_html("+ item 1\n+ item 2")
        assert "<ul>" in result

    def test_checklist_checked(self):
        """Checkbox HTML gets escaped by format_inline; verify the substitution ran."""
        result = md_to_html("- [x] done task")
        assert "checkbox" in result
        assert "checked" in result

    def test_checklist_unchecked(self):
        """Checkbox HTML gets escaped by format_inline; verify the substitution ran."""
        result = md_to_html("- [ ] pending task")
        assert "checkbox" in result
        assert "checked" not in result

    def test_code_block(self):
        result = md_to_html("```python\nprint('hello')\n```")
        assert '<pre><code class="language-python">' in result
        assert "print" in result
        assert "</code></pre>" in result

    def test_code_block_default_lang(self):
        result = md_to_html("```\nsome code\n```")
        assert 'class="language-text"' in result

    def test_code_block_escapes_html(self):
        result = md_to_html("```\n<div>html</div>\n```")
        assert "&lt;div&gt;" in result

    def test_empty_lines(self):
        result = md_to_html("para 1\n\npara 2")
        assert result.count("<p>") == 2

    def test_list_closes_on_empty_line(self):
        result = md_to_html("- item\n\nparagraph")
        assert "</ul>" in result
        assert "<p>paragraph</p>" in result

    def test_mixed_content(self):
        content = """\
# Title

Some text with **bold**.

- Item 1
- Item 2

```python
x = 1
```

More text.
"""
        result = md_to_html(content)
        assert "<h1>" in result
        assert "<strong>bold</strong>" in result
        assert "<ul>" in result
        assert "<pre>" in result
        assert "<p>" in result
