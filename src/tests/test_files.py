from base64  import b64decode

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

            self.assertEqual(r.status_code, requests.codes.created)

    def test_wrong_mime_type_results_in_error(self):
        with open('tests/res/example.txt', 'rb') as f:
            files = {'file': ('example.txt', f,  'text/xml')}
            r = requests.post(self.CLIP_URL, files=files)

            self.assertEqual(r.status_code, requests.codes.bad_request)

    def test_upload_returns_file(self):
        with open('tests/res/example.txt', 'rb') as f:
            files = {'file': ('example.txt', f, 'text/plain')}
            r = requests.post(self.CLIP_URL, files=files)

            filename = r.json()['filename']
            received_data = r.json()['data']

            received_data = b64decode(received_data)

            f.seek(0)
            self.assertEqual(received_data, f.read())
            self.assertEqual(filename, 'example.txt')

    def test_image_upload_returns_file(self):
        with open('tests/res/example.txt', 'rb') as f:
            files = {'file': ('example.jpg', f, 'image/jpeg')}
            r = requests.post(self.CLIP_URL, files=files)

            filename = r.json()['filename']
            received_data = r.json()['data']

            received_data = b64decode(received_data)

            f.seek(0)
            self.assertEqual(received_data, f.read())

    def test_url_upload_returns_correct_file(self):
        image_url = 'http://www.google.com/favicon.ico'
        data = {'mimetype': 'text/plain', 'data': image_url, 'download_request': True}
        r = requests.post(self.CLIP_URL, json=data)
        r1 = requests.get(image_url, allow_redirects=True)
        server_data = b64decode(r.json()['data'])
        # shows you, it's working :p
        f = open('tests/res/favicon.ico', 'wb')
        f.write(server_data)
        f.close()
        self.assertEqual(server_data, r1.content)

if __name__ == '__main__':
    unittest.main()
