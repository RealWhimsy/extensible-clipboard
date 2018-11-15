from datetime import datetime
from uuid import UUID, uuid4

from bson.binary import Binary, UUID_SUBTYPE
from bson.json_util import default, dumps
from bson.objectid import ObjectId
from pymongo import MongoClient


class ClipDatabase:

    def __init__(self):
        self.client = MongoClient()
        self.db = self.client.clipboard
        self.clip_collection = self.db['clip-collection']

    def create_binary_uuid(self, id):
        """
        https://stackoverflow.com/questions/51283260/pymongo-uuid-search-not-returning-documents-that-definitely-exist
        """  # noqc
        id_bytes = id.bytes
        bin_id = Binary(bytes(bytearray(id_bytes)), UUID_SUBTYPE)
        return bin_id

    def save_clip(self, content):
        """
        Inserts a new clip-object into the database.

        :param content: The content of the new clip-object
        :return: A json-like string with the newly created object
        """
        _id = uuid4()
        _id = self.create_binary_uuid(_id)
        modified_date = datetime.now()
        new_clip = {
                '_id': _id,
                'data': content,
                'last_modified': modified_date.isoformat()
        }

        insert_result = self.clip_collection.insert_one(new_clip)
        new_clip = self.clip_collection.find_one({'_id': _id})
        return dumps(new_clip)

    def get_clip_by_id(self,  clip_id):
        """
        Searches the database for a clip with the specified id.

        :param id: The id to be searched. Has to be the string representation
                   of a uuid-object
        :return: Json-like string containing the found object or None
                 if no object with the id could be found in the database
        """
        clip_id = UUID(clip_id)
        clip_id = self.create_binary_uuid(clip_id)

        clip = self.clip_collection.find_one({'_id': clip_id})
        clip = dumps(clip)

        if clip is 'null':
            return None
        else:
            return clip

    def get_all_clips(self):
        """
        :return: Json-like string containing all clips
        """
        return dumps(self.clip_collection.find({}))
