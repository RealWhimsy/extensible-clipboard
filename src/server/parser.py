import re
import requests

from flask_server import FlaskServer as server


class RequestParser():

    ACCEPTED_HEADERS = ['X-C2-src_url', 'X-C2-src_app', 'X-C2-sender_id']

    def file_too_large(self, url):
        r = requests.head(url)
        cl = r.headers.get('content-length')
        if cl and int(cl) <= server.MAX_CONTENT_LENGTH:
            return False
        else:
            return True

    def get_filename_from_url(self, url):
        end = url.rsplit('/', 1)[-1]
        if self.filename_pattern.match(end):
            return end
        else:
            return None

    def get_filename_from_cd(self, cd):
        """
        Get filename from content-disposition
        """
        if not cd:
            return None
        fname = re.findall('filename=(.+)', cd)
        if len(fname) == 0:
            return None
        return fname[0]

    def download_file(self, url):
        # https://www.codementor.io/aviaryan/downloading-files-from-urls-in-python-77q3bs0un
        if self.file_too_large(url):
            return None

        try:
            r = requests.get(url, allow_redirects=True)
        except:
            print('Error during download')
            return None
        if int(r.headers.get('content-length')) >= server.MAX_CONTENT_LENGTH:
            # HEAD to url war not indicating large file
            return None
        file_content = r.content
        filename = self.get_filename_from_url(url)
        if not filename:
            filename = self.get_filename_from_cd(
                    r.headers.get('content-disposition'))
        mimetype = r.headers.get('content-type')

        return (file_content, filename, mimetype)

    def get_data_from_request(self, request):
        data = {}

        # Server received a file
        data['mimetype'] = request.headers['Content-Type']
        if 'file' in request.files:
            f = request.files['file']
            data['filename'] = f.filename
            data['data'] = f.stream.read()

        # Server received an object (text)
        else:
            data['data'] = request.get_data()
            if 'X-C2-download_request' in request.headers:
                _file = self.download_file(data['data'].decode())
                if _file:
                    data['filename'] = _file[1]
                    data['data'] = _file[0]
                    data['mimetype'] = _file[2]
                else:
                    return {'error': 'Error during download. \
                            Check if file is accessible and smaller than 15MB'}

            for h in self.ACCEPTED_HEADERS:
                if h in request.headers:
                    data[h[5:]] = request.headers[h]
        try:
            data['data'] = data['data'].decode()
        except:
            pass
        return data

    def __init__(self):
        self.filename_pattern = re.compile('^.*\..*$')
