import re

from flask import abort, current_app, jsonify, make_response, request, url_for
from flask.views import MethodView

import decorators as decorators
from exceptions import (GrandchildException, ParentNotFoundException,
                        SameMimetypeException)
from parser import RequestParser

from hooks.hook_manager import HookManager

"""
The classes in this file act as the views for Flask and expose the application
to the network. Extension of the API should happen here and new classes
introduced should inherit from BaseClip.
Here, the concept of Clip is introduced used throughout the whole project.
A clip is the representation of an object in the clipboard. Apart from its
data it must contain a mimetype. Several other pieces of data can be sent
with custom HTTP-headers. Please refer to parser.py for a specification
of those.
Apart from Recipient, the classes were added to split the logic of processing
the incoming data into different methods as to make the code more readable.
"""


class BaseClip(MethodView):
    """
    This Method view acts a parent-class for all following classes
    and provides several utility-methods for them like checking
    the objects received from  the database for errors and returning
    the correct error-code.
    It is not intended to act as a view like its subclasses and has no methods
    implemented for processing requests, this should be done by subclasses.
    """

    def __init__(self):
        self.parser = RequestParser()
        self.pre_hooks = HookManager()

    def _load_pre_hooks(self):
        return []

    def check_for_errors(self, new_item):
        """
        Checks if any errors occured during adding of child and
        returns directly aborts the request with an error code
        Works similar to passing of errors in Django
        """
        if 'error' in new_item:
            error = new_item['error']
            if isinstance(error, ParentNotFoundException):
                return jsonify(error='Parent specified by request not found '
                               + 'on server.'), 412
            elif isinstance(error, SameMimetypeException):
                return jsonify(error='Entry has same mimetype specified '
                               + 'as parent'), 422
            elif isinstance(error, GrandchildException):
                return jsonify(error='Can only create child for '
                               + 'original entry'), 422
            else:
                return None

    def set_headers(self, res, clip):
        """
        Iterates over all items of a clip and puts them into custom
        HTTP-headers prefixed with X-C2-
        Also sets the Content-Disposition- and Location-header as needed.
        """
        clip['mimetype'] = clip['mimetype'] + "; charset=utf8"
        res.headers['Content-Type'] = clip.pop('mimetype')
        for key, value in clip.items():
            res.headers['X-C2-{}'.format(key)] = value
        if 'filename' in clip:
            res.headers['Content-Disposition'] = \
                'inline; filename={}'.format(clip['filename'])
        res.headers['Location'] = url_for('clip_details',
                                          clip_id=clip['_id'],
                                          _external=True)


class Clip(BaseClip):
    """
    This class deals with operations on a single clip such as changing
    its contents or getting alternative representations of the same data.
    """

    @decorators.pre_hooks
    def get(self, clip_id=None):
        clip = None
        # gets the siblings and parent or children of a clip
        if request.url.endswith('/alternatives/'):
            clips = current_app.get_alternatives(clip_id)
            for c in clips:
                c['url'] = url_for('clip', clip_id=c['_id'], _external=True)
            return jsonify(clips), 300
        # returns the last added parent-clip
        elif request.url.endswith('/latest/'):
            clip = current_app.get_latest_clip()
        # returns the spcified clip or a sibling according to the CN
        else:
            preferred_type = None
            if request.accept_mimetypes.best != '*/*':  # Default value
                # Already sorted by Werkzeug
                preferred_type = request.accept_mimetypes
            clip = current_app.get_clip_by_id(clip_id, preferred_type)

        if clip is None:
            return jsonify(error='No clip with specified id'), 404
        res = make_response(clip.pop('data'), 200)
        self.set_headers(res, clip)
        return res

    @decorators.pre_hooks
    def put(self, clip_id=None):
        """
        Updates the clip specified by clip_id
        """
        if clip_id is None:
            return jsonify(
                    error='Please specify an existing object to update'), 405
        data = self.parser.get_data_from_request(request)
        if not data:
            return jsonify(error='Could not parse data'), 400
        clip = current_app.save_in_database(_id=clip_id,
                                            data=data,)

        if clip is not None:
            res = make_response(clip.pop('data'), 200)
            self.set_headers(res, clip)
            return res
        else:
            return jsonify(error='No clip with specified id'), 404

    @decorators.pre_hooks
    def delete(self, clip_id=None):
        """
        Deletes the clip specified by clip_id. When a parent is deleted,
        all its children will be removed also.
        """
        if clip_id is None:
            return jsonify(
                    error='Please specify an existing object to delete'), 404
        item = current_app.delete_entry_by_id(clip_id=clip_id)

        if item is not 0:
            return jsonify(_id=clip_id), 200
        else:
            return jsonify(error='No clip with specified id'), 404

    @decorators.pre_hooks
    def post(self, clip_id=None):
        if request.url.endswith('/hooks/call'):
            current_app.call_hooks(clip_id)
            return '', 204
        else:
            return jsonify(error='Please use put to update a clip'), 400


class Clips(BaseClip):
    """
    Class responsible for handling a set of Clips
    """

    @decorators.pre_hooks
    def post(self):
        """
        Create a new clip
        """
        data = self.parser.get_data_from_request(request)
        if not data:
            return jsonify(error='Unable to parse data'), 400
        elif 'error' in data:
            return jsonify(error=data['error']), 413
        elif 'parent' in data:
            return jsonify(error='Please send to url of intended parent'), 422

        new_item = current_app.save_in_database(data=data)
        res = make_response(new_item.pop('data'), 201)
        self.set_headers(res, new_item)
        return res

    @decorators.pre_hooks
    def get(self):
        """
        Get all clips from the db. This will not get their data to reduce
        the amount of data sent to the clients. To get the data, one has
        to request the clip directly by its url ( /clip/{CLIP_ID}/
        """
        clips = current_app.get_all_clips()

        if clips is None:
            return jsonify(error='No clips saved yet'), 404
        else:
            return jsonify(clips), 200


class ChildClipAdder(BaseClip):
    """
    Responsible for adding a child to an existing clip.
    Introduced to simplify the flow of the application.
    """

    @decorators.pre_hooks
    def post(self, clip_id=None):
        data = self.parser.get_data_from_request(request)
        if not data:
            abort(400)

        data['parent'] = clip_id
        new_item = current_app.save_in_database(data=data)
        errors = self.check_for_errors(new_item)
        if errors:
            return errors
        else:
            res = make_response(new_item.pop('data'), 201)
            self.set_headers(res, new_item)
            return res


class Recipient(MethodView):
    """
    Adds a recipient to the database. A recipient represents another webserver
    that is interested in the data saved on THIS server. There are two kinds
    of recipeints: remote clipboards and webhook. A clipboard will get
    virtually and data saved on the server while a webhook may subscribe to
    specific mimetypes it is interested in.
    """

    def __init__(self):
        self.parser = RequestParser()
        self.pre_hooks = HookManager()

    def is_url(self, url):
        """
        Sanity-check to see if the data sent by the recipient seems to be
        an URL, might be imporoved
        """
        return re.match(r'^http://', url)

    @decorators.pre_hooks
    def post(self):
        """
        Adds another recipient. Depending on the URL, the request was sent
        to, it will be treated as a webhook or a clipboard.
        """
        if request.headers.get('CONTENT-TYPE') not in 'application/json':
            return jsonify(error='Please send aplication/json'), 415

        data = request.get_json()
        if 'url' not in data:
            return jsonify(error='No url specified'), 400
        url = data['url']
        if self.is_url(url):
            is_hook = 'hooks' in request.url
            _id = current_app.add_recipient(
                    url,
                    is_hook,
                    data.get('subscribed_types', None))
            # TODO? clip to clips
            return jsonify(_id=_id,
                           response_url=url_for('clip', _external=True)), 201
        else:
            return ('Sent value for url was not an acceptable url', 422)
