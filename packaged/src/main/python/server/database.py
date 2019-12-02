from datetime import datetime
from configparser import ConfigParser
from uuid import UUID, uuid4

from bson.binary import Binary, UUID_SUBTYPE
from pymongo import ASCENDING, MongoClient
from pymongo.collection import ReturnDocument

from server.exceptions import (GrandchildException, ParentNotFoundException)

from util.context import Context

class ClipDatabase:
    """
    This database is mainly for storing single clips. A clip is an object
    consisting of a mimetype and the associated data as they would be saved
    in the OS-clipboard. Additionally, metadata can be stored with a clip,
    the database should simply save those fields, their creation
    and validation is the responsibility of the parser.
    A clip may be part of a simple tree-like structure containing one root
    (called parent) and n leaves (called children). This relation is used
    to identify clips representing the same data-item and originates
    from the different representations of an item provided by the OS-clipboard.

    In addition to clips, Recipients can be saved. A recipient represents
    either a remote clipboard or a webhook and will have an Url pointing
    to itself. A webhook will also have a list of mimetypes it is subscribed
    to.
    """

    def __init__(self):
        """
        Mainly reads the config from dbconfig.ini and establishes
        a connection to the database
        """
        config = ConfigParser()
        config.read(Context.ctx.get_resource('config/dbconfig.ini'))
        database_conf = config['mongodb']
        self.client = MongoClient(
                database_conf['url'],
                int(database_conf['port']))
        self.db = getattr(self.client, database_conf['database'])
        self.clip_collection = self.db[
                database_conf['collection']
        ]
        self.clip_collection.create_index([("creation_date", ASCENDING)])
        self.clipboard_collection = self.db[
                database_conf['clipboard_collection']
        ]

    def _create_binary_uuid(self, _id):
        """
        Creates an Mongo binary uuid from the string-representation of a uuid4
        This is supposedly faster then using strings as PK's

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

        if 'parent' in clip:
            clip['parent'] = str(clip['parent'])

        return clip

    def _get_related_entries(self, parent):
        """
        Returns a cursor containing the parent itself as well as
        all it's children.
        """
        parent_id = self._create_binary_uuid(parent['_id'])
        return self.clip_collection.find(
                {'$or': [
                    {'parent': parent_id},
                    {'_id': parent_id}
                ]})

    def _get_parent(self, child):
        """
        Returns the parent-document of the specified child.
        Should never return None
        """
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
        :return: The Mongo-object with the closes match. None, if no match
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
        return None

    def save_clip(self, data):
        """
        Inserts a new clip-object into the database.
        This method also adds ISO-Timestamps to the new object
        with the keys creation_date and last_modified

        :param data: The content of the new clip-object
        :return: A dict representing the new item
        """
        _id = uuid4()
        _id = self._create_binary_uuid(str(_id))
        modified_date = datetime.now()
        new_clip = {}

        if 'parent' in data:
            parent_id = self._create_binary_uuid(data.pop('parent'))
            parent = self.clip_collection.find_one({'_id': parent_id})
            # Abandon insert, when parent-id not in db
            if parent is None:
                raise ParentNotFoundException
            if 'parent' in parent:
                raise GrandchildException
            new_clip['parent'] = parent_id

        new_clip['_id'] = _id
        new_clip['creation_date'] = modified_date.isoformat()
        new_clip['last_modified'] = modified_date.isoformat()
        for key, value in data.items():
            new_clip[key] = value
        print(new_clip)
        self.clip_collection.insert_one(new_clip)
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
        :return: A dict containing the found object or None
                 if no object with the id could be found in the database
        """
        clip_id = self._create_binary_uuid(clip_id)
        clip = self.clip_collection.find_one({'_id': clip_id})

        if clip is not None:
            if preferred_types:  # Request specified mimetype
                if not clip['mimetype'] == preferred_types[0]:
                    best_match = self._find_best_match(clip, preferred_types)
                    if best_match:
                        clip = best_match

            clip = self._build_json_response_clip(clip)
        return clip

    def get_all_clips(self):
        """
        A list containing all clips in the database. Sorted by creation_date
        in ascending order (oldest first)
        """
        projection = {'data': False}
        results = list(self.clip_collection.find({}, projection=projection)
                       .sort('creation_date', ASCENDING))
        json_result = [self._build_json_response_clip(i) for i in results]
        return json_result

    def get_latest(self):
        """
        Returns the parent clip that was added last into the database
        as a dict
        """
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
                }).raw_result
        else:  # Cascade when parent
            deleted = self.clip_collection.delete_many(
                    {'$or': [
                        {'parent': bin_id},
                        {'_id': bin_id}
                    ]})
            return deleted.deleted_count

    def get_alternatives(self, clip_id):
        """
        Returns all siblings and the parent for clip_id
        as a list of dicts
        """
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

    def add_recipient(self, url, is_hook, subscribed_types):
        """
        Adds a recipient to the database. If there is already an recipient
        with the same URL, this will be returned instead. Subscribed types
        for a hook will be updated beforehand.

        :param url: The URL the recipient can be reached at
        :param is_hook: True, if recipient is a hook otherwise it will be
                        treated as a clipboard
        :param subscribed_types: List of mimetypes the hook is interested in.
                                 Will be ignored for clipboards
        """
        old_instance = self.clipboard_collection.find_one({'url': url})
        if old_instance is not None:
            if subscribed_types:
                old_instance = self.clipboard_collection.find_one_and_update(
                    {'url': url},
                    {'$set': {'subscribed_types': subscribed_types}},
                    return_document=ReturnDocument.AFTER)
            return self._build_json_response_clip(old_instance)

        _id = uuid4()
        _id = self._create_binary_uuid(str(_id))
        new_clipboard = {}

        new_clipboard['_id'] = _id
        new_clipboard['url'] = url
        new_clipboard['is_hook'] = is_hook
        if subscribed_types:
            new_clipboard['subscribed_types'] = subscribed_types

        self.clipboard_collection.insert_one(new_clipboard)
        new_clipboard = self.clipboard_collection.find_one({'_id': _id})

        return self._build_json_response_clip(new_clipboard)

    def get_recipients(self):
        """
        Returns a list of all saved recipients represented as dicts
        """
        if self.clipboard_collection.count_documents({}) is 0:
            return None
        print("YAHOOO")
        print(list(self.clipboard_collection.find({})))
        return list(self.clipboard_collection.find({}))



import sqlite3
# Sql Implementation of the extensible clipboard database module
class ClipSqlDatabase(ClipDatabase):
    statement_create_clip_table = \
    """
    CREATE TABLE IF NOT EXISTS clips (
        _id VARCHAR(40) PRIMARY KEY,
        creation_date VARCHAR(40),
        last_modified VARCHAR(40),
        mimetype VARCHAR(40),
        data BLOB        
    );
    """

    statement_create_clipboard_table = \
    """
    CREATE TABLE IF NOT EXISTS clipboards (
        _id VARCHAR(40) PRIMARY KEY,
        url VARCHAR(40),
        is_hook INTEGER
    );
    """

    statement_add_recipient =   """ INSERT INTO clipboards (_id, url, is_hook) VALUES (?, ?, ?); """
    statement_get_recipients =  """ SELECT * FROM clipboards; """

    statement_add_clip = """ INSERT INTO clips (_id, creation_date, last_modified, mimetype, data) VALUES (?, ?, ?, ?, ?);"""
    statement_get_clips = """ SELECT * FROM clips;"""

    def __init__(self):
        config = ConfigParser()
        config.read(Context.ctx.get_resource('config/dbconfig.ini'))
        self.file_name = config['sqlite']['file_name']

        connection = self._get_connection()
        connection.execute(self.statement_create_clip_table)
        connection.execute(self.statement_create_clipboard_table)


    def _get_connection(self):
        # https://stackoverflow.com/questions/16936608/storing-bools-in-sqlite-database?rq=1
        sqlite3.register_adapter(bool, int)
        sqlite3.register_converter("BOOLEAN", lambda v: bool(int(v)))
        connection = sqlite3.connect(self.file_name)
        return connection

    def _get_recipient_from_cursor_item(self, item):
        return {
            '_id': UUID(item[0]),
            'url': item[1],
            'is_hook': bool(item[2])
        }

    def _get_clip_from_cursor_item(self, item):
        print(item)
        return {
            '_id': None,
            'creation': None
        }

    # RECIPIENT OPERATIONS

    # Return all registered recipients
    def get_recipients(self):
        conn = self._get_connection()
        cursor = conn.execute(self.statement_get_recipients)
        if len(list(cursor)) == 0:
            return None
        result = []
        for row in cursor:
            result.append(self._get_recipient_from_cursor_item(row))
        conn.close()
        return result

    # Register another clipboard as recipient
    def add_recipient(self, url, is_hook, subscribed_types):
        _id = uuid4().__str__()
        connection = self._get_connection()
        connection.execute(self.statement_add_recipient, (_id, url, is_hook))
        connection.commit()
        connection.close()
        pass

    # CLIP OPERATIONS

    # Insert a new clip
    def save_clip(self, data):
        _id = str(uuid4())
        date = datetime.now()
        new_clip = {}

        if 'parent' in data:
            parent_id = str(data.pop('parent'))
            parent = self.get_clip_by_id(parent_id)
            # Abandon insert, when parent-id not in db
            if parent is None:
                raise ParentNotFoundException
            if 'parent' in parent:
                raise GrandchildException
            new_clip['parent'] = parent_id
        conn = self._get_connection()
        conn.execute(self.statement_add_clip, (_id, date.isoformat(), date.isoformat(), data['mimetype'], data['data']))
        conn.commit()
        conn.close()
        return self.get_clip_by_id(_id)


    # Get all clips
    def get_all_clips(self):
        conn = self._get_connection()
        cursor = conn.execute(self.statement_get_clips)
        result = []
        for row in cursor:
            result.append(self._get_clip_from_cursor_item(row))
        print(result)
        return result

    def get_alternatives(self, clip_id):
        pass

    def delete_entry_by_id(self, clip_id):
        pass

    def update_clip(self, object_id, data):
        pass

    def get_latest(self):
        pass


    def get_clip_by_id(self, clip_id, preferred_types=None):
        pass
