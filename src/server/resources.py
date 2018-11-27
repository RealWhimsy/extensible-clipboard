from mimetypes import guess_type

from flask import abort, make_response, request

from flask_restful import Resource


class Clip(Resource):

    def __init__(self, **kwargs):
        self.server = kwargs['server']

    def get(self, clip_id=None):

        if clip_id is None:
            clip = self.server.get_all_clips()
        else:
            clip = self.server.get_clip_by_id(clip_id)

        if clip is None:
            return abort(404)

        return clip

    def handle_file_upload(self, f):
        pass

    def post(self, clip_id=None):

        if clip_id is not None:
            response = make_response('Use PUT to update existing objects', 405)
            return response

        # Server received a file
        if 'file' in request.files:
            f = request.files['file']
            
            received_mt = f.mimetype
            guessed_mt = guess_type(f.filename)[0]

            if received_mt != guessed_mt:
                return make_response(
                        'Request and file specify different mimetypes',
                        400)


            custom_file = {'filename': f.filename, 'content': f.stream.read()}
            new_item = self.server.save_in_database(custom_file)
            return new_item

        # Server received an object (text)
        else:
            content = request.form['clip']  # Automatically sends 400 if no match
            new_item = self.server.save_in_database(content)
            return new_item

