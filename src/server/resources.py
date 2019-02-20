from mimetypes import guess_type
import re

from flask import request, url_for
from flask import current_app as server
from flask.views import MethodView

from flask_restful import abort, Resource

from exceptions import (GrandchildException, ParentNotFoundException,
                        SameMimetypeException)
from parser import RequestParser


class BaseClip(MethodView):

    def __init__(self):
        self.parser = RequestParser()

    def _not_from_hook(self, request):
        if request and 'from_hook' in request:
            return False
        else:
            return True

    def check_for_errors(self, new_item):
        # Checks if any errors occured during lookup;
        # Works similar to passing of errors in Django
        if 'error' in new_item:
            error = new_item['error']
            if isinstance(error, ParentNotFoundException):
                return ({
                    'error': 'Parent specified by request not found on server'
                    },
                    412
                )
            elif isinstance(error, SameMimetypeException):
                return ({
                    'error': 'Entry has same mimetype specified as parent'},
                    422
                )
            elif isinstance(error, GrandchildException):
                return ({
                    'error': 'Can only create child for original entry'},
                    422
                )
            else:
                return None


class Clip(BaseClip):

    def get(self, clip_id=None):
        clip = None
        if request.url.endswith('/get_alternatives/'):
            clip = server.get_alternatives(clip_id)
        elif request.url.endswith('/latest/'):
            clip = server.get_latest_clip()
        else:
            preferred_type = None
            if request.accept_mimetypes.best != '*/*':  # Default value
                # Already sorted by Werkzeug
                preferred_type = request.accept_mimetypes

            clip = server.get_clip_by_id(clip_id, preferred_type)

        if clip is None:
            return {'error': 'No clip with specified id'} , 404

        return clip

    def put(self, clip_id=None):
        if clip_id is None:
            return ({'error': 'Please specifiy an existing object to update'},
                    405)

        data = self.parser.get_data_from_request(request)
        if not data:
            abort(400)
        clip = server.save_in_database(_id=clip_id, data=data, propagate=False)

        if clip is not None:
            return clip
        else:
            return {'error': 'No clip with specified id'} , 404

    def delete(self, clip_id=None):
        if clip_id is None:
            return ({'error': 'Please specifiy an existing object to delete'},
                    405)
        item = server.delete_entry_by_id(clip_id=clip_id)

        if item is not 0:
            return str(clip_id), 200
        else:
            return {'error': 'No clip with specified id'} , 404

    def post(self, clip_id=None):
        if request.url.endswith('/call_hooks'):
            server.call_hooks(clip_id)
            return '', 204
        else:
            return {'error': 'Please use put to update a clip'}, 400

class Clips(BaseClip):
    """
    Class responsible for handling a set of Clips
    """

    def post(self):
        """
        Create a new clip
        """
        data = self.parser.get_data_from_request(request)
        propagate = self._not_from_hook(data)
        if not data:
            abort(400)
        elif 'error' in data:
            return {'error': data['error']}, 413
        elif 'parent' in data:
            return {'error': 'Please send to url of intended parent'}, 422
        
        new_item = server.save_in_database(data=data, propagate=propagate)
        return new_item, 201

    def get(self):
        """
        Get all clips from the db
        """
        clip = server.get_all_clips()

        if clip is None:
            return {'error': 'No clip with specified id'} , 404

        return clip

class ChildClipAdder(BaseClip):
    """
    Responsible for adding a child to an existing clip
    """

    def post(self, clip_id=None):
        propagate = self._not_from_hook(request.get_json())
        data = self.parser.get_data_from_request(request)
        if not data:
            abort(400)

        data['parent'] = clip_id

        new_item = server.save_in_database(data=data, propagate=propagate)
        errors = self.check_for_errors(new_item)
        if errors:
            return errors
        else:
            return new_item, 201

class Recipient(Resource):

    def __init__(self, **kwargs):
        server = kwargs['server']
        self.pattern = re.compile(r'http://\w+')

    def _is_url(self, url):
        return self.pattern.match(url)

    def post(self):
        if request.headers.get('CONTENT_TYPE') not in 'application/json':
            return ('Please send aplication/json', 415)

        data = request.get_json()
        url = data['url']
        if self._is_url(url):
            is_hook = 'hook' in request.url
            _id = server.add_recipient(data['url'], is_hook)
            return ({
                '_id': _id,
                'response_url': url_for('clip', _external=True)}, 201)
        else:
            return ('Sent value for url was not an acceptable url', 422)

