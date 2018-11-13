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

    def post(self, clip_id=None):
        if clip_id is not None:
            response = make_response('Use PUT to update existing objects', 405)
            return response

        content = request.form['clip'] # Automatically sends 400 if no match
        new_item_id = self.server.save_in_database(content)
        self.server.emit_data(content)
        return {'saved': new_item_id}
        
