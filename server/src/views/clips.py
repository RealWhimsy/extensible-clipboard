import decorators as decorators
from views.base_clip import BaseClip
from flask import abort, current_app, jsonify, make_response, request, url_for

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

    @decorators.pre_hooks
    def delete(self):
        """
        Remove all clips from database, or by option just the ones older than a certain date.
        """
        current_app.delete_clips(request.args.get('before'))
        return "Clips Deleted Successfully", 200