from django.test import TestCase

from planet.templatetags.planet_tags import clean_html


class CleanHtmlFilterTest(TestCase):
    def test_empty_string_returns_empty(self):
        self.assertEqual(clean_html(""), "")

    def test_strips_script_tags(self):
        html = '<div><p>Hello</p><script>alert("xss")</script></div>'
        result = clean_html(html)
        self.assertNotIn("<script", result)

    def test_strips_style_tags(self):
        html = "<div><p>Hello</p><style>.evil { color: red }</style></div>"
        result = clean_html(html)
        self.assertNotIn("<style", result)

    def test_preserves_text_content(self):
        html = "<div><p>This is a paragraph about Django.</p></div>"
        result = clean_html(html)
        self.assertIn("This is a paragraph about Django", result)
