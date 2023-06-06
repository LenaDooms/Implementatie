from abc import ABC, abstractmethod

from SourceLanguageMP.Environment.AbstractElement import MPPElemAbstract, MPGCElemAbstract, MPGammaElem


class MPContext(ABC):
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


class MPAbstractP(MPContext, ABC):
    def removeLastElement(self) -> MPPElemAbstract:
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


class MPAbstractGC(MPContext, ABC):
    def removeLastElement(self) -> MPGCElemAbstract:
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


class MPAbstractGamma(MPContext, ABC):
    def removeLastElement(self) -> MPGammaElem:
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
    def elaborate(self, gc):
        pass

    @abstractmethod
    def getDeltaIndex(self):
        pass

    @abstractmethod
    def getDeltaOfGammaQ(self, gammaQ):
        pass
