from datetime import datetime
from uuid import uuid4

from bson.json_util import dumps
from bson.objectid import ObjectId
from pymongo import MongoClient

class ClipDatabase:

    def __init__(self):
        self.client = MongoClient()
        self.db = self.client.clipboard
        self.clip_collection = self.db['clip-collection']

    def save_clip(self, content):
        _id = uuid4()
        modified_date = datetime.now()
        new_clip = {
                '_id': str(_id),
                'text': content,
                'last_modified': modified_date.isoformat()
        }

        new_clip = self.clip_collection.insert_one(new_clip)
        return str(new_clip.inserted_id)

    def get_clip_by_id(self,  id):
        clip = self.clip_collection.find_one({'_id': id})
        clip = dumps(clip)

        if clip is 'null':
            return None
        else:
            return dumps(clip)

    def get_all_clips(self):
        return dumps(self.clip_collection.find({}))
