from .basehook import BaseHook

class ExampleHook(BaseHook):

    def do_work(self, obj=None):
        print('example1_hook doing gods work')

    def __init__(self):
        print('hello from example1_hook')
