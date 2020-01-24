from flask import request


def pre_hooks(func):
    def wrapper(*args, **kwargs):
        # Pass request to hooks and get their 'consent'
        if not args[0].pre_hooks.call_hooks(request):
            return '', 403
        return func(*args, **kwargs)
    return wrapper
