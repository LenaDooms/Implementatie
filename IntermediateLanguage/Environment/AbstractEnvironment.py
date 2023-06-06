from abc import ABC, abstractmethod


class IContext(ABC):
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
    def insertElement(self, element):
        pass


class IAbstractP(IContext, ABC):
    pass


class IAbstractGC(IContext, ABC):
    pass


class IAbstractGamma(IContext, ABC):
    pass
