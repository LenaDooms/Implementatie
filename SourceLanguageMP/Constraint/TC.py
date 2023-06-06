from abc import ABC, abstractmethod
from typing import List

from IntermediateLanguage.Constraint.TC import ITCTau, ITCA
from IntermediateLanguage.Types.Sigma import ITypeSubst, ITypeA
from SourceLanguageMP.Environment.AbstractEnvironment import MPAbstractGC
from SourceLanguageMP.Types.AbstractTypes import MPTau
from SourceLanguageMP.Types.Tau import MPTypeA


class MPTC(ABC):
    def __init__(self, name: str, tList: List[MPTau]):
        self.name = name
        self.tList = tList

    def show(self):
        print(self.name + " ", end=' ')
        for t in self.tList:
            t.show()

    def getName(self):
        return self.name

    def equals(self, tc):
        return (isinstance(tc, MPTC)
                and len(self.tList) == len(tc.tList)
                and all(self.tList[i].equals(tc.tList[i]) for i in range(len(self.tList)))
                and self.name == tc.name)

    @abstractmethod
    def elaborate(self, gc: MPAbstractGC):
        pass


class MPTCA(MPTC):
    def __init__(self, name: str, aList: List[MPTypeA]):
        super().__init__(name, aList)

    def elaborate(self, gc: MPAbstractGC):
        return ITCA(self.name, ITypeA("a"))


class MPTCTau(MPTC):
    def __init__(self, name: str, tList: List[MPTau]):
        super().__init__(name, tList)

    def elaborate(self, gc: MPAbstractGC):
        sigma = gc.getSigmaFromName(self.name).elaborate(gc)
        aList = list(map(lambda a: a.elaborate(gc), gc.getAFromName(self.name)))
        tList = list(map(lambda t: t.elaborate(gc), self.tList))
        tNew = ITypeSubst(tList, aList, sigma)
        tNew = tNew.evaluate()
        return ITCTau(self.name, tNew)
