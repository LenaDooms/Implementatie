from abc import ABC, abstractmethod


class FDConstraint(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def equals(self, constraint):
        pass

    @abstractmethod
    def elaborate(self, p, gc):
        pass


class FDAbstractQ(FDConstraint):
    @abstractmethod
    def show(self):
        pass

    @abstractmethod
    def wellFormed(self, gamma, gc):
        pass

    @abstractmethod
    def substitute(self, tau, a):
        pass

    @abstractmethod
    def entails(self, p, gc, gamma):
        pass

    @abstractmethod
    def getDictionary(self, p, gc, gamma):
        pass

    @abstractmethod
    def containsVariables(self):
        pass


class FDAbstractC(FDConstraint):
    def __init__(self, aList, qList, q):
        super().__init__()
        self.aList = aList
        self.qList = qList
        self.q = q

    @abstractmethod
    def show(self):
        pass

    @abstractmethod
    def wellFormed(self, gamma, gc):
        pass

    @abstractmethod
    def unambiguous(self, p, gc):
        pass

    @abstractmethod
    def applyFunctionalDependencies(self, p, gc):
        pass
