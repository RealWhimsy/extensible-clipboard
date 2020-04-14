import decorators as decorators
from views.base_clip import BaseClip
from flask import abort, current_app, jsonify, make_response, request, url_for

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

    def get_alternatives(self, clip_id):
        pass

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
        item = current_app.delete_clip_by_id(clip_id=clip_id)

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