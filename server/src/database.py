from datetime import datetime
from uuid import UUID, uuid4
import os

from exceptions import (GrandchildException, ParentNotFoundException)

from peewee import Model, DateField, PrimaryKeyField, ForeignKeyField, CharField, BlobField, IntegerField, SqliteDatabase, BooleanField
from playhouse.shortcuts import model_to_dict
path = os.path.expanduser('~/clip_collection.db')
database = SqliteDatabase(path)


class BaseModel(Model):
    class Meta:
        database = database


class Clip(BaseModel):
    _id = CharField(primary_key=True)
    creation_date = CharField()
    last_modified = CharField()
    mimetype = CharField()
    data = BlobField()
    src_app = CharField(null=True)
    filename = CharField(null=True)
    #parent = ForeignKeyField('self', backref="children", null=True)
    parent = CharField(null=True)




class Clipboard(BaseModel):
    _id = CharField(primary_key=True)
    url = CharField()
    is_hook = BooleanField()


class PreferredTypes(BaseModel):
    parent = ForeignKeyField(Clipboard, backref="preferred_types")
    type = CharField()



################################################################################################
#
# SQLite peewee Implementation of database
#
################################################################################################

class ClipSqlPeeweeDatabase:

    def __init__(self):
        database.create_tables([Clip, Clipboard, PreferredTypes])

    def _get_parent(self, child):
        if(child['parent'] is None):
            return child
        else:
            q = Clip.select().where(Clip._id == child['parent'])
            if(q.count() < 1):
                return None
            else:
                return model_to_dict(q.get())

    def _get_children(self, parent):
        childrenCursor = Clip.select().where(Clip.parent == parent['_id']).execute()
        result = []
        for item in childrenCursor:
            result.append(model_to_dict(item))
        return result

    def _find_best_match(self, clip, preferred_types):
        """
        Searches all children of parent if a direct match for
        the specified mimetypes can be found.
        :param parent: Mongo-object, should have children in db
        :param preferred_types: List of tuples representing the Accept-header
            of the request. Format: ('text/plain', 1.0).
            The list is to be sorted by the rules of the Accept-header
        :return: The Mongo-object with the closes match. None, if no match
        """
        parent = self._get_parent(clip)
        children = self._get_children(parent)

        # first round, exact match
        for curr_type in preferred_types:
            print(curr_type)
            if parent['mimetype'] == curr_type[0]:
                return parent
            for child in children:
                if child['mimetype'] == curr_type[0]:
                    return child

        # second round, wildcard match
        for curr_type in preferred_types:
            # Check if mimestring is wildcard and get part before the /
            mime_base = curr_type[0]
            if '*' in mime_base:
                mime_base = mime_base.split('/')[0]

                for child in children:
                    if mime_base in child['mimetype']:
                        return child

        # No exact or wildcard match, default to sent-in clip
        return clip

    def __get_uuidv4__(self):
        return (uuid4().__str__())



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

        clipboards_with_url = Clipboard.select().where(Clipboard.url==url)
        if clipboards_with_url.count() > 0:
            return model_to_dict(clipboards_with_url.get())
        else:
            id = self.__get_uuidv4__()
            clipboard = Clipboard.create(_id=id,url=url,is_hook=is_hook)
            clipboard.save()
            if subscribed_types:
                for type in subscribed_types:
                    newItem = PreferredTypes.create(parent=id, type=type)
                    newItem.save()
            return model_to_dict(Clipboard.get(Clipboard._id==id))

    def get_recipients(self):
        recipients = Clipboard.select().execute()
        results = []
        """
        Returns a list of all saved recipients represented as dicts
        """
        for rec in recipients:
            current_recipient = model_to_dict(rec, backrefs=True)
            # TODO: refactor this to avoid cumbersome mapping
            current_recipient['preferred_types'] = list(map(lambda item: item['type'], current_recipient['preferred_types']))
            results.append(current_recipient)
        return results

    def delete_all_clips(self):
        return Clip.delete().execute()


    def save_clip(self, data):
        id = self.__get_uuidv4__()
        if data.get('parent') is not None:
            if Clip.select().where(Clip._id == data['parent']).count() < 1:
                raise ParentNotFoundException
            elif model_to_dict(Clip.select().where(Clip._id == data['parent']).get())['parent'] is not None:
                raise GrandchildException

        clip = Clip.create(
            _id=id,
            mimetype=data['mimetype'],
            creation_date=str(datetime.now()),
            last_modified=str(datetime.now()),
            data=data['data'],
            src_app=data.get('src_app'),
            filename=data.get('filename'),
            parent=data.get('parent')
        )
        clip.save()
        return model_to_dict(Clip.get(Clip._id==id))

    def get_clip_by_id(self, clip_id, preferred_types=None):
        q = Clip.select().where(Clip._id == clip_id)
        clip = None
        if(q.count() < 1):
            return clip
        else:
            clip = model_to_dict(q.get())
        if preferred_types and clip['mimetype'] is not preferred_types[0]:
            clip = self._find_best_match(clip, preferred_types)
        return clip

    def get_all_clips(self):
        # Exclude 'data' from fetch (would be too large)
        clipModels = Clip.select(
            Clip._id,
            Clip.mimetype,
            Clip.creation_date,
            Clip.src_app,
            Clip.filename,
            Clip.parent
        ).execute()
        results = []
        for model in clipModels:
            results.append(model_to_dict(model))
        return results

    def get_latest(self):
        q = Clip.select().order_by(Clip.creation_date.desc())
        if q.count() > 0:
            return model_to_dict(q.get())
        else:
            return None

    def delete_entry_by_id(self, clip_id):
        return Clip.delete().where((Clip._id==clip_id) | (Clip.parent==clip_id)).execute()

    def get_alternatives(self, clip_id):
        """
        Returns all siblings and the parent for clip_id
        as a list of dicts
        """
        q = Clip.select().where(Clip._id == clip_id)
        if q.count() < 1:
            return []
        else:
            clips = []
            clipsCursor = Clip.select(
                Clip._id,
                Clip.mimetype,
                Clip.creation_date,
                Clip.src_app,
                Clip.filename,
                Clip.parent
            ).where((Clip._id==clip_id) | (Clip.parent==clip_id))\
            .execute()
            for clipItem in clipsCursor:
                clips.append(model_to_dict(clipItem))
            return clips

    def update_clip(self, object_id, data):
        q = Clip.select().where(Clip._id == object_id)
        if q.count() < 1:
            return None
        else:
            clip = q.get()
            clip.data = data['data']
            clip.last_modified = str(datetime.now())
            clip.save()
            return model_to_dict(Clip.get_by_id(object_id))

