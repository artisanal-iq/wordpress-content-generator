import unittest

from agents.shared import utils


class TestSlugifyUtils(unittest.TestCase):
    def test_slugify_removes_punctuation(self):
        title = "Hello, World! This is a Test."
        self.assertEqual(utils.slugify(title), "hello-world-this-is-a-test")

    def test_slugify_handles_special_chars(self):
        title = "Python & Django @ Scale"
        self.assertEqual(utils.slugify(title), "python-django-scale")


if __name__ == "__main__":
    unittest.main()
