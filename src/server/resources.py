from mimetypes import guess_type

from flask import request

from flask_restful import abort, Resource

from exceptions import *


class Clip(Resource):

    def __init__(self, **kwargs):
        self.server = kwargs['server']

    def _get_data_from_request(self, request):
        # Server received a file
        data = {}
        if 'file' in request.files:
            f = request.files['file']
            received_mt = f.mimetype
            guessed_mt = guess_type(f.filename)[0]

            if received_mt != guessed_mt:
                return abort(400)

            data['filename'] = f.filename
            data['content'] = f.stream.read()
            data['mimetype'] = guessed_mt

        # Server received an object (text)
        else:
            if request.headers.get('CONTENT_TYPE') in 'application/json':
                json = request.get_json()
                data['content'] = json['clip']
                data['mimetype'] = json['mimetype']
                
            else:
                data['content'] = request.form['clip']
                data['mimetype'] = request.form['mimetype']

        return data

    def get(self, clip_id=None):

        if clip_id is None:
            # Returns all visible clips
            clip = self.server.get_all_clips()
        else:
            preferred_type = None
            if request.accept_mimetypes.best != '*/*':  # Default value
                preferred_type = request.accept_mimetypes # Already sorted by Werkzeug

            clip = self.server.get_clip_by_id(clip_id, preferred_type)

        if clip is None:
            return abort(404)

        return clip

    def put(self, clip_id=None):
        if clip_id is None:
            return ({'error': 'Please specifiy an existing object to update'},
                    405)

        data = self._get_data_from_request(request)
        clip = self.server.save_in_database(_id=clip_id, data=data)

        if clip is not None:
            return clip
        else:
            return abort(404)

    def post(self, clip_id=None):

        if clip_id is not None and not request.url.endswith('add_child'):
            return ({'error': 'Use PUT to update existing objects'},
                    405)

        data = self._get_data_from_request(request)

        if request.url.endswith('add_child'):
            data['parent'] = clip_id

        new_item = self.server.save_in_database(data=data)

        # Checks if any errors occured during lookup;
        # Works similar to passing of errors in Django
        if 'error' in new_item:
            error = new_item['error']
            if type(error) is ParentNotFoundException:
                return ({
                    'error': 'Parent specified by request not found on server'},
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

        return new_item, 201

    def delete(self, clip_id=None):
        if clip_id is None:
            return ({'error': 'Please specifiy an existing object to delete'},
                    405)
        item = self.server.delete_entry_by_id(clip_id=clip_id)

        if item is not 0:
            return ('', 204)
        else:
            return abort(404)
