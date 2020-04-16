import requests
from uuid import UUID

from flask import Flask, url_for

from event_emitter import ClipEventEmitter
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
        self.emitter = ClipEventEmitter(database)


        # TODO: these instance variables belong somewhere else
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

    # TODO: take care of this
    def _build_recipients(self):
        self.emitter.invalidate_listeners()

    def call_hooks(self, clip_id):
        """
        Gets a clip and sends it to the post hooks
        """
        clip = self.db.get_clip_by_id(clip_id)
        if clip:
            self.send_to_hooks(clip)

    def _get_last_sender_or_None(self, sender_id):
        """
        Creates a UUID to identify the client which sent the last clip.
        Returns None if sender_id is not a parsable UUID-string

        TODO: this method is arguable too
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

        TODO: this is the most influential refactoring site... it strongly depends on instance variables,
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

