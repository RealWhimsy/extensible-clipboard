from hooks.basehook import BaseHook

class LocalhostOnlyHook(BaseHook):
    """
    Hook for restricting access to the local machine
    """

    def do_work(self, request):
        remote = request.remote_addr
        if remote.startswith('127.0.0'):
            return True
        else:
            return False
