from mimetypes import guess_type

class RequestParser():

    def get_data_from_request(self, request):
        data = {}
        """
        Server received a file
        This path might get deleted and user be forced
        To send files as base64 inside json-request
        """
        if 'file' in request.files:
            f = request.files['file']
            received_mt = f.mimetype
            guessed_mt = guess_type(f.filename)[0]

            if received_mt != guessed_mt:
                return None

            data['filename'] = f.filename
            data['data'] = f.stream.read()
            data['mimetype'] = guessed_mt

        # Server received an object (text)
        else:
            if request.headers.get('CONTENT_TYPE') in 'application/json':
                json = request.get_json()
                if json.get('data') and json.get('mimetype'):
                    data['data'] = json['data']
                    data['mimetype'] = json['mimetype']
                    data['src_url'] = json.get('src_url', 'n/a')
                    data['src_app'] = json.get('src_app', 'n/a')
        return data

