import os
import unittest


class TestDashboardAuth(unittest.TestCase):
    def test_middleware_exists(self):
        path = os.path.join('dashboard', 'src', 'middleware.ts')
        self.assertTrue(os.path.exists(path), 'middleware.ts should exist')
        with open(path, 'r') as f:
            content = f.read()
        self.assertIn('createMiddlewareClient', content)
        self.assertIn("'/login'", content)

    def test_settings_link_restricted(self):
        path = os.path.join('dashboard', 'src', 'app', 'layout.tsx')
        with open(path, 'r') as f:
            layout = f.read()
        self.assertIn("role === 'admin'", layout)


if __name__ == '__main__':
    unittest.main()
