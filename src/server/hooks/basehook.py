from abc import ABC, abstractmethod

class BaseHook(ABC):

    @abstractmethod
    def do_work(self, obj):
        pass
