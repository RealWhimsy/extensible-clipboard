import unittest

import server.main as server


class SimpleTextServerText(unittest.TestCase):

    def setUp(self):
        server.clipboard.contents = ''

    def test_say_hello_returns_content_of_clipboard(self):
        response = server.get_contents()
        self.assertEqual(response, server.clipboard.contents)

    def test_set_contents_changes_internal_state(self):
        new_string = "Own contents"
        self.assertNotEqual(new_string, server.clipboard.contents)
        server.set_contents(new_string)
        self.assertEqual(new_string, server.clipboard.contents)

    def test_new_content_returned_after_set_is_called(self):
        new_contents = "Own contents"
        old_contents = str(server.clipboard.contents)

        self.assertEqual(server.get_contents(), old_contents)

        server.set_contents(new_contents)

        self.assertNotEqual(server.get_contents(), old_contents)
        self.assertEqual(server.get_contents(), new_contents)


if __name__ == "__main__":
    unittest.main()
