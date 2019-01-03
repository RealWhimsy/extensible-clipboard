from mimetypes import guess_type

from flask import request

from flask_restful import abort, Resource


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
            data['mimetype'] = received_mt

        # Server received an object (text)
        else:
            data['content'] = request.form['clip']
            data['mimetype'] = request.form['mimetype']

        return data

    def get(self, clip_id=None):

        if clip_id is None:
            # Returns all visible clips
            clip = self.server.get_all_clips()
        else:
            clip = self.server.get_clip_by_id(clip_id)

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

        if clip_id is not None:
            return ({'error': 'Use PUT to update existing objects'},
                    405)

        data = self._get_data_from_request(request)

        new_item = self.server.save_in_database(data=data)
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
