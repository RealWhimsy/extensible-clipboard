from hooks.post_notify.basepostnotifyhook import BasePostnotifyHook

class PrintPostNotifyHook(BasePostnotifyHook):

    def do_work(self, item, from_hook, sender_id, recipients):
        print("Hasta la vista de postnotify")
        return item, from_hook, sender_id, recipients
