from typing import List

from IntermediateLanguage.Types.Sigma import ITypeConstr
from SourceLanguageMP.Constraint.constraint import MPQ
from SourceLanguageMP.Environment.AbstractEnvironment import MPAbstractGamma, MPAbstractGC
from SourceLanguageMP.Types.AbstractTypes import MPRho, MPTau, MPSigma


class MPRhoConstr(MPRho):

    def __init__(self, qList: List[MPQ], tau: MPTau):
        super().__init__()
        self.qList = qList
        self.tau = tau

    def show(self):
        for q in self.qList:
            q.show()
            print(" => ", end=' ')
        self.tau.show()

    def wellTyped(self, gamma: MPAbstractGamma, gc: MPAbstractGC):
        return all(q.wellFormed(gamma, gc) for q in self.qList) and self.tau.wellTyped(gamma, gc)

    def getTau(self):
        return self.tau

    def getRho(self):
        return self

    def equals(self, rho: MPSigma):
        if len(rho.getVariables()) != 0:
            return False
        if isinstance(rho, MPRhoConstr):
            return (self.tau.equals(rho.tau)
                    and all(any(q.equals(qi) for qi in rho.qList)for q in self.qList))
        elif isinstance(rho, MPTau) and len(self.qList) == 0:
            return self.tau.equals(rho)
        return False

    def getFreeVars(self):
        return self.tau.getFreeVars()

    def unambiguous(self):
        return self.tau.unambiguous()

    def getVariables(self):
        return []

    def getConstraints(self):
        return self.qList

    def elaborate(self, gc):
        s = self.tau.elaborate(gc)
        qList = list(map(lambda q: q.elaborate(gc), self.qList))
        for i in range(1, len(qList) + 1):
            s = ITypeConstr(qList[-i], s)
        return s
