from .basehook import BaseHook


class ExampleHook(BaseHook):

    def do_work(self, obj, handle):
        if obj['mimetype'] in 'text/plain' and 'filename' not in obj:
            print(obj)
            new_object = {}
            new_object['parent'] = obj['_id']
            new_object['mimetype'] = 'text/xml'
            new_object['data'] = '<h1>' + obj['data'] + '</h1>'
            handle(new_object)
