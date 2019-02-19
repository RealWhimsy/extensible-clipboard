import re
import requests

from mimetypes import guess_type

from flask_server import FlaskServer as server

class RequestParser():

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
            filename = self.get_filename_from_cd(r.headers.get('content-disposition'))
        mimetype = r.headers.get('content-type')

        return (file_content, filename, mimetype)


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
                    if json.pop('download_request', None):
                        _file = self.download_file(str(json['data']))
                        if _file:
                            data['filename'] = _file[1]
                            json['mimetype'] = _file[2]
                            json['data'] = _file[0]
                        else:
                            return {'error': 'Error during download. Check if file is accessible and smaller than 15MB'}
                    data['data'] = json['data']
                    data['mimetype'] = json['mimetype']
                    data['src_url'] = json.get('src_url', 'n/a')
                    data['src_app'] = json.get('src_app', 'n/a')
                    #if 'sender_id' in json and 'from_hook' not in json:
                    if 'sender_id' in json:
                        data['sender_id'] = json['sender_id']

        return data

    def __init__(self):
        self.filename_pattern = re.compile('^.*\..*$')
