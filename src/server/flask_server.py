import requests
from uuid import UUID

from flask import Flask, url_for

from hooks.hook_manager import HookManager
from exceptions import (GrandchildException, ParentNotFoundException,
                        SameMimetypeException)


class FlaskServer(Flask):
    """
    Wrapper around the Flask-server to be able to run it in a QThread.
    Also responsible for passing data to the database and the clipboard
    """
    MAX_CONTENT_LENGTH = 15 * 1024 * 1024

    def __init__(self, app_name, database):
        super(FlaskServer, self).__init__(app_name)
        self.db = database
        self.native_hooks = HookManager()
        self.clipboards = []
        self.post_hooks = []
        self.current_clip = ''
        self.last_sender = ''

        self._build_recipients()
        self.config['MAX_CONTENT_LENGTH'] = self.MAX_CONTENT_LENGTH

    def start_server(self):
        """
        Starts the Flask development-server. Cannot use autoreload
        because it runs in a seperate thread
        """
        self.run(debug=False, use_reloader=False, host='0.0.0.0')

    def _build_recipients(self):
        result = self.db.get_recipients() or []
        self.post_hooks = []
        self.clipboards = []
        for r in result:
            if r['is_hook']:
                self.post_hooks.append(r)
            else:
                self.clipboards.append(r)
            r['error_count'] = 0

    def _send_failed(self, recipient):
        recipient['error_count'] += 1
        print('Could not send data to {}'.format(recipient['url']))
        print('Errors for {}: {}'.format(
            recipient['url'],
            recipient['error_count']
        ))

    def send_to_clipboards(self, data):
        """
        Passes data to the Q-Application so it can put them into the clipboard
        :param data: The data (text, binary) received by the Resource
        """
        """
        self.native_hooks.call_hooks(data, self.db.save_clip)
        """
        parent = data.get('parent')
        if parent and self.current_clip != parent:
            # Update was not to current clip
            return

        for c in self.clipboards:
            try:
                requests.post(c['url'], json=data, timeout=5)
            except:
                self._send_failed(c)

    def send_to_hooks(self, data):
        """
        Passes data to the Q-Application so it can put them into the clipboard
        :param data: The data (text, binary) received by the Resource
        """
        """
        self.native_hooks.call_hooks(data, self.db.save_clip)
        """
        _id = data.get('parent', data['_id'])
        for c in self.post_hooks:
            if c['is_hook']:
                try:
                    data['response_url'] = url_for(
                            'child_adder',
                            clip_id=_id, _external=True
                    )
                    requests.post(c['url'], json=data, timeout=5)
                except:
                    self._send_failed(c)

    def call_hooks(self, clip_id):
        clip = self.db.get_clip_by_id(clip_id)
        if clip:
            self.send_to_hooks(clip)

    def _get_last_sender_or_None(self, sender_id):
        try:
            return UUID(sender_id)
        except:
            return None

    def save_in_database(self, data, _id=None):
        """
        Saves the clip it got from the resource in the database and
        :param data: The data (text, binary) received by the Resource
        :param _id: If specified, the object with this id will be updated
        :return: the newly created entry
        """
        new_clip = {}
        self.last_sender = self._get_last_sender_or_None(
                data.pop('sender_id', '')
        )  # Prevents clipboard from uselessly receiving it's own data again
        try:
            if _id is None:
                new_clip = self.db.save_clip(data)
            else:
                new_clip = self.db.update_clip(_id, data)

            if new_clip:
                if 'parent' not in new_clip:
                    self.current_clip = new_clip['_id']
                response_url = url_for(
                        'child_adder',
                        clip_id=new_clip['_id'],
                        _external=True
                )
                new_clip['response_url'] = response_url.format(new_clip['_id'])
                self.send_to_clipboards(new_clip)

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

    def add_recipient(self, url, is_hook):
        r = self.db.add_recipient(url, is_hook)
        self._build_recipients()
        return r['_id']
