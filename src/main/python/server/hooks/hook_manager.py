from importlib import import_module, machinery
from os import listdir
import os
from server.hooks.basehook import BaseHook
from server.hooks.trusted_client_hook import ClientIsTrustedHook


class HookManager:

    def _create_hooks(self):

        # Rebuild hooks if method is called manually fore some reason
        if self.hooks:
            self.hooks = []
        """
        TODO: packaging the application did break the dynamic hook system by Matthias
        - A dynamic hook system could be implemented using context resources, but this would require a bigger refactor
        """
        self.hooks.append(ClientIsTrustedHook())
        """
        files = listdir(os.path.dirname(__file__))
        # Remove all files not ending on _hook.py
        hook_files = [f for f in files if f.endswith('_hook.py')]
        for file_name in hook_files:
            module = import_module('server.hooks.' + file_name[:-3])
            members = dir(module)
            for m in members:
                # Do not even check underscored stuff and Parent class
                if not m.startswith('_') and 'BaseHook'not in m:
                    hook = getattr(module, m)()  # instanciate found class
                    if isinstance(hook, BaseHook):  # is child of BaseHook
                        print(hook)
                        self.hooks.append(hook)
        """

    def call_hooks(self, request):
        for h in self.hooks:
            print("Call hook", h)
            if not h.do_work(request):
                return False
        return True

    def __init__(self):
        self.hooks = []
        self._create_hooks()
