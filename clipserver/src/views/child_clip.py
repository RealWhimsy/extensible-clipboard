import decorators as decorators
from exceptions import GrandchildException, ParentNotFoundException, SameMimetypeException
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
        try:
            new_item = current_app.db.save_clip(data=data)
            current_app.emitter.send_to_clipboards(
                new_item,
                data.pop('from_hook', False),
                data.pop('sender_id', ''))
            res = make_response(new_item.pop('data'), 201)
            self.set_headers(res, new_item)
            return res
        except (GrandchildException,
                ParentNotFoundException,
                SameMimetypeException) as e:
            return self.resolve_error(new_item)