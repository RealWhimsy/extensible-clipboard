from json import loads
import requests
import unittest
from unittest.mock import patch
from uuid import uuid4

from pymongo import MongoClient


class RecipientTest(unittest.TestCase):

    CLIP_URL = 'http://localhost:5000/clip/'
    CLIPBOARD_URL = 'http://localhost:5000/clipboard/register'
    WEBHOOK_URL = 'http://localhost:5000/webhook/register'
    client = None
    db = None
    collection = None

    @classmethod
    def setUpClass(cls):
        cls.client = MongoClient()
        cls.db = cls.client.clipboard
        cls.clip_collection = cls.db['clip-collection']

    @classmethod
    def tearDownClass(cls):
        cls.clip_collection.delete_many({})

    def tearDown(self):
        # Removes all previously saved documents
        self.clip_collection.delete_many({})

    @patch('src.server.flask_server.requests.post')
    def test_normal_post_calls_clipboards_and_hooks(self, mock_post):
        requests.post(self.CLIPBOARD_URL, json={'url': 'http://localhost:456/'})
        requests.post(self.WEBHOOK_URL, json={'url': 'http://localhost:45678/'})

        r = requests.post(self.CLIP_URL, json={'mimetype': 'text/plain', 'data': 'test'})

        self.assertEqual(mock_post.call_count, 2)
