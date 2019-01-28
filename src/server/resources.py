from json import dumps
from mimetypes import guess_type
import re

from flask import request, url_for

from flask_restful import abort, Resource

from src.server.exceptions import *


class Clip(Resource):

    def __init__(self, **kwargs):
        self.server = kwargs['server']

    def _get_data_from_request(self, request):
        data = {}
        # Server received a file
        if 'file' in request.files:
            f = request.files['file']
            received_mt = f.mimetype
            guessed_mt = guess_type(f.filename)[0]

            if received_mt != guessed_mt:
                abort(400)

            data['filename'] = f.filename
            data['data'] = f.stream.read()
            data['mimetype'] = guessed_mt

        # Server received an object (text)
        else:
            if request.headers.get('CONTENT_TYPE') in 'application/json':
                json = request.get_json()
                data['data'] = json['data']
                data['mimetype'] = json['mimetype']

            else:
                data['data'] = request.form['data']
                data['mimetype'] = request.form['mimetype']

        return data

    def _not_from_hook(self, request):
        if request and 'from_hook' in request:
            return False
        else:
            return True

    def get(self, clip_id=None):
        clip = None
        if request.url.endswith('/clip/'):
            clip = self.server.get_all_clips()
        elif request.url.endswith('/get_alternatives/'):
            clip = self.server.get_alternatives(clip_id)
        elif request.url.endswith('/latest/'):
            clip = self.server.get_latest_clip()
        else:
            preferred_type = None
            if request.accept_mimetypes.best != '*/*':  # Default value
                # Already sorted by Werkzeug
                preferred_type = request.accept_mimetypes

            clip = self.server.get_clip_by_id(clip_id, preferred_type)

        if clip is None:
            return 'No clip with specified id' , 404

        return dumps(clip)

    def put(self, clip_id=None):
        if clip_id is None:
            return ({'error': 'Please specifiy an existing object to update'},
                    405)

        data = self._get_data_from_request(request)
        clip = self.server.save_in_database(_id=clip_id, data=data, propagate=False)

        if clip is not None:
            return dumps(clip)
        else:
            return 'No clip with specified id', 404

    def post(self, clip_id=None):

        if clip_id is not None and not request.url.endswith('add_child'):
            return ({'error': 'Use PUT to update existing objects'},
                    405)

        propagate = self._not_from_hook(request.get_json())
        data = self._get_data_from_request(request)

        if request.url.endswith('add_child'):
            data['parent'] = clip_id

        new_item = self.server.save_in_database(data=data, propagate=propagate)

        # Checks if any errors occured during lookup;
        # Works similar to passing of errors in Django
        if 'error' in new_item:
            error = new_item['error']
            if type(error) is ParentNotFoundException:
                return ({
                    'error': 'Parent specified by request not found on server'
                    },
                    412
                )
            elif type(error) is SameMimetypeException:
                return ({
                    'error': 'Entry has same mimetype specified as parent'},
                    422
                )
            elif type(error) is GrandchildException:
                return ({
                    'error': 'Can only create child for original entry'},
                    422
                )

        return dumps(new_item), 201

    def delete(self, clip_id=None):
        if clip_id is None:
            return ({'error': 'Please specifiy an existing object to delete'},
                    405)
        item = self.server.delete_entry_by_id(clip_id=clip_id)

        if item is not 0:
            return ('', 204)
        else:
            return 'No clip with specified id', 404


class Recipient(Resource):

    def __init__(self, **kwargs):
        self.server = kwargs['server']
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
            _id = self.server.add_recipient(data['url'], is_hook)
            #if _id >= 0:
            return ({'response_url': url_for('clip', _external=True)}, 201)
            #else:
            #    return ('', 204)
        else:
            return ('Sent value for url was not an acceptable url', 422)

