from pymongo import MongoClient

class ClipDatabase:

    def __init__(self):
        self.client = MongoClient()
        self.db = self.client.clipboard
        self.clip_collection = self.db['clip-collection']

    def save_clip(self, content):
        new_clip = {'text': content}
        new_clip = self.clip_collection.insert_one(new_clip)
        return new_clip.inserted_id
