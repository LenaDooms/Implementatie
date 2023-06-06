from typing import List

from IntermediateLanguage.Types.Sigma import ITypeConstr
from SourceLanguageFD.Constraint.constraint import FDQ
from SourceLanguageFD.Environment.AbstractEnvironment import FDAbstractGamma, FDAbstractGC, FDAbstractP
from SourceLanguageFD.Types.AbstractTypes import FDRho, FDTau, FDSigma


class FDRhoConstr(FDRho):

    def __init__(self, qList: List[FDQ], tau: FDTau):
        super().__init__()
        self.qList = qList
        self.tau = tau

    def show(self):
        for q in self.qList:
            q.show()
            print(" => ", end=' ')
        self.tau.show()

    def wellTyped(self, gamma: FDAbstractGamma, gc: FDAbstractGC):
        return all(q.wellFormed(gamma, gc) for q in self.qList) and self.tau.wellTyped(gamma, gc)

    def getTau(self):
        return self.tau

    def getRho(self):
        return self

    def equals(self, rho: FDSigma):
        if len(rho.getVariables()) != 0:
            return False
        if isinstance(rho, FDRhoConstr):
            return (self.tau.equals(rho.tau)
                    and all(any(q.equals(qi) for qi in rho.qList)for q in self.qList))
        elif isinstance(rho, FDTau) and len(self.qList) == 0:
            return self.tau.equals(rho)
        return False

    def getFreeVars(self):
        return self.tau.getFreeVars()

    def unambiguous(self, p: FDAbstractP, gc: FDAbstractGC):
        return self.tau.unambiguous(p, gc)

    def getVariables(self):
        return []

    def getConstraints(self):
        return self.qList

    def elaborate(self, p, gc):
        s = self.tau.elaborate(p, gc)
        qList = list(map(lambda q: q.elaborate(p, gc), self.qList))
        for i in range(1, len(qList) + 1):
            s = ITypeConstr(qList[-i], s)
        return s
