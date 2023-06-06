from abc import ABC, abstractmethod


class IConstraint(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def equals(self, constraint):
        pass


class IAbstractQ(IConstraint):
    @abstractmethod
    def show(self):
        pass

    @abstractmethod
    def substitute(self, tau, a):
        pass


class IAbstractC(IConstraint):
    @abstractmethod
    def show(self):
        pass
