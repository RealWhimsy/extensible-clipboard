from mimetypes import guess_type

class RequestParser():

    def get_data_from_request(self, request):
        data = {}
        # Server received a file
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
                data['data'] = json['data']
                data['mimetype'] = json['mimetype']

            else:
                data['data'] = request.form['data']
                data['mimetype'] = request.form['mimetype']

        return data

