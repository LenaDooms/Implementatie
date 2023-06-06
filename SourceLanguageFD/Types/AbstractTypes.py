from abc import ABCMeta, abstractmethod, ABC


class FDSigma(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    def show(self):
        pass

    @abstractmethod
    def wellTyped(self, gamma, gc):
        pass

    @abstractmethod
    def equals(self, t):
        pass

    @abstractmethod
    def getRho(self):
        pass

    @abstractmethod
    def getTau(self):
        pass

    @abstractmethod
    def getFreeVars(self):
        pass

    @abstractmethod
    def unambiguous(self, p, gc):
        pass

    @abstractmethod
    def getVariables(self):
        pass

    @abstractmethod
    def getConstraints(self):
        pass

    @abstractmethod
    def elaborate(self, p, gc):
        pass


class FDRho(FDSigma, ABC):
    pass


class FDTau(FDRho, ABC):
    @abstractmethod
    def substitute(self, aList, tList):
        pass

    @abstractmethod
    def equalsWithVars(self, aList, tau, bList):
        pass

    def getVariables(self):
        return []

    def getConstraints(self):
        return []
