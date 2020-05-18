from hooks.pre_notify.baseprenotifyhook import BasePrenotifyHook

class PrintPrenotifyHook(BasePrenotifyHook):

    def do_work(self, item, from_hook, sender_id, recipients):
        print("Hola de prenotify")
        """
        This is the base hook for the prenotify-hook, which is triggered right before other clipboards are updated and webhooks are notified.
        """
        return item, from_hook, sender_id, recipients
