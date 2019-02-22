from .basehook import BaseHook


class UserIsLocalHook(BaseHook):
    """
    Small example hook that returns True if the request
    came from a local IP, one starting with '127.'
    """

    def do_work(self, request):
        remote = request.remote_addr
        return remote.startswith('127.')
