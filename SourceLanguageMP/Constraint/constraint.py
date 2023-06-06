from typing import List

from IntermediateLanguage.Constraint.constraint import IQSubst, IQ, IC
from IntermediateLanguage.Dictionaries.Dictionary import DictionaryDelta, DictionarySigma
from SourceLanguageMP.Constraint.AbstractConstraint import MPAbstractQ, MPAbstractC
from SourceLanguageMP.Constraint.TC import MPTC
from SourceLanguageMP.Environment.AbstractEnvironment import MPAbstractGamma, MPAbstractGC, MPAbstractP
from SourceLanguageMP.Environment.Element import MPGammaA, MPGammaQ
from SourceLanguageMP.Types.AbstractTypes import MPTau
from SourceLanguageMP.Types.Tau import MPTypeA
from copy import deepcopy

from exceptions import NotFoundError


class MPQ(MPAbstractQ):
    def __init__(self, tc: MPTC):
        super().__init__()
        self.tc = tc

    def show(self):
        self.tc.show()

    def wellFormed(self, gamma: MPAbstractGamma, gc: MPAbstractGC):
        sigma = gc.getSigmaFromName(self.tc.name)
        gc1 = gc.getGC1FromName(self.tc.name)
        gammaNew = deepcopy(gamma)
        gammaNew.elements = deepcopy(gamma.elements)
        gammaNew.setElements(list(map(lambda a: MPGammaA(a), gc.getAFromName(self.tc.name))))
        return all(t.wellTyped(gamma, gc) for t in self.tc.tList) and sigma.wellTyped(gammaNew, gc1)

    def equals(self, constraint):
        return isinstance(constraint, MPQ) and self.tc.equals(constraint.tc)

    def substitute(self, tList: List[MPTau], aList: List[MPTypeA]):
        for i in range(len(aList)):
            for j in range(len(self.tc.tList)):
                if self.tc.tList[j].equals(aList[i]):
                    self.tc.tList[j] = tList[i]

    def entails(self, p: MPAbstractP, gc: MPAbstractGC, gamma: MPAbstractGamma):
        if any(element.c.q.equals(MPGammaQ(self)) for element in p.elements) and p.wellFormed(gc, gamma):
            return True
        else:
            return MPQSubst([], [], self).entails(p, gc, gamma)

    def elaborate(self, gc):
        return IQ(self.tc.elaborate(gc))

    def getDictionary(self, p: MPAbstractP, gc: MPAbstractGC, gamma: MPAbstractGamma):
        if any(element.c.q.equals(MPGammaQ(self)) for element in p.elements) and p.wellFormed(gc, gamma):
            return gamma.getDeltaOfGammaQ(MPGammaQ(self))
        else:
            return MPQSubst([], [], self).getDictionary(p, gc, gamma)


class MPQSubst(MPAbstractQ):

    def __init__(self, tList: List[MPTau], aList: List[MPTypeA], q: MPAbstractQ):
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
        if isinstance(constraint, MPQSubst):
            q2New = deepcopy(constraint.q)
            q2New.substitute(self.tList, self.aList)
        else:
            q2New = constraint
        return q1New.equals(q2New)

    def substitute(self, tList: List[MPTau], aList: List[MPTypeA]):
        assert all(not any(a1.equals(a2) for a2 in aList) for a1 in self.aList)
        self.q.substitute(self.tList, self.aList)
        self.q.substitute(tList, aList)
        return self.q

    def entails(self, p: MPAbstractP, gc: MPAbstractGC, gamma: MPAbstractGamma):
        if any(element.c.q.equals(MPGammaQ(self)) for element in p.elements):
            return p.wellFormed(gc, gamma)
        else:
            try:
                qiList = p.getQiFromQ(self.q)
            except:
                q = deepcopy(self.q)
                q = q.substitute(self.tList, self.aList)
                qiList = p.getQiFromQ(q)
            return (all(t.wellTyped(gamma, gc) for t in self.tList)
                    and p.wellFormed(gc, gamma)
                    and all(MPQSubst(self.tList, self.aList, qi).entails(p, gc, gamma) for qi in qiList))

    def elaborate(self, gc):
        tList = list(map(lambda t: t.elaborate(gc), self.tList))
        aList = list(map(lambda a: a.elaborate(gc), self.aList))
        return IQSubst(tList, aList, self.q.elaborate(gc))

    def getDictionary(self, p: MPAbstractP, gc: MPAbstractGC, gamma: MPAbstractGamma):
        if any(element.c.q.equals(MPGammaQ(self)) for element in p.elements):
            delta = gamma.getDeltaOfGammaQ(MPGammaQ(self))
            return DictionaryDelta(delta)
        else:
            sj = list(map(lambda t: t.elaborate, self.tList))
            di = list(
                map(lambda q: MPQSubst(self.tList, self.aList, q).getDictionary(p, gc, gamma), p.getQiFromQ(self.q)))
            d = p.getDFromQ(self.q)
            return DictionarySigma(d, sj, di)


class MPC(MPAbstractC):
    def __init__(self, aList: List[MPTypeA], qList: List[MPQ], q: MPQ):
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

    def wellFormed(self, gamma: MPAbstractGamma, gc: MPAbstractGC):
        gammaNew = deepcopy(gamma)
        aj = list(map(lambda x: MPGammaA(x), self.aList))
        gammaNew.addElements(aj)
        return (all(not gamma.contains(a) for a in aj)
                and all(q.wellFormed(gammaNew, gc) for q in self.qList)
                and self.q.wellFormed(gammaNew, gc))

    def equals(self, constraint):
        return (isinstance(constraint, MPC)
                and self.q.equals(constraint.q)
                and len(self.aList) == len(constraint.aList)
                and all(any(a.equals(aj) for aj in constraint.aList) for a in self.aList)
                and len(self.qList) == len(constraint.qList)
                and all(any(q.equals(qj) for qj in constraint.qList) for q in self.qList))

    def unambiguous(self):
        fv = []
        for t in self.q.tc.tList:
            fv += t.getFreeVars()
        return all(any(aj.equals(a) for a in fv) for aj in self.aList)

    def elaborate(self, gc):
        aList = list(map(lambda a: a.elaborate(gc), self.aList))
        qList = list(map(lambda q: q.elaborate(gc), self.qList))
        return IC(aList, qList, self.q.elaborate(gc))
