from importlib import machinery
from os import listdir
from hooks.basehook import BaseHook
from hooks.pre_commit.baseprecommithook import BasePreCommitHook


class HookManager:

    def _load_hooks(self, root_dir, name_contains, BaseClass):
        hooks = []
        files = listdir(root_dir)
        hook_files = [f for f in files if f.endswith('_' + name_contains + '.py')]
        for file_name in hook_files:
            modname = file_name[:-3]
            module = machinery.SourceFileLoader(modname, root_dir +'/'+file_name).load_module()
            members = dir(module)
            for m in members:
                # Do not even check underscored stuff and Parent class
                if not m.startswith('_') and 'Base'not in m and 'Hook' in m:
                    try:
                        hook = getattr(module, m)()  # instanciate found class
                    except TypeError:
                        print("Could not instantiate hook", m, 'from module', modname)
                    if isinstance(hook, BaseClass):  # is child of BaseHook
                        hooks.append(hook)
        return hooks


    def call_hooks(self, request):
        for h in self.hooks:
            if not h.do_work(request):
                return False
        return True


    def trigger_precommit(self, request):
        for h in self.pre_commit_hooks:
            if not h.do_work(request):
                return False
        return True

    def __init__(self):
        self.hooks = []
        self.pre_commit_hooks = self._load_hooks('./hooks/pre_commit', 'precommithook', BasePreCommitHook)
