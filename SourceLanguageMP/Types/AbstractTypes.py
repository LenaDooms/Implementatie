from abc import ABCMeta, abstractmethod, ABC


class MPSigma(metaclass=ABCMeta):
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
    def unambiguous(self):
        pass

    @abstractmethod
    def getVariables(self):
        pass

    @abstractmethod
    def getConstraints(self):
        pass

    @abstractmethod
    def elaborate(self, gc):
        pass


class MPRho(MPSigma, ABC):
    pass


class MPTau(MPRho, ABC):
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
