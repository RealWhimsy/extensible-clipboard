from hooks.pre_access.basepreaccesshook import BasePreAccessHook

class LocalhostOnlyHook(BasePreAccessHook):
    """
    Hook for restricting access to the local machine
    """

    def do_work(self, request):
        # Ignore other methods than delete
        if request.method is not 'DELETE':
            return True
        # Only allow local machine to do delete operations
        if request.remote_addr.startswith('127.0.0'):
            return True
        else:
            print("Unauthorized Delete from machine", request.remote_addr)
            return False
