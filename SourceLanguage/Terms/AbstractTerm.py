from abc import ABCMeta, abstractmethod


class Term(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    def show(self):
        pass

    @abstractmethod
    def getType(self, p, gc, gamma):
        pass

    @abstractmethod
    def hasType(self, p, gc, gamma, tau):
        pass

    @abstractmethod
    def equals(self, e):
        pass

    @abstractmethod
    def elaborate(self, p, gc, gamma):
        pass

    @abstractmethod
    def elaborateWithType(self, p, gc, gamma, tau):
        pass
