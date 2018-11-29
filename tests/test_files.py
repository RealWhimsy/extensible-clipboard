from base64  import b64decode
from json import loads

import requests
import unittest

from pymongo import MongoClient


class FileUploadTest(unittest.TestCase):

    CLIP_URL = 'http://localhost:5000/clip/'
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

    def test_can_upload_simple_file(self):
        with open('tests/res/example.txt', 'rb') as f:
            files = {'file': ('example.txt', f,  'text/plain')}
            r = requests.post(self.CLIP_URL, files=files)

            self.assertEqual(r.status_code, requests.codes.ok)

    def test_wrong_mime_type_results_in_error(self):
        with open('tests/res/example.txt', 'rb') as f:
            files = {'file': ('example.txt', f,  'text/xml')}
            r = requests.post(self.CLIP_URL, files=files)

            self.assertEqual(r.status_code, requests.codes.bad_request)

    def test_upload_returns_file(self):
        with open('tests/res/example.txt', 'rb') as f:
            files = {'file': ('example.txt', f, 'text/plain')}
            r = requests.post(self.CLIP_URL, files=files)

            filename = loads(r.json())['filename']
            received_data = loads(r.json())['data']

            received_data = b64decode(received_data)

            f.seek(0)
            self.assertEqual(received_data, f.read())
            self.assertEqual(filename, 'example.txt')

    def test_image_upload_returns_file(self):
        with open('tests/res/example.txt', 'rb') as f:
            files = {'file': ('example.jpg', f, 'image/jpeg')}
            r = requests.post(self.CLIP_URL, files=files)

            filename = loads(r.json())['filename']
            received_data = loads(r.json())['data']

            received_data = b64decode(received_data)

            f.seek(0)
            self.assertEqual(received_data, f.read())
