from abc import ABC, abstractmethod


class BasePrenotifyHook(ABC):

    @abstractmethod
    def do_work(self, item, from_hook, sender_id, recipients):
        """
        The pre-notify hook manages the list of recipients to be notified
        """
        return item, from_hook, sender_id, recipients,
