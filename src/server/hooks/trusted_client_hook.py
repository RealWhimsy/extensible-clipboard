from .basehook import BaseHook


class ClientIsTrustedHook(BaseHook):
    trusted_addresses = [
        '132.199.132.37'
    ]
    """
    Demo hook for allowing connections from two demo devices (my phone and a raspberry Pi) 
    """
    def do_work(self, request):
        remote = request.remote_addr
        print(remote)
        if remote in self.trusted_addresses:
            return True
        else:
            return False
