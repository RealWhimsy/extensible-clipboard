from PyQt5 import QtCore

from hooks.hook_manager import HookManager
from exceptions import *


class FlaskQt(QtCore.QObject):
    """
    Wrapper around the Flask-server to be able to run it in a QThread.
    Also responsible for passing data to the database and the clipboard
    """

    data = QtCore.pyqtSignal(object)

    def __init__(self, flask_app, database):
        super(QtCore.QObject, self).__init__()
        self.app = flask_app
        self.db = database
        self.native_hooks = HookManager()

    def start_server(self):
        """
        Starts the Flask development-server. Cannot use autoreload
        because it runs in a seperate thread
        """
        self.app.run(debug=True, use_reloader=False)

    def emit_data(self, data):
        """
        Passes data to the Q-Application so it can put them into the clipboard
        :param data: The data (text, binary) received by the Resource
        """
        #self.native_hooks.call_hooks(data, self.db.save_clip)
        #print(data)
        #self.data.emit(data)

    def save_in_database(self, data, _id=None):
        """
        Saves the clip it got from the resource in the database and
        :param data: The data (text, binary) received by the Resource
        :param _id: If specified, the object with this id will be updated
        :return: the newly created entry
        """

        new_clip = {}
        try:
            if _id is None:
                new_clip = self.db.save_clip(data)
            else:
                new_clip = self.db.update_clip(_id, data)
            self.emit_data(new_clip)
        except (GrandchildException,
                ParentNotFoundException,
                SameMimetypeException) as e:
            new_clip['error'] = e

        return new_clip

    def get_clip_by_id(self, _id, preferred_type=None):
        """
        Queries the database for a clip with the specified uuid.
        :return: Json representation of the clip or None if no clip found
        """
        return self.db.get_clip_by_id(_id, preferred_type)

    def get_all_clips(self):
        """
        Returns all the clips from the database.
        TODO: When different users, only returns the clips a user may access
        :return: A json-array containing all clips
        """
        return self.db.get_all_clips()

    def get_latest_clip(self):
        return self.db.get_latest()

    def delete_entry_by_id(self, clip_id):
        """
        Deletes a clip from the collection.
        :return: Number of deleted items, can be 0 if no match found
        """
        return self.db.delete_entry_by_id(clip_id)

    def get_alternatives(self, clip_id):
        """
        Gets a Json-Array containg id and mimetype of all related
        (child, siblings or parent) entries of clip_id
        :returns: Said array or None, if clip_id not found in db
        """
        return self.db.get_alternatives(clip_id)
