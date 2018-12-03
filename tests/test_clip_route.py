from json import loads
import requests
import unittest
from uuid import uuid4

from pymongo import MongoClient


class SimpleTextServerTest(unittest.TestCase):

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

    def test_get_returns_json(self):
        r = requests.post(self.CLIP_URL, data={'clip': 'Clip 1'})

        _id = loads(r.json())['_id']

        r = requests.get(self.CLIP_URL + _id)
        header = r.headers.get('content-type')
        self.assertEqual(header, 'application/json')

    def test_can_save_and_retrieve_single_item(self):
        r = requests.post(self.CLIP_URL, data={'clip': 'Clip 1'})
        self.assertEqual(r.status_code, requests.codes.created)

        object_id = loads(r.json())['_id']
        
        r = requests.get(self.CLIP_URL + object_id)
        self.assertEqual(r.status_code, requests.codes.ok)
        self.assertIn('Clip 1', r.text)

    def test_can_save_and_retrieve_multiple_items(self):
        r = requests.post(self.CLIP_URL, data={'clip': 'Clip 1'})
        self.assertEqual(r.status_code, requests.codes.created)
        object_id_1 = loads(r.json())['_id']

        r = requests.post(self.CLIP_URL, data={'clip': 'Clip 2'})
        self.assertEqual(r.status_code, requests.codes.created)
        object_id_2 = loads(r.json())['_id']
        
        object_1 = requests.get(self.CLIP_URL + object_id_1)
        object_2 = requests.get(self.CLIP_URL + object_id_2)

        self.assertIn('Clip 1', object_1.text)
        self.assertNotIn('Clip 2', object_1.text)

        self.assertIn('Clip 2', object_2.text)
        self.assertNotIn('Clip 1', object_2.text)

    def test_POST_need_correct_key(self):
        r = requests.post(self.CLIP_URL, data={'wrong': 'key'})
        self.assertEqual(r.status_code, requests.codes.bad_request)

    def test_not_existing_id_raises_404(self):
        _id = uuid4()
        r = requests.get(self.CLIP_URL + str(_id))
        self.assertEqual(r.status_code, requests.codes.not_found)

    def test_POST_with_uuid_returns_405(self):
        r = requests.post(self.CLIP_URL + str(uuid4()))
        self.assertEqual(r.status_code, requests.codes.method_not_allowed)

    def test_GET_without_id_returns_all_clips(self):
        requests.post(self.CLIP_URL, data={'clip': 'Clip 1'})
        requests.post(self.CLIP_URL, data={'clip': 'Clip 2'})

        r = requests.get(self.CLIP_URL)
        objects = r.json()
        self.assertIn('Clip 1', objects)
        self.assertIn('Clip 2', objects)

    def test_PUT_needs_id(self):
        r = requests.put(self.CLIP_URL)
        self.assertEqual(r.status_code, requests.codes.method_not_allowed)

    def test_PUT_needs_existing_url(self):
        _id = uuid4()
        r = requests.put(self.CLIP_URL + str(_id), data={'clip': 'clip new'})

        self.assertEqual(r.status_code, requests.codes.not_found)

    def test_correct_PUT_returns_updated_clip(self):
        r = requests.post(self.CLIP_URL, data={'clip': 'old clip'})
        _id = loads(r.json())['_id']

        r = requests.put(self.CLIP_URL + _id, data={'clip': 'new clip'})
        r = r.json()

        self.assertIn(_id, r)
        self.assertNotIn('old clip', r)
        self.assertIn('new clip', r)

    def test_delete_item_returns_no_content_on_success(self):
        r = requests.post(self.CLIP_URL, data={'clip': 'Test delete'})
        _id = loads(r.json())['_id']

        r = requests.delete(self.CLIP_URL + _id)

        self.assertEqual(r.status_code, 204)

    def test_delete_needs_id(self):
        r = requests.delete(self.CLIP_URL)
        self.assertEqual(r.status_code, 405)

    def test_deleted_item_get_no_longer_returned(self):
        r = requests.post(self.CLIP_URL, data={'clip': 'Test delete'})
        _id = loads(r.json())['_id']

        r = requests.delete(self.CLIP_URL + _id)
        r = requests.get(self.CLIP_URL + _id)

        self.assertEqual(r.status_code, 404)

    def test_cannot_delete_non_existing_item(self):
        _id = str(uuid4())
        r = requests.delete(self.CLIP_URL + _id)

        self.assertEqual(r.status_code, 404)

if __name__ == "__main__":
    unittest.main()
