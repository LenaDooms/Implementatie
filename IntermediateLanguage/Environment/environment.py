from typing import List

from IntermediateLanguage.Environment.AbstractElement import IGammaElem, IGCElemAbstract, IPElemAbstract
from IntermediateLanguage.Environment.AbstractEnvironment import IAbstractP, IAbstractGC, IAbstractGamma


class IGamma(IAbstractGamma):
    elements = []

    def __init__(self, gammaList: List[IGammaElem]):
        super().__init__()
        self.elements = gammaList

    def addElement(self, element: IGammaElem):
        self.elements.append(element)

    def addElements(self, elements: List[IGammaElem]):
        self.elements = self.elements + elements

    def equals(self, gamma: IAbstractGamma):
        return (len(gamma.elements) == len(self.elements)
                and all(gamma.elements[i].equals(self.elements[i]) for i in range(len(self.elements))))

    def setElements(self, elements: List[IGammaElem]):
        self.elements = elements

    def insertElement(self, element: IGammaElem):
        self.elements.insert(0, element)


class IGC(IAbstractGC):
    elements = []

    def __init__(self, gcList: List[IGCElemAbstract]):
        super().__init__()
        self.elements = gcList

    def addElement(self, element: IGCElemAbstract):
        self.elements.append(element)

    def addElements(self, elements: List[IGCElemAbstract]):
        self.elements = self.elements + elements

    def insertElement(self, element: IGCElemAbstract):
        self.elements.insert(0, element)


class IP(IAbstractP):
    elements = []

    def __init__(self):
        super().__init__()
        self.elements = []

    def addElement(self, element: IPElemAbstract):
        self.elements.append(element)

    def addElements(self, elements: List[IPElemAbstract]):
        self.elements = self.elements + elements

    def insertElement(self, element: IPElemAbstract):
        self.elements.insert(0, element)
