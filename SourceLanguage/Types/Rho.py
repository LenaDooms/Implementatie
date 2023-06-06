from typing import List

from IntermediateLanguage.Types.Sigma import ITypeConstr
from SourceLanguage.Constraint.constraint import Q
from SourceLanguage.Environment.AbstractEnvironment import AbstractGamma, AbstractGC
from SourceLanguage.Types.AbstractTypes import Rho, Tau, Sigma

class RhoConstr(Rho):

    def __init__(self, qList: List[Q], tau: Tau):
        super().__init__()
        self.qList = qList
        self.tau = tau

    def show(self):
        for q in self.qList:
            q.show()
            print(" => ", end=' ')
        self.tau.show()

    def wellTyped(self, gamma: AbstractGamma, gc: AbstractGC):
        return all(q.wellFormed(gamma, gc) for q in self.qList) and self.tau.wellTyped(gamma, gc)

    def getTau(self):
        return self.tau

    def getRho(self):
        return self

    def equals(self, rho: Sigma):
        if len(rho.getVariables()) != 0:
            return False
        if isinstance(rho, RhoConstr):
            return (self.tau.equals(rho.tau)
                    and all(any(q.equals(qi) for qi in rho.qList)for q in self.qList))
        elif isinstance(rho, Tau) and len(self.qList) == 0:
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

    def elaborate(self):
        s = self.tau.elaborate()
        for i in range(1, len(self.qList)+1):
            s = ITypeConstr(self.qList[-i].elaborate(), s)
        return s
