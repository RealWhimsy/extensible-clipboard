from base64 import b64encode
from datetime import datetime
from configparser import ConfigParser
from uuid import UUID, uuid4

from bson.binary import Binary, UUID_SUBTYPE
from bson.json_util import default, dumps
from bson.objectid import ObjectId
from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.collection import ReturnDocument

from src.server.exceptions import *


class ClipDatabase:

    def __init__(self):
        config = ConfigParser()
        config.read('config.ini')
        database_conf = config['database']
        self.client = MongoClient(
                database_conf['url'],
                int(database_conf['port']))
        self.db = getattr(self.client, database_conf['database'])
        self.clip_collection = self.db[
                database_conf['collection']
        ]
        self.clipboard_collection = self.db[
                database_conf['clipboard_collection']
        ]

    def _create_binary_uuid(self, _id):
        """
        Creates an Mongo binary uuid from the string-representation of a uuid4

        https://stackoverflow.com/questions/51283260/pymongo-uuid-search-not-returning-documents-that-definitely-exist
        """  # noqc
        if type(_id) is not str:
            _id = str(_id)

        bin_id = UUID(_id)
        bin_id = Binary(bin_id.bytes, UUID_SUBTYPE)
        return bin_id

    def _build_json_response_clip(self, clip):
        """
        The method strips the additional informations added by Mongo
        in order to return pure json
        i.e. convert uuid-objects to their string or handle binary
        """
        clip['_id'] = str(clip['_id'])

        if 'filename' in clip:
            data = b64encode(clip['data'])

            clip['data'] = str(data)[2:-1]

        if 'parent' in clip:
            clip['parent'] = str(clip['parent'])

        return clip

    def _get_related_entries(self, parent):
        parent_id = self._create_binary_uuid(parent['_id'])
        return self.clip_collection.find(
                {'$or': [
                    {'parent': parent_id},
                    {'_id': parent_id}
                ]})

    def _get_parent(self, child):
        return self.clip_collection.find_one({
                '_id': self._create_binary_uuid(child['parent'])
            })

    def _find_best_match(self, parent, preferred_types):
        """
        Searches all children of parent if a direct match for
        the specified mimetypes can be found.
        :param parent: Mongo-object, should have children in db
        :param preferred_types: List of tuples representing the Accept-header
            of the request. Format: ('text/plain', 1.0).
            The list is to be sorted by the rules of the Accept-header
        :return: The Mongo-object with the closes match. parent, if no match
        """
        if 'parent' in parent:  # If requested entity is a child itself
            parent = self._get_parent(parent)

        children = self._get_related_entries(parent)

        # first round, exact match
        for curr_type in preferred_types:
            for child in children:
                if child['mimetype'] == curr_type[0]:
                    return child

        # second round, wildcard match
        children.rewind()
        for curr_type in preferred_types:
            # Check if mimestring is wildcard and get part before the /
            mime_base = curr_type[0]
            if '*' in mime_base:
                mime_base = mime_base.split('/')[0]

                for child in children:
                    if mime_base in child['mimetype']:
                        return child

        # No exact or wildcard match, default to parent
        return parent

    def save_clip(self, data):
        """
        Inserts a new clip-object into the database.

        :param content: The content of the new clip-object
        :return: A json-like string with the newly created object
        """
        _id = uuid4()
        _id = self._create_binary_uuid(str(_id))
        modified_date = datetime.now()
        new_clip = {}

        if 'parent' in data:
            parent_id = self._create_binary_uuid(data['parent'])
            parent = self.clip_collection.find_one({'_id': parent_id})
            # Abandon insert, when parent-id not in db
            if parent is None:
                raise ParentNotFoundException
            if 'parent' in parent:
                raise GrandchildException
            if parent['mimetype'] == data['mimetype']:
                raise SameMimetypeException
            new_clip['parent'] = self._create_binary_uuid(data['parent'])

        new_clip['_id'] = _id
        new_clip['data'] = data['data']
        new_clip['mimetype'] = data['mimetype']
        new_clip['creation_date'] = modified_date.isoformat()
        new_clip['last_modified'] = modified_date.isoformat()

        if 'filename' in data:
            new_clip['filename'] = data['filename']

        insert_result = self.clip_collection.insert_one(new_clip)
        new_clip = self.clip_collection.find_one({'_id': _id})
        return self._build_json_response_clip(new_clip)

    def get_clip_by_id(self, clip_id, preferred_types=None):
        """
        Searches the database for a clip with the specified id.

        :param id: The id to be searched. Has to be the string representation
                   of a uuid-object
        :param preferred_types: List of tuples representing the Accept-header
            of the request. Format of single entry: ('text/plain', 1.0).
            The list is to be sorted by the rules of the Accept-header
        :return: Json-like string containing the found object or None
                 if no object with the id could be found in the database
        """
        clip_id = self._create_binary_uuid(clip_id)
        clip = self.clip_collection.find_one({'_id': clip_id})

        if clip is not None:
            if preferred_types:  # Request specified mimetype
                if not clip['mimetype'] == preferred_types[0]:
                    clip = self._find_best_match(clip, preferred_types)

            clip = self._build_json_response_clip(clip)
        return clip

    def get_all_clips(self):
        """
        :return: Json-like string containing all clips
        """
        results = list(self.clip_collection.find({}))
        json_result = [self._build_json_response_clip(i) for i in results]
        return json_result

    def get_latest(self):
        results = self.clip_collection.find({
                "parent": {"$exists": False}
            })
        results.sort('creation_date', ASCENDING)
        if results.count():
            r = results[0]
            return self._build_json_response_clip(r)
        else:
            return None

    def update_clip(self, object_id, data):
        """
        Updates an existing clip-object with new data.

        :param object_id: Id of the object to be updated
        :param data: New data. For safety, you should not replace text with
                     a file and vice versa
        :return: Json string containing the newly updated object or None
                 if no object with the id could be found in the database
        """
        bin_id = self._create_binary_uuid(object_id)
        new_doc = self.clip_collection.find_one_and_update(
                {'_id': bin_id},
                {'$set': {'data': data['data']}},
                return_document=ReturnDocument.AFTER
        )

        if new_doc is not None:  # When replace actually did take place
            new_doc = self._build_json_response_clip(new_doc)

        return new_doc

    def delete_entry_by_id(self, clip_id):
        """
        Deletes an object.
        :param clip_id: Id of the objecte to be deleted
        :return: Number of deleted objects.
                 Can be zero, if no objects were deleted
        """
        bin_id = self._create_binary_uuid(clip_id)
        clip = self.clip_collection.find_one({'_id': bin_id}) or {}
        if 'parent' in clip:  # Only delete entry when child
            return self.clip_collection.delete_one({
                    '_id': bin_id
                }).deleted_count
        else:  # Cascade when parent
            deleted = self.clip_collection.delete_many(
                    {'$or': [
                        {'parent': bin_id},
                        {'_id': bin_id}
                    ]})
            return deleted.deleted_count

    def get_alternatives(self, clip_id):
        bin_id = self._create_binary_uuid(clip_id)
        parent = self.clip_collection.find_one({'_id': bin_id})
        if parent is None:
            return None
        else:
            results = []
            clips = self._get_related_entries(parent)
            for clip in clips:
                results.append({
                    '_id': str(clip['_id']),
                    'mimetype': clip['mimetype']
                })
            return results

    def add_recipient(self, url, is_hook):
        if self.clipboard_collection.find_one({'url': url}) is not None:
            return None

        _id = uuid4()
        _id = self._create_binary_uuid(str(_id))
        new_clipboard = {}

        new_clipboard['_id'] = _id
        new_clipboard['url'] = url
        new_clipboard['is_hook'] = is_hook

        insert_result = self.clipboard_collection.insert_one(new_clipboard)
        new_clipboard = self.clipboard_collection.find_one({'_id': _id})

        return self._build_json_response_clip(new_clipboard)

    def get_recipients(self):
        if self.clipboard_collection.count_documents({}) is 0:
            return None
        results = self.clipboard_collection.find({})
        return list(self.clipboard_collection.find({}))
