from importlib import import_module
from os import listdir

from .basehook import BaseHook


class HookManager:

    def _create_hooks(self):
        # Rebuild hooks if method is called manually fore some reason
        if self.hooks:
            self.hooks = []

        files = listdir('hooks/')
        # Remove all files not ending on _hook.py
        hook_files = [f for f in files if f.endswith('_hook.py')]

        for file_name in hook_files:
            module = import_module('hooks.' + file_name[:-3])
            members = dir(module)
            for m in members:
                # Do not even check underscored stuff and Parent class
                if not m.startswith('_') and 'BaseHook'not in m:
                    hook = getattr(module, m)()  # instanciate found class
                    if isinstance(hook, BaseHook):  # is child of BaseHook
                        self.hooks.append(hook)

    def call_hooks(self, obj, handle):
        [h.do_work(obj, handle) for h in self.hooks]

    def __init__(self):
        self.hooks = []
        self._create_hooks()
