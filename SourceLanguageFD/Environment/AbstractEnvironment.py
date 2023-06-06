from abc import ABC, abstractmethod

from SourceLanguageFD.Environment.AbstractElement import FDPElemAbstract, FDGCElemAbstract, FDGammaElem


class FDContext(ABC):
    elements = []

    def __init__(self):
        pass

    @abstractmethod
    def addElement(self, element):
        pass

    @abstractmethod
    def addElements(self, element):
        pass

    def show(self):
        for i in range(len(self.elements)):
            self.elements[i].show()
            if not (i == len(self.elements) - 1):
                print(", ", end=' ')

    @abstractmethod
    def removeLastElement(self):
        pass


class FDAbstractP(FDContext, ABC):
    def removeLastElement(self) -> FDPElemAbstract:
        assert len(self.elements) > 0
        return self.elements.pop()

    @abstractmethod
    def wellFormed(self, gc, gamma):
        pass

    @abstractmethod
    def getQiFromQ(self, q):
        pass

    @abstractmethod
    def getDFromQ(self, q):
        pass

    @abstractmethod
    def elaborate(self, gc):
        pass

    @abstractmethod
    def hasFunctionalDependency(self, gc, tc):
        pass

    @abstractmethod
    def getFunctionalDependency(self, gc, tc):
        pass


class FDAbstractGC(FDContext, ABC):
    def removeLastElement(self) -> FDGCElemAbstract:
        assert len(self.elements) > 0
        return self.elements.pop()

    @abstractmethod
    def getSigmaFromName(self, name: str):
        pass

    @abstractmethod
    def getSigmaFromMethod(self, m: str):
        pass

    @abstractmethod
    def getAFromName(self, name: str):
        pass

    @abstractmethod
    def getGC1FromName(self, name: str):
        pass

    @abstractmethod
    def getTCFromMethod(self, m: str):
        pass

    @abstractmethod
    def getTCListFromMethod(self, m: str):
        pass

    @abstractmethod
    def closure(self, qList):
        pass

    @abstractmethod
    def elaborate(self):
        pass

    @abstractmethod
    def inGC(self, aList, tau):
        pass

    @abstractmethod
    def getFDFromName(self, name):
        pass

    @abstractmethod
    def getDependants(self, tc):
        pass


class FDAbstractGamma(FDContext, ABC):
    def removeLastElement(self) -> FDGammaElem:
        assert len(self.elements) > 0
        return self.elements.pop()

    @abstractmethod
    def contains(self, element):
        pass

    @abstractmethod
    def containsTypeVar(self, element):
        pass

    @abstractmethod
    def equals(self, gamma):
        pass

    @abstractmethod
    def setElements(self, elements):
        pass

    @abstractmethod
    def elaborate(self, p, gc):
        pass

    @abstractmethod
    def getDeltaIndex(self):
        pass

    @abstractmethod
    def getDeltaOfGammaQ(self, gammaQ):
        pass
