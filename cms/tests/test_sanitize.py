"""
Tests for the sanitize_html helper function.
"""

from django.test import SimpleTestCase

from cms.models import sanitize_html


class SanitizeHtmlTests(SimpleTestCase):
    """Tests for sanitize_html."""

    def test_allows_basic_formatting(self):
        html = "<p>Hello <strong>world</strong></p>"
        self.assertEqual(sanitize_html(html), html)

    def test_allows_links_with_attributes(self):
        html = '<a href="https://example.com" title="Ex">link</a>'
        self.assertEqual(sanitize_html(html), html)

    def test_strips_script_tags(self):
        html = '<p>Hello</p><script>alert("xss")</script>'
        result = sanitize_html(html)
        self.assertNotIn("<script>", result)
        self.assertIn("<p>Hello</p>", result)

    def test_strips_onclick_attribute(self):
        html = '<p onclick="alert(1)">text</p>'
        result = sanitize_html(html)
        self.assertNotIn("onclick", result)
        self.assertIn("<p>", result)

    def test_strips_style_tags(self):
        html = "<style>body{display:none}</style><p>Hi</p>"
        result = sanitize_html(html)
        self.assertNotIn("<style>", result)
        self.assertIn("<p>Hi</p>", result)

    def test_strips_iframe(self):
        html = '<iframe src="https://evil.com"></iframe>'
        result = sanitize_html(html)
        self.assertNotIn("<iframe", result)

    def test_allows_table_markup(self):
        html = (
            "<table><thead><tr><th>H</th></tr></thead>"
            "<tbody><tr><td>D</td></tr></tbody></table>"
        )
        self.assertEqual(sanitize_html(html), html)

    def test_allows_lists(self):
        html = "<ul><li>one</li><li>two</li></ul>"
        self.assertEqual(sanitize_html(html), html)

    def test_allows_headings(self):
        for tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            html = f"<{tag}>Title</{tag}>"
            self.assertEqual(sanitize_html(html), html)

    def test_empty_string(self):
        self.assertEqual(sanitize_html(""), "")

    def test_none(self):
        self.assertIsNone(sanitize_html(None))

    def test_allows_img_tag_with_safe_attributes(self):
        html = '<img src="https://example.com/x.png" alt="test" width="100" height="50">'
        result = sanitize_html(html)
        self.assertIn("<img", result)
        self.assertIn('src="https://example.com/x.png"', result)

    def test_strips_img_onerror_attribute(self):
        html = '<img src="x.png" onerror="alert(1)">'
        result = sanitize_html(html)
        self.assertNotIn("onerror", result)

    def test_strips_disallowed_attributes_on_allowed_tags(self):
        html = '<p style="color:red" class="foo">text</p>'
        result = sanitize_html(html)
        self.assertNotIn("style", result)
        self.assertNotIn("class", result)

    def test_allows_span_class(self):
        html = '<span class="highlight">text</span>'
        self.assertEqual(sanitize_html(html), html)

    def test_strips_javascript_href(self):
        html = '<a href="javascript:alert(1)">click</a>'
        result = sanitize_html(html)
        self.assertNotIn("javascript:", result)
