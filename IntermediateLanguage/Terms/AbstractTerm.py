from abc import ABCMeta, abstractmethod, ABC


class ITerm(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    def show(self):
        pass

    @abstractmethod
    def equals(self, e):
        pass


class IValue(ITerm, ABC):
    pass
