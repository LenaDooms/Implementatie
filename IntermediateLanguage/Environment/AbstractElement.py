from abc import ABC, abstractmethod


class IPElemAbstract(ABC):
    def __init__(self, c, m, e):
        self.c = c
        self.m = m
        self.e = e

    @abstractmethod
    def show(self):
        pass

    @abstractmethod
    def equals(self, element):
        pass


class IGCElemAbstract(ABC):
    def __init__(self, m, tc, sigma):
        self.m = m
        self.tc = tc
        self.sigma = sigma

    @abstractmethod
    def show(self):
        pass

    @abstractmethod
    def equals(self, element):
        pass


class IGammaElem(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def show(self):
        pass

    @abstractmethod
    def equals(self, element):
        pass
