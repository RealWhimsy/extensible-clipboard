from .base_hook import BaseHook

class SecondExample(BaseHook):

    def do_work(self, obj=None):
        print('SecondExample is working')
