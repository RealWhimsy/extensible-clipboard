from .basehook import BaseHook


class ExampleHook(BaseHook):

    def do_work(self, obj=None):
        if obj['mimetype'] in 'text/plain' and 'filename' not in obj:
            obj['content'] = obj['content'] + ' modified'

