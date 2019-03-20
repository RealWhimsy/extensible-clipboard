from .basehook import BaseHook


class UserIsLocalHook(BaseHook):
    """
    Small example hook that returns True if the request
    came from a local IP, one starting with '127.'
    """

    def do_work(self, request):
        remote = request.remote_addr
        if remote.startswith('192.') or remote.startswith('127.'):
            return True
        else:
            return False
