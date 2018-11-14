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
        """
        Inserts a new clip-object into the database.

        :param content: The content of the new clip-object
        :return: A string with the id of the created object
        """
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
        """
        Searches the database for a clip with the specified id.

        :param id: The id to be searched. Has to be the string representation
                   of a uuid-object
        :return: Json-like string containing the found object or None
                 if no object with the id could be found in the database
        """
        clip = self.clip_collection.find_one({'_id': id})
        clip = dumps(clip)

        if clip is 'null':
            return None
        else:
            return dumps(clip)

    def get_all_clips(self):
        """
        :return: Json-like string containing all clips
        """
        return dumps(self.clip_collection.find({}))
