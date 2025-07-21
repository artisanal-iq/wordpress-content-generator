import unittest

from agents.shared.markdown_utils import markdown_to_html


class TestMarkdownUtils(unittest.TestCase):
    def test_markdown_to_html_basic(self):
        md = "# Title\n\nHello **world**"
        html = markdown_to_html(md)
        self.assertIn("<h1>Title</h1>", html)
        self.assertIn("<strong>world</strong>", html)


if __name__ == "__main__":
    unittest.main()
