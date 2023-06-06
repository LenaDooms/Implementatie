from abc import ABC, abstractmethod

from SourceLanguage.Environment.AbstractElement import PElemAbstract, GCElemAbstract, GammaElem


class Context(ABC):
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

    @abstractmethod
    def insertElement(self, element):
        pass


class AbstractP(Context, ABC):
    def removeLastElement(self) -> PElemAbstract:
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


class AbstractGC(Context, ABC):
    def removeLastElement(self) -> GCElemAbstract:
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


class AbstractGamma(Context, ABC):
    def removeLastElement(self) -> GammaElem:
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
    def getDeltaIndex(self):
        pass

    @abstractmethod
    def getDeltaOfGammaQ(self, gammaQ):
        pass

    @abstractmethod
    def elaborate(self):
        pass
