from peewee import \
    Model, \
    DateField, \
    PrimaryKeyField, \
    ForeignKeyField, \
    CharField, \
    BlobField, \
    IntegerField, \
    SqliteDatabase, \
    BooleanField, \
    Proxy
import os
path = os.path.expanduser('~/clip_collection.db')
db = SqliteDatabase(path)

class BaseModel(Model):
    class Meta:
        database = db


class Clip(BaseModel):
    _id = CharField(primary_key=True)
    creation_date = CharField()
    last_modified = CharField()
    mimetype = CharField()
    data = BlobField()
    src_app = CharField(null=True)
    filename = CharField(null=True)
    parent = CharField(null=True)


class Recipient(BaseModel):
    _id = CharField(primary_key=True)
    url = CharField()
    is_hook = BooleanField()


class PreferredTypes(BaseModel):
    parent = ForeignKeyField(Recipient, backref="preferred_types")
    type = CharField()