import requests
import unittest

from pymongo import MongoClient


class SimpleTextServerTest(unittest.TestCase):

    CLIP_URL = 'http://localhost:5000/clip/'
    CLIPBOARD_URL = 'http://localhost:5000/clipboard/'
    client = None
    db = None
    collection = None

    @classmethod
    def setUpClass(cls):
        cls.client = MongoClient()
        cls.db = cls.client.clipboard
        cls.clip_collection = cls.db['clip-collection']
        cls.clipboard_collection = cls.db['clipboards']

    @classmethod
    def tearDownClass(cls):
        cls.clip_collection.delete_many({})
        cls.clipboard_collection.delete_many({})

    def tearDown(self):
        # Removes all previously saved documents
        self.clip_collection.delete_many({})
        self.clipboard_collection.delete_many({})

    def test_get_returns_json(self):
        r = requests.post(self.CLIP_URL, json={
            'mimetype': 'text/plain', 'data': 'Clip 1'})

        _id = r.headers['X-C2-_id']

        r = requests.get(self.CLIP_URL + _id)
        header = r.headers.get('content-type')
        self.assertIn('application/json', header)

    def test_register_returns_201_when_url(self):
        headers = {'content-type': 'application/json'}
        r = requests.post(self.CLIPBOARD_URL + 'register',
                          headers=headers,
                          json={'url': 'http://localhost:5555/'})
        self.assertEqual(r.status_code, 201)

    def test_server_only_accepts_json(self):
        r = requests.post(self.CLIPBOARD_URL + 'register',
                          data={'url': 'http://localhost:5555/'})
        self.assertEqual(r.status_code, 415)

    def test_server_refuses_non_url(self):
        headers = {'content-type': 'application/json'}
        r = requests.post(self.CLIPBOARD_URL + 'register',
                          headers=headers, json={'url': 'notAnURL'})
        self.assertEqual(r.status_code, 422)


if __name__ == '__main__':
    unittest.main()
