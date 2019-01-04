from .basehook import BaseHook

class SecondExample(BaseHook):

    def do_work(self, obj=None):
        print('SecondExample頑張ってるよ')
