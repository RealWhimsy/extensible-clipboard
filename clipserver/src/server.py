import requests
from uuid import UUID

from flask import Flask, url_for

from exceptions import (GrandchildException, ParentNotFoundException,
                        SameMimetypeException)

from views.clips import Clips
from views.clip import Clip
from views.recipient import Recipient
from views.child_clip import ChildClip

class Server(Flask):
    """
    Wrapper around the Flask-server adding custom logic.
    Also responsible for passing data to the database and to send
    newly added data to the webhooks or remote clipboards registered to
    the server.
    """

    # Bigger requests will be discarded. Currently 15MB
    MAX_CONTENT_LENGTH = 15 * 1024 * 1024

    def __init__(self, app_name, database, port=5000):
        super(Server, self).__init__(app_name)
        self.db = database
        self.port = port
        self.clipboards = []
        self.post_hooks = []
        self.current_clip = ''
        self.last_sender = ''

        self._build_recipients()
        self.config['MAX_CONTENT_LENGTH'] = self.MAX_CONTENT_LENGTH

        self.__init_routing()


    def __init_routing(self):
        """
        Since we use class-based routing for the server, we cannot utilize
        the decorators provided by Flask and instead have to plug in the
        routes manually
        """
        clip_view = Clip.as_view('clip')  # 'clip' can be used in url_for
        clip_details = Clip.as_view('clip_details')
        clip_list_view = Clips.as_view('clip_list')
        child_add_view = ChildClip.as_view('child_adder')
        recipient_view = Recipient.as_view('recipient')

        self.add_url_rule('/clips/',
                                       view_func=clip_list_view,
                                       methods=['GET', 'POST', 'DELETE'])
        self.add_url_rule('/clips/latest/',
                                       view_func=clip_view,
                                       methods=['GET'])
        self.add_url_rule('/clips/<uuid:clip_id>/',
                                       view_func=clip_details,
                                       methods=['GET', 'DELETE',
                                                'PUT', ])
        self.add_url_rule('/clips/<uuid:clip_id>/'
                                       + 'alternatives/',
                                       view_func=clip_view,
                                       methods=['GET'])
        self.add_url_rule('/clips/<uuid:clip_id>/hooks/call',
                                       view_func=clip_view,
                                       methods=['POST'])
        self.add_url_rule('/clips/<uuid:clip_id>/children',
                                       view_func=child_add_view,
                                       methods=['POST'])
        self.add_url_rule('/clipboards/register',
                                       view_func=recipient_view,
                                       methods=['POST'])
        self.add_url_rule('/hooks/register',
                                       view_func=recipient_view,
                                       methods=['POST'])


    def start(self):
        """
        Starts the Flask development-server. Cannot use autoreload
        because it runs in a seperate thread
        """
        self.run(debug=False, use_reloader=False,
                 host='0.0.0.0', port=self.port)

    def _build_recipients(self):
        """
        Refreshes the lists of all recipients for data on the server,
        webhooks and clipboards
        """
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
        """
        Called when sending data to a recipient failed. Currently ony counts
        errors and prints them. Could be used to remove the recipient after
        a certain number of consecutive failures.
        """
        recipient['error_count'] += 1
        print('Could not send data to {}'.format(recipient['url']))
        print('Errors for {}: {}'.format(
            recipient['url'],
            recipient['error_count']
        ))

    def send_to_clipboards(self, data, force_propagation=False):
        """
        Passes data to the recipient clipboards
        :param data: The data (text, binary) received by the Resource
        """
        parent = data.get('parent')

        if parent and self.current_clip != parent:
            # Update was not to current clip
            return

        for c in self.clipboards:
            if force_propagation or self.last_sender != c['_id']:
                try:
                    send_data = data.get('data')
                    response_url = url_for('child_adder',
                                           clip_id=data['_id'],
                                           _external=True)
                    headers = {'X-C2-response_url': response_url}
                    headers['Content-Type'] = data.get('mimetype')
                    for key, value in data.items():
                        if key != 'data' and key != 'mimetype':
                            headers['X-C2-{}'.format(key)] = value

                    requests.post(c['url'],
                                  data=send_data,
                                  headers=headers,
                                  timeout=5)

                except Exception as e:
                    print(e)
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
            types = c['preferred_types']
            if data['mimetype'] in types or types == ['*/*']:
                try:
                    send_data = data.pop('data')
                    # URL used for adding a child to the entry
                    response_url = url_for('child_adder',
                                           clip_id=_id,
                                           _external=True)
                    headers = {'X-C2-response_url': response_url}
                    headers['Content-Type'] = data.pop('mimetype')
                    for key, value in data.items():
                        headers['X-C2-{}'.format(key)] = value
                    requests.post(c['url'],
                                  data=send_data,
                                  headers=headers,
                                  timeout=5)
                except Exception as e:
                    print(e)
                    self._send_failed(c)

    def call_hooks(self, clip_id):
        """
        Gets a clip and sends it to the post hooks
        """
        clip = self.db.__get_clip_by_id__(clip_id)
        if clip:
            self.send_to_hooks(clip)

    def _get_last_sender_or_None(self, sender_id):
        """
        Creates a UUID to identify the client which sent the last clip.
        Returns None if sender_id is not a parsable UUID-string
        """
        try:
            return UUID(sender_id)
        except Exception as e:
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
        force_propagation = data.pop('from_hook', False)
        try:
            if _id is None:
                new_clip = self.db.save_clip(data)
            else:
                new_clip = self.db.update_clip(_id, data)

            # Creation successful
            if new_clip:
                if new_clip['parent'] is None:
                    self.current_clip = new_clip['_id']
                response_url = url_for(
                        'child_adder',
                        clip_id=new_clip['_id'],
                        _external=True
                )
                # this is a quick fix for errors related to #25
                new_clip['_id'] = str(new_clip['_id'])
                new_clip['response_url'] = response_url.format(new_clip['_id'])
                self.send_to_clipboards(new_clip, force_propagation)

        except (GrandchildException,
                ParentNotFoundException,
                SameMimetypeException) as e:
            new_clip['error'] = e

        return new_clip

    def get_clip_by_id(self, _id, preferred_type=None):

        return self.db.__get_clip_by_id__(_id, preferred_type)

    def get_all_clips(self):
        """
        Returns all the clips from the database.
        TODO: When different users, only returns the clips a user may access
        :return: A json-array containing all clips
        """
        return self.db.get_all_clips()

    def delete_clip_by_id(self, clip_id):
        """
        Deletes a clip from the collection.
        :return: Number of deleted items, can be 0 if no match found
        """
        return self.db.delete_clip_by_id(clip_id)

    def delete_clips(self, before_date=None):
        if before_date is None :
            return self.db.delete_all_clips()
        else:
            return self.db.delete_clips_before(before_date)

    def get_alternatives(self, clip_id):
        return self.db.__get_alternatives__(clip_id)

    def add_recipient(self, url, is_hook, subscribed_types):
        """
        Adds a recipient (webhook or clipboard to the database)
        with the specified options
        :return: The UUID of the created recipient as a UUID-string
        """
        r = self.db.add_recipient(url, is_hook, subscribed_types)
        self._build_recipients()
        return r['_id']
