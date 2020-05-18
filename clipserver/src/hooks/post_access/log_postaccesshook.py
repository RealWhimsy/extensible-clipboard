from hooks.post_access.basepostaccesshook import BasePostAccessHook


class LogHook(BasePostAccessHook):

    def do_work(self, response):
        print("See ya soon! Yours, Postaccess")
        return
