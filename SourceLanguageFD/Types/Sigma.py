from copy import deepcopy
from typing import List

from IntermediateLanguage.Types.Sigma import ITypeVar
from SourceLanguage.Constraint.constraint import QSubst
from SourceLanguage.Types.Tau import TypeSubst
from SourceLanguageFD.Constraint.constraint import FDQSubst
from SourceLanguageFD.Environment.AbstractEnvironment import FDAbstractGamma, FDAbstractGC, FDAbstractP
from SourceLanguageFD.Environment.Element import FDGammaA
from SourceLanguageFD.Types import Tau
from SourceLanguageFD.Types.AbstractTypes import FDSigma, FDRho
from SourceLanguageFD.Types.Rho import FDRhoConstr
from SourceLanguageFD.Types.Tau import FDTypeA, FDTypeSubst


class FDSigmaForall(FDSigma):

    def __init__(self, aList: List[FDTypeA], rho: FDRho):
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

    def wellTyped(self, gamma: FDAbstractGamma, gc: FDAbstractGC):
        gammaNew = deepcopy(gamma)
        gammaNew.elements = deepcopy(gamma.elements)
        gammaNew.addElements(list(map(lambda a: FDGammaA(a), self.aList)))
        return (all(not gamma.contains(FDGammaA(a)) for a in self.aList)
                and self.rho.wellTyped(gammaNew, gc))

    def getRho(self) -> FDRho:
        return self.rho

    def getTau(self) -> Tau:
        return self.rho.getTau()

    def equals(self, s: FDSigma):
        aList1 = self.aList
        if isinstance(s, FDSigmaForall):
            aList2 = s.aList
            return (s.rho.equals(self.rho)
                    and len(aList1) == len(aList2)
                    and all(any(a.equals(aj) for aj in aList2)for a in aList1))
        elif len(aList1) == 0 and isinstance(s, FDRho):
            return self.rho.equals(s)
        return False

    def getFreeVars(self):
        fv = []
        for a in self.getTau().getFreeVars():
            if not any(a.equals(aj) for aj in self.aList):
                fv.append(a)
        return fv

    def unambiguous(self, p: FDAbstractP, gc: FDAbstractGC):
        sigmaNew = self.applyFunctionalDependencies(p, gc)
        fv = sigmaNew.getTau().getFreeVars()
        return all(any(aj.equals(a) for a in fv) for aj in sigmaNew.getVariables())

    def getVariables(self):
        return self.aList

    def getConstraints(self):
        return self.rho.getConstraints()

    def addElements(self, elements: List[FDTypeA]):
        self.aList += elements

    def elaborate(self, p, gc):
        sigmaNew = self.applyFunctionalDependencies(p, gc)
        s = sigmaNew.rho.elaborate(p, gc)
        for i in range(1, len(sigmaNew.getVariables()) + 1):
            s = ITypeVar(sigmaNew.getVariables()[-i].elaborate(gc), s)
        return s

    def applyFunctionalDependencies(self,  p: FDAbstractP, gc: FDAbstractGC):
        changes = True
        sigma = deepcopy(self)
        while changes:
            changes = False
            for q in sigma.getConstraints():
                if q.containsVariables() and p.hasFunctionalDependency(gc, q.tc):
                    tc2 = p.getFunctionalDependency(gc, q.tc)
                    variables = gc.getDependants(q.tc)
                    values = gc.getDependants(tc2)
                    aListNew = list(filter(lambda a: all(not a.equals(a2) for a2 in variables), sigma.aList))
                    qListNew = list(map(lambda qi: FDQSubst(values, variables, qi).evaluate(), sigma.getConstraints()))
                    tauNew = FDTypeSubst(values, variables, sigma.getTau()).evaluate()
                    sigma = FDSigmaForall(aListNew, FDRhoConstr(qListNew, tauNew))
                    changes = True
        return sigma
