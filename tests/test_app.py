import unittest
import json
from app import app

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_chat(self):
        response = self.app.post('/chat', json={'query': 'Tell me a joke.'})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('response', data)
        self.assertEqual(data['response'], 'Tell me a joke.')

if __name__ == '__main__':
    unittest.main()
