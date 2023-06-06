from copy import deepcopy
from typing import List

from IntermediateLanguage.Types.Sigma import ITypeVar
from SourceLanguage.Environment.AbstractEnvironment import AbstractGamma, AbstractGC
from SourceLanguage.Environment.Element import GammaA
from SourceLanguage.Types import Tau
from SourceLanguage.Types.AbstractTypes import Sigma, Rho
from SourceLanguage.Types.Tau import TypeA


class SigmaForall(Sigma):

    def __init__(self, aList: List[TypeA], rho: Rho):
        super().__init__()
        self.aList = aList
        self.rho = rho

    def show(self):
        print("Forall ", end=' ')
        for a in self.aList:
            a.show()
            print(", ", end=' ')
        print(". ", end=' ')
        self.rho.show()

    def wellTyped(self, gamma: AbstractGamma, gc: AbstractGC):
        gammaNew = deepcopy(gamma)
        gammaNew.elements = deepcopy(gamma.elements)
        gammaNew.addElements(list(map(lambda a: GammaA(a), self.aList)))
        return (all(not gamma.contains(GammaA(a)) for a in self.aList)
                and self.rho.wellTyped(gammaNew, gc))

    def getRho(self) -> Rho:
        return self.rho

    def getTau(self) -> Tau:
        return self.rho.getTau()

    def equals(self, s: Sigma):
        aList1 = self.aList
        if isinstance(s, SigmaForall):
            aList2 = s.aList
            return (s.rho.equals(self.rho)
                    and len(aList1) == len(aList2)
                    and all(any(a.equals(aj) for aj in aList2)for a in aList1))
        elif len(aList1) == 0 and isinstance(s, Rho):
            return self.rho.equals(s)
        return False

    def getFreeVars(self):
        fv = []
        for a in self.getTau().getFreeVars():
            if not any(a.equals(aj) for aj in self.aList):
                fv.append(a)
        return fv

    def unambiguous(self):
        fv = self.getTau().getFreeVars()
        return all(any(aj.equals(a) for a in fv) for aj in self.aList)

    def getVariables(self):
        return self.aList

    def getConstraints(self):
        return self.rho.getConstraints()

    def elaborate(self):
        s = self.rho.elaborate()
        for i in range(1, len(self.aList) + 1):
            s = ITypeVar(self.aList[-i].elaborate(), s)
        return s
