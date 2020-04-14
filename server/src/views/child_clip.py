import decorators as decorators
from views.base_clip import BaseClip
from flask import abort, current_app, jsonify, make_response, request, url_for

class ChildClip(BaseClip):
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