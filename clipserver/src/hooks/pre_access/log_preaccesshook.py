from hooks.pre_access.basepreaccesshook import BasePreAccessHook


class LogPreaccessHook(BasePreAccessHook):
    """
    Hook for restricting access to the local machine
    """

    def do_work(self, request):
        print("Howdy from preaccess")
        return True