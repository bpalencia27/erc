import unittest
from app import create_app

class TestConfig:
    TESTING = True
    SECRET_KEY = 'test-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    @staticmethod
    def init_app(app):
        pass

class BasicTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_app_exists(self):
        self.assertIsNotNone(self.app)

    def test_app_is_testing(self):
        self.assertTrue(self.app.config['TESTING'])


if __name__ == '__main__':
    unittest.main()
