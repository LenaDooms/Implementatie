from abc import ABC, abstractmethod
from typing import List

from IntermediateLanguage.Types.AbstractType import ISigma


class Dictionary(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def equals(self, d):
        pass

    @abstractmethod
    def show(self):
        pass


class DictionaryDelta(Dictionary):
    def __init__(self, delta: int):
        super().__init__()
        self.delta = delta

    def equals(self, d: Dictionary):
        return isinstance(d, DictionaryDelta) and self.delta == d.delta

    def show(self):
        print(self.delta, end='')


class DictionarySigma(Dictionary):
    def __init__(self, d: int, sList: List[ISigma], dList: List[Dictionary]):
        super().__init__()
        self.d = d
        self.sList = sList
        self.dList = dList

    def equals(self, d):
        return (isinstance(d, DictionarySigma)
                and self.d == d.d
                and len(self.sList) == len(d.sList)
                and all(self.sList[i].equals(d.sList[i]) for i in range(len(self.sList)))
                and len(self.dList) == len(d.dList)
                and all(self.dList[i].equals(d.dList[i]) for i in range(len(self.dList))))

    def show(self):
        print(self.d, end='')
        for sigma in self.sList:
            print(' ', end=' ')
            sigma.show()
        for d in self.dList:
            print(' ', end=' ')
            d.show()

#  to do: dictionary values
