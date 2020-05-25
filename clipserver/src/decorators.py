from flask import request

'''
ACCESS HOOKS

Access Hooks will be triggered, whenever an API Request is made. 

Access Hooks can be used for controlling access to resources based on the requests made or document access 
(e.g. for logging reasons).
'''


def access_hooks(func):
    def wrapper(*args, **kwargs):
        return _pre_access_hooks(
            _post_access_hooks(
                func
            )
        )(*args, **kwargs)
    return wrapper


def _pre_access_hooks(func):
    def wrapper(*args, **kwargs):
        try:
            args[0].hook_manager.trigger_preaccess(request)
            return func(*args, **kwargs)
        except ValueError:
            return 'Unauthorized Access', 403
    return wrapper


def _post_access_hooks(func):
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        args[0].hook_manager.trigger_postaccess(response)
        return response
    return wrapper
#
#

'''
COMMIT HOOKS

Commit Hooks will be triggered right before saving a new clip or child clip.

Commit Hooks can be used to derive and save related formats or transform the clip to be saved.
'''

def commit_hooks(func):
    def wrapper(*args, **kwargs):
        return _pre_commit_hooks(
            _post_commit_hooks(
                func
            )
        )(*args, **kwargs)
    return wrapper


def _pre_commit_hooks(func):
    def wrapper(*args, **kwargs):
        # Pass request to hooks and get their 'consent'
        if not args[0].hook_manager.trigger_precommit(*args, **kwargs):
            return '', 403
        return func(*args, **kwargs)
    return wrapper


def _post_commit_hooks(func):
    def wrapper(*args, **kwargs):
        result = func(**kwargs)
        result = args[0].hook_manager.trigger_postcommit(result)
        return result
    return wrapper
#
#


def notify_hooks(func):
    def wrapper(*args, **kwargs):
        return _pre_notify_hooks(
            _post_notify_hooks(
                func
            )
        )(*args, **kwargs)
    return wrapper


def _pre_notify_hooks(func):
    def wrapper(*args, **kwargs):
        nargs = args[0].hook_manager.trigger_prenotify(*args[1:])
        return func(args[0], *nargs, **kwargs)
    return wrapper


def _post_notify_hooks(func):
    def wrapper(*args, **kwargs):
        for i in args[1:]:
            print(i)
        result = func(*args[1:])
        args[0].hook_manager.trigger_postnotify(*args[1:])
        return result
    return wrapper
