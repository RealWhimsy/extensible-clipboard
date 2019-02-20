from urllib import parse

from flask import abort, current_app, jsonify, make_response, request, url_for
from flask.views import MethodView

from exceptions import (GrandchildException, ParentNotFoundException,
                        SameMimetypeException)
from parser import RequestParser


class BaseClip(MethodView):

    def __init__(self):
        self.parser = RequestParser()

    def check_for_errors(self, new_item):
        # Checks if any errors occured during lookup;
        # Works similar to passing of errors in Django
        if 'error' in new_item:
            error = new_item['error']
            if isinstance(error, ParentNotFoundException):
                return ({
                    'error': 'Parent specified by request not found on current_app.'
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

    def is_base_64_encoded(self, headers):
        if 'Content-Encoding' not in request.headers:
            return False
        elif 'base64' == request.headers['Content-Encoding']:
            return True
        else:
            raise ValueError

    def set_headers(self, res, clip):
        res.headers['Content-Type'] = clip.pop('mimetype')
        for key, value in clip.items():
            res.headers['X-C2-{}'.format(key)] = value


class Clip(BaseClip):

    def get(self, clip_id=None):
        clip = None
        if request.url.endswith('/get_alternatives/'):
            clip = current_app.get_alternatives(clip_id)
        elif request.url.endswith('/latest/'):
            clip = current_app.get_latest_clip()
        else:
            preferred_type = None
            if request.accept_mimetypes.best != '*/*':  # Default value
                # Already sorted by Werkzeug
                preferred_type = request.accept_mimetypes

            clip = current_app.get_clip_by_id(clip_id, preferred_type)

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
        clip = current_app.save_in_database(_id=clip_id, data=data, propagate=False)

        if clip is not None:
            return clip
        else:
            return {'error': 'No clip with specified id'} , 404

    def delete(self, clip_id=None):
        if clip_id is None:
            return ({'error': 'Please specifiy an existing object to delete'},
                    405)
        item = current_app.delete_entry_by_id(clip_id=clip_id)

        if item is not 0:
            return str(clip_id), 200
        else:
            return {'error': 'No clip with specified id'} , 404

    def post(self, clip_id=None):
        if request.url.endswith('/call_hooks'):
            current_app.call_hooks(clip_id)
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
        try:
            decode = self.is_base_64_encoded(request.headers)
        except ValueError:
            return jsonify(error='Content-Encoding must only \
                    be base64 or none'), 422
        data = self.parser.get_data_from_request(request, decode)
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

    def get(self):
        """
        Get all clips from the db
        """
        clip = current_app.get_all_clips()

        if clip is None:
            return jsonify(error='No clips saved yet'), 404
        else:
            return clip


class ChildClipAdder(BaseClip):
    """
    Responsible for adding a child to an existing clip
    """

    def post(self, clip_id=None):
        try:
            decode = self.is_base_64_encoded(request.headers)
        except ValueError:
            return jsonify(error='Content-Encoding must only \
                    be base64 or none'), 422
        data = self.parser.get_data_from_request(request, decode)
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


class Recipient(MethodView):

    def post(self):
        if request.headers.get('CONTENT-TYPE') not in 'application/json':
            return jsonify(error='Please send aplication/json'), 415

        data = request.get_json()
        if 'url' not in data:
            return jsonify(error='No url specified'), 400
        url = data['url']
        try:
            parse.urlparse(url)
            is_hook = 'hook' in request.url
            _id = current_app.add_recipient(data['url'], is_hook)
            return jsonify(_id=_id,
                           response_url=url_for('clip', _external=True)), 201
        except ValueError:
            return ('Sent value for url was not an acceptable url', 422)

