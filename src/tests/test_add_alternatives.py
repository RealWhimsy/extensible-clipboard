from json import loads
import requests
import unittest
from uuid import uuid4, UUID

from pymongo import MongoClient


class SimpleTextServerTest(unittest.TestCase):

    CLIP_URL = 'http://localhost:5000/clip/'
    CLIP_ID_URL = 'http://localhost:5000/clip/{}/'
    ADD_CHILD_URL = CLIP_URL + 'add_child'
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

    def create_parent(self):
        r = requests.post(self.CLIP_URL,
                      data={'mimetype': 'text/plain',
                            'data': 'parentClip'
                           })

        return loads(r.json())['_id']

    def add_child(self, parent_id):
        r = requests.post(
                self.CLIP_URL + parent_id + '/add_child',
                data={'mimetype': 'text/html',
                      'data': '<h1>Child text</h1>',
                      'parent': parent_id
                     })
        return r

    def test_add_without_parent_fails(self):
        fake_id = uuid4()

        r = requests.post(
                self.CLIP_URL + str(fake_id) + '/add_child',
                data={'mimetype': 'text/plain',
                      'data': 'ClipChild',
                      'parent': str(fake_id)
                     })

        self.assertEqual(r.status_code, 412)

    def test_add_child_returns_child(self):
        parent_id = self.create_parent()
        
        r = self.add_child(parent_id)

        self.assertEqual(r.status_code, 201)
        json = loads(r.json())
        self.assertIn('parent', json)

        try:
            UUID(json['parent'])
        except ValueError:
            self.fail('Cannot create UUID from {}'.format(json['parent']))

    def test_child_must_have_different_mimetype(self):
        parent_id = self.create_parent()


        r = requests.post(
                self.CLIP_URL + parent_id + '/add_child',
                data={'mimetype': 'text/plain',
                      'data': 'ClipChild',
                      'parent': parent_id
                     })
        self.assertEqual(r.status_code, 422)

    def test_server_honors_ACCEPT_header(self):
        parent_id = self.create_parent()
        self.add_child(parent_id)
        header = {'accept': 'text/html, application/json;q=0.5 ,text/plain;q=0.8'}

        r = requests.get(
            self.CLIP_URL + parent_id,
            headers=header
        )

        json = loads(r.json())
        self.assertIn('<h1>Child text</h1>', json['data'])

    def test_wildcard_in_ACCEPT_header_honored(self):
        parent_id = self.create_parent()
        self.add_child(parent_id)

        r = requests.post(
                self.CLIP_URL + parent_id + '/add_child',
                data={'mimetype': 'application/json',
                      'data': '{"key": "json-child"}',
                      'parent': parent_id
                     })

        header = {'accept': 'application/*'}
        r = requests.get(
            self.CLIP_URL + parent_id,
            headers=header
        )

        json = loads(r.json())
        self.assertIn('json-child', json['data'])

    def test_cannot_create_grandchildren(self):
        parent_id = self.create_parent()
        child = self.add_child(parent_id)
        child_id = loads(child.json())['_id']
        grandchild = self.add_child(child_id)

        self.assertEqual(grandchild.status_code, 422)
        self.assertIn('Can only create child for original entry', grandchild.json()['error'])

    def test_ACCEPT_will_always_get_best_result(self):
        # parent: plain, child: html, query:child but prefers plains > parent delivered
        parent_id = self.create_parent()
        child = self.add_child(parent_id)
        child_id = loads(child.json())['_id']

        header = {'accept': 'text/plain;q=0.8, text/html;q=0.3'}

        r = requests.get(
                self.CLIP_URL + child_id, 
                headers=header
        )

        json = loads(r.json())
        self.assertIn('parentClip', json['data'])

    def test_delete_parent_will_delete_children(self):
        parent_id = self.create_parent()
        child = self.add_child(parent_id)
        child_id = loads(child.json())['_id']
        r = requests.get(self.CLIP_URL + child_id)
        self.assertEqual(r.status_code, 200)

        r = requests.delete(self.CLIP_ID_URL.format(parent_id))
        self.assertEqual(r.status_code, 204)

        r = requests.get(self.CLIP_URL + child_id)
        self.assertEqual(r.status_code, 404)

    def test_can_get_list_of_alternatives(self):
        parent_id = self.create_parent()
        child = self.add_child(parent_id)
        child_id = loads(child.json())['_id']
        r = requests.get(self.CLIP_URL + parent_id + '/get_alternatives/')
        self.assertEqual(r.status_code, 200)

        self.assertIn(parent_id, r.text)
        self.assertIn(child_id, r.text)

    def test_unrelated_clip_is_not_returned(self):
        parent_id = self.create_parent()
        child = self.add_child(parent_id)
        child_id = loads(child.json())['_id']
        r = requests.post(self.CLIP_URL,
                      data={'mimetype': 'text/plain',
                            'data': 'WrongTurn'
                           })
        wrong_id = loads(r.json())['_id']
        r = requests.get(self.CLIP_URL + parent_id + '/get_alternatives/')

        self.assertIn(parent_id, r.text)
        self.assertIn(child_id, r.text)
        self.assertNotIn(wrong_id, r.text)

if __name__ == '__main__':
    unittest.main()
