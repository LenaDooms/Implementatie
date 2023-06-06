from abc import ABCMeta, abstractmethod


class ISigma(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    def show(self):
        pass

    @abstractmethod
    def equals(self, s):
        pass

    @abstractmethod
    def substitute(self, tList, aList):
        pass