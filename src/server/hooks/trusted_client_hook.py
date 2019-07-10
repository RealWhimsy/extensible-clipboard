from .basehook import BaseHook


class ClientIsTrustedHook(BaseHook):
    trusted_addresses = [
        '132.199.132.37',
        '132.199.182.211'
    ]
    """
    Demo hook for allowing connections from two demo devices (my phone and a raspberry Pi) 
    """
    def do_work(self, request):
        remote = request.remote_addr
        print(remote)
        if (remote in self.trusted_addresses) or remote.startswith('192.') or remote.startswith('127.'):
            return True
        else:
            return False
