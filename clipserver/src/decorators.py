from flask import request


def pre_commit_hooks(func):
    def wrapper(*args, **kwargs):
        # Pass request to hooks and get their 'consent'
        if not args[0].hook_manager.trigger_precommit(request):
            return '', 403
        return func(*args, **kwargs)
    return wrapper


def pre_access_hooks(func):
    def wrapper(*args, **kwargs):
        # Pass request to hooks and get their 'consent'
        if not args[0].hook_manager.trigger_preaccess(request):
            return '', 403
        return func(*args, **kwargs)
    return wrapper


def post_access_hooks(func, self):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        result = self.hook_manager.trigger_postcommit(result)
        return result
    return wrapper

