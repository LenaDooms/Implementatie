from typing import List

from IntermediateLanguage.Constraint.constraint import IQSubst, IQ, IC
from IntermediateLanguage.Dictionaries.Dictionary import DictionaryDelta, DictionarySigma
from SourceLanguageFD.Constraint.AbstractConstraint import FDAbstractQ, FDAbstractC
from SourceLanguageFD.Constraint.TC import FDTC
from SourceLanguageFD.Environment.AbstractEnvironment import FDAbstractGamma, FDAbstractGC, FDAbstractP
from SourceLanguageFD.Environment.Element import FDGammaA, FDGammaQ
from SourceLanguageFD.Types.AbstractTypes import FDTau
from SourceLanguageFD.Types.Tau import FDTypeA
from copy import deepcopy


class FDQ(FDAbstractQ):
    def __init__(self, tc: FDTC):
        super().__init__()
        self.tc = tc

    def show(self):
        self.tc.show()

    def wellFormed(self, gamma: FDAbstractGamma, gc: FDAbstractGC):
        sigma = gc.getSigmaFromName(self.tc.name)
        gc1 = gc.getGC1FromName(self.tc.name)
        gammaNew = deepcopy(gamma)
        gammaNew.elements = deepcopy(gamma.elements)
        gammaNew.setElements(list(map(lambda a: FDGammaA(a), gc.getAFromName(self.tc.name))))
        return all(t.wellTyped(gamma, gc) for t in self.tc.tList) and sigma.wellTyped(gammaNew, gc1)

    def equals(self, constraint):
        return isinstance(constraint, FDQ) and self.tc.equals(constraint.tc)

    def substitute(self, tList: List[FDTau], aList: List[FDTypeA]):
        for i in range(len(aList)):
            for j in range(len(self.tc.tList)):
                if self.tc.tList[j].equals(aList[i]):
                    self.tc.tList[j] = tList[i]

    def entails(self, p: FDAbstractP, gc: FDAbstractGC, gamma: FDAbstractGamma):
        if any(element.c.q.equals(FDGammaQ(self)) for element in p.elements) and p.wellFormed(gc, gamma):
            return True
        else:
            return FDQSubst([], [], self).entails(p, gc, gamma)

    def elaborate(self, p, gc):
        return IQ(self.tc.elaborate(p, gc))

    def getDictionary(self, p: FDAbstractP, gc: FDAbstractGC, gamma: FDAbstractGamma):
        if any(element.c.q.equals(FDGammaQ(self)) for element in p.elements) and p.wellFormed(gc, gamma):
            return gamma.getDeltaOfGammaQ(FDGammaQ(self))
        else:
            return FDQSubst([], [], self).getDictionary(p, gc, gamma)

    def containsVariables(self):
        fv = []
        for t in self.tc.tList:
            fv += t.getFreeVars()
        return len(fv) > 0


class FDQSubst(FDAbstractQ):

    def __init__(self, tList: List[FDTau], aList: List[FDTypeA], q: FDAbstractQ):
        assert len(tList) == len(aList)
        super().__init__()
        self.tList = tList
        self.aList = aList
        self.q = q

    def show(self):
        print("[ ", end=" ")
        for tau in self.tList:
            tau.show()
            print(", ", end=' ')
        print(" / ", end=' ')
        for a in self.aList:
            a.show()
            print(", ", end=' ')
        print(" ] ", end=' ')
        self.q.show()

    def wellFormed(self, gamma, gc):
        newQ = deepcopy(self.q)
        newQ.substitute(self.tList, self.aList)
        return newQ.wellFormed(gamma, gc)

    def equals(self, constraint):
        q1New = deepcopy(self.q)
        q1New.substitute(self.tList, self.aList)
        if isinstance(constraint, FDQSubst):
            q2New = deepcopy(constraint.q)
            q2New.substitute(self.tList, self.aList)
        else:
            q2New = constraint
        return q1New.equals(q2New)

    def substitute(self, tList: List[FDTau], aList: List[FDTypeA]):
        assert all(not any(a1.equals(a2) for a2 in aList) for a1 in self.aList)
        self.q.substitute(self.tList, self.aList)
        self.q.substitute(tList, aList)
        return self.q

    def entails(self, p: FDAbstractP, gc: FDAbstractGC, gamma: FDAbstractGamma):
        if any(element.c.q.equals(FDGammaQ(self)) for element in p.elements):
            return p.wellFormed(gc, gamma)
        else:
            qiList = p.getQiFromQ(self.q)
            return (all(t.wellTyped(gamma, gc) for t in self.tList)
                    and p.wellFormed(gc, gamma)
                    and all(FDQSubst(self.tList, self.aList, qi).entails(p, gc, gamma) for qi in qiList))

    def elaborate(self, p, gc):
        tList = list(map(lambda t: t.elaborate(p, gc), self.tList))
        aList = list(map(lambda a: a.elaborate(p, gc), self.aList))
        return IQSubst(tList, aList, self.q.elaborate(p, gc))

    def getDictionary(self, p: FDAbstractP, gc: FDAbstractGC, gamma: FDAbstractGamma):
        if any(element.c.q.equals(FDGammaQ(self)) for element in p.elements):
            delta = gamma.getDeltaOfGammaQ(FDGammaQ(self))
            return DictionaryDelta(delta)
        else:
            sj = list(map(lambda t: t.elaborate(p, gc), self.tList))
            di = list(map(lambda q: FDQSubst(self.tList, self.aList, q).getDictionary(p, gc, gamma), p.getQiFromQ(self.q)))
            d = p.getDFromQ(self.q)
            return DictionarySigma(d, sj, di)

    def evaluate(self):
        q = deepcopy(self)
        q.q.substitute(q.tList, q.aList)
        return q.q

    def containsVariables(self):
        q = self.evaluate()
        fv = []
        for t in q.tc.tList:
            fv += t.getFreeVars()
        return len(fv) > 0


class FDC(FDAbstractC):
    def __init__(self, aList: List[FDTypeA], qList: List[FDQ], q: FDQ):
        super().__init__(aList, qList, q)

    def show(self):
        print("Forall ", end=' ')
        for a in self.aList:
            a.show()
            print(", ", end=' ')
        print(". ", end=" ")
        for q in self.qList:
            q.show()
            print(", ", end=' ')
        print(" => ", end=' ')
        self.q.show()

    def wellFormed(self, gamma: FDAbstractGamma, gc: FDAbstractGC):
        gammaNew = deepcopy(gamma)
        aj = list(map(lambda x: FDGammaA(x), self.aList))
        gammaNew.addElements(aj)
        return (all(not gamma.contains(a) for a in aj)
                and all(q.wellFormed(gammaNew, gc) for q in self.qList)
                and self.q.wellFormed(gammaNew, gc))

    def equals(self, constraint):
        return (isinstance(constraint, FDC)
                and self.q.equals(constraint.q)
                and len(self.aList) == len(constraint.aList)
                and all(any(a.equals(aj) for aj in constraint.aList) for a in self.aList)
                and len(self.qList) == len(constraint.qList)
                and all(any(q.equals(qj) for qj in constraint.qList) for q in self.qList))

    def unambiguous(self, p: FDAbstractP, gc: FDAbstractGC):
        cNew = self.applyFunctionalDependencies(p, gc)
        fv = []
        for t in cNew.q.tc.tList:
            fv += t.getFreeVars()
        return all(any(aj.equals(a) for a in fv) for aj in cNew.aList)

    def elaborate(self, p, gc):
        cNew = self.applyFunctionalDependencies(p, gc)
        aList = list(map(lambda a: a.elaborate(p, gc), cNew.aList))
        qList = list(map(lambda q: q.elaborate(p, gc), cNew.qList))
        return IC(aList, qList, cNew.q.elaborate(p, gc))

    def applyFunctionalDependencies(self,  p: FDAbstractP, gc: FDAbstractGC):
        changes = True
        c = deepcopy(self)
        while changes:
            changes = False
            for q in c.qList:
                if q.containsVariables() and p.hasFunctionalDependency(gc, q.tc):
                    tc2 = p.getFunctionalDependency(gc, q.tc)
                    variables = gc.getDependants(q.tc)
                    values = gc.getDependants(tc2)
                    aListNew = list(filter(lambda a: all(not a.equals(a2) for a2 in variables), c.aList))
                    qListNew = list(map(lambda qi: FDQSubst(values, variables, qi).evaluate(), c.qList))
                    qNew = FDQSubst(values, variables, c.q).evaluate()
                    c = FDC(aListNew, qListNew, qNew)
                    changes = True
        return c
