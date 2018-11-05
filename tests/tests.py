import requests
import unittest


class SimpleTextServerTest(unittest.TestCase):

    CLIP_URL = 'http://localhost:5000/clip/'

    def setUp(self):
        #server.clipboard.contents = ''
        pass

    def test_get_returns_json(self):
        r = requests.post(self.CLIP_URL, data={'clip': 'Clip 1'})
        _id = r.json()['saved']

        r = requests.get(self.CLIP_URL + _id)
        header = r.headers.get('content-type')
        self.assertEqual(header, 'application/json')

    def test_can_save_and_retrieve_single_item(self):
        r = requests.post(self.CLIP_URL, data={'clip': 'Clip 1'})
        self.assertEqual(r.status_code, requests.codes.ok)
        object_id = r.json()['saved']
        
        r = requests.get(self.CLIP_URL + object_id)
        self.assertEqual(r.status_code, requests.codes.ok)
        self.assertIn('Clip 1', r.text)

    def test_can_save_and_retrieve_multiple_items(self):
        r = requests.post(self.CLIP_URL, data={'clip': 'Clip 1'})
        self.assertEqual(r.status_code, requests.codes.ok)
        object_id_1 = r.json()['saved']

        r = requests.post(self.CLIP_URL, data={'clip': 'Clip 2'})
        self.assertEqual(r.status_code, requests.codes.ok)
        object_id_2 = r.json()['saved']
        
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
        r = requests.get(self.CLIP_URL + '111111111111111111111111')
        self.assertEqual(r.status_code, requests.codes.not_found)


if __name__ == "__main__":
    unittest.main()
