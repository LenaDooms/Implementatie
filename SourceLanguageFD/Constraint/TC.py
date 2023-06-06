from abc import ABC, abstractmethod
from typing import List

from IntermediateLanguage.Constraint.TC import ITCTau, ITCA
from IntermediateLanguage.Types.Sigma import ITypeSubst, ITypeA
from SourceLanguageFD.Environment.AbstractEnvironment import FDAbstractGC, FDAbstractP
from SourceLanguageFD.Types.AbstractTypes import FDTau
from SourceLanguageFD.Types.Tau import FDTypeA


class FDTC(ABC):
    def __init__(self, name: str, tList: List[FDTau]):
        self.name = name
        self.tList = tList

    def show(self):
        print(self.name + " ", end=' ')
        for t in self.tList:
            t.show()

    def getName(self):
        return self.name

    def equals(self, tc):
        return (isinstance(tc, FDTC)
                and len(self.tList) == len(tc.tList)
                and all(self.tList[i].equals(tc.tList[i]) for i in range(len(self.tList)))
                and self.name == tc.name)

    @abstractmethod
    def elaborate(self, p: FDAbstractP, gc: FDAbstractGC):
        pass


class FDTCA(FDTC):
    def __init__(self, name: str, aList: List[FDTypeA]):
        super().__init__(name, aList)

    def elaborate(self, p: FDAbstractP, gc: FDAbstractGC):
        return ITCA(self.name, ITypeA("a"))


class FDTCTau(FDTC):
    def __init__(self, name: str, tList: List[FDTau]):
        super().__init__(name, tList)

    def elaborate(self, p: FDAbstractP, gc: FDAbstractGC):
        sigma = gc.getSigmaFromName(self.name).elaborate(p, gc)
        aList = list(map(lambda a: a.elaborate(p, gc), gc.getAFromName(self.name)))
        tList = list(map(lambda t: t.elaborate(p, gc), self.tList))
        tNew = ITypeSubst(tList, aList, sigma)
        tNew = tNew.evaluate()
        return ITCTau(self.name, tNew)
