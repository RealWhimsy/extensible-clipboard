from importlib import machinery
from os import listdir

# TODO: this may be a bit cumbersome, but currently seems like the best solution
from hooks.basehook import BaseHook


class HookManager:

    def _create_hooks(self):

        # Rebuild hooks if method is called manually fore some reason
        if self.hooks:
            self.hooks = []

        base_path = './hooks'
        files = listdir(base_path)
        # Remove all files not ending on _hook.py
        hook_files = [f for f in files if f.endswith('_hook.py')]
        for file_name in hook_files:
            # module = import_module('server.hooks.' + file_name[:-3])
            modname = file_name[:-3]
            module = machinery.SourceFileLoader(modname, base_path+'/'+file_name).load_module()
            members = dir(module)
            for m in members:
                # Do not even check underscored stuff and Parent class
                if not m.startswith('_') and 'BaseHook'not in m and 'Hook' in m:
                    try:
                        hook = getattr(module, m)()  # instanciate found class
                    except TypeError:
                        print("Could not instantiate hook", m, 'from module', modname)
                    if isinstance(hook, BaseHook):  # is child of BaseHook
                        self.hooks.append(hook)


    def call_hooks(self, request):
        for h in self.hooks:
            if not h.do_work(request):
                return False
        return True

    def __init__(self):
        self.hooks = []
        self._create_hooks()
