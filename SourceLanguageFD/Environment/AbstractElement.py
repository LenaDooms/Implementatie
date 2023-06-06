from abc import ABC, abstractmethod


class FDPElemAbstract(ABC):
    def __init__(self, c, m, gamma, e):
        self.c = c
        self.m = m
        self.gamma = gamma
        self.e = e

    @abstractmethod
    def show(self):
        pass

    @abstractmethod
    def equals(self, element):
        pass


class FDGCElemAbstract(ABC):
    def __init__(self,  m, tcList, tc, sigma, fd):
        self.m = m
        self.tcList = tcList
        self.tc = tc
        self.sigma = sigma
        self.fd = fd

    @abstractmethod
    def show(self):
        pass

    @abstractmethod
    def equals(self, element):
        pass

    @abstractmethod
    def elaborate(self, gc):
        pass


class FDGammaElem(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def show(self):
        pass

    @abstractmethod
    def equals(self, element):
        pass

    @abstractmethod
    def elaborate(self, p, gc):
        pass
