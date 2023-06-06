from typing import List

from IntermediateLanguage.Constraint.constraint import IQ, IC, IQSubst
from IntermediateLanguage.Dictionaries.Dictionary import DictionaryDelta, DictionarySigma
from SourceLanguage.Constraint.AbstractConstraint import AbstractQ, AbstractC
from SourceLanguage.Constraint.TC import TC
from SourceLanguage.Environment.AbstractEnvironment import AbstractGamma, AbstractGC, AbstractP
from SourceLanguage.Environment.Element import GammaA, GammaQ
from SourceLanguage.Types.AbstractTypes import Tau
from SourceLanguage.Types.Tau import TypeA
from copy import deepcopy


class Q(AbstractQ):
    def __init__(self, tc: TC):
        super().__init__()
        self.tc = tc

    def show(self):
        self.tc.show()

    def wellFormed(self, gamma: AbstractGamma, gc: AbstractGC):
        sigma = gc.getSigmaFromName(self.tc.name)
        gc1 = gc.getGC1FromName(self.tc.name)
        a = gc.getAFromName(self.tc.name)
        gammaNew = deepcopy(gamma)
        gammaNew.elements = deepcopy(gamma.elements)
        gammaNew.setElements([GammaA(a)])
        return self.tc.getType().wellTyped(gamma, gc) and sigma.wellTyped(gammaNew, gc1)

    def equals(self, constraint):
        return isinstance(constraint, Q) and self.tc.equals(constraint.tc)

    def substitute(self, tList: List[Tau], aList: List[TypeA]):
        for i in range(len(aList)):
            if self.tc.t.equals(aList[i]):
                self.tc.t = tList[i]
                return

    def entails(self, p: AbstractP, gc: AbstractGC, gamma: AbstractGamma):
        if any(element.c.q.equals(GammaQ(self)) for element in p.elements) and p.wellFormed(gc, gamma):
            return True
        else:
            return QSubst([], [], self).entails(p, gc, gamma)

    def elaborate(self):
        return IQ(self.tc.elaborate())

    def getDictionary(self, p: AbstractP, gc: AbstractGC, gamma: AbstractGamma):
        if any(element.c.q.equals(GammaQ(self)) for element in p.elements) and p.wellFormed(gc, gamma):
            return gamma.getDeltaOfGammaQ(GammaQ(self))
        else:
            return QSubst([], [], self).getDictionary(p, gc, gamma)


class QSubst(AbstractQ):

    def __init__(self, tList: List[Tau], aList: List[TypeA], q: AbstractQ):
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
        if isinstance(constraint, QSubst):
            q2New = deepcopy(constraint.q)
            q2New.substitute(self.tList, self.aList)
        else:
            q2New = constraint
        return q1New.equals(q2New)

    def substitute(self, tList: List[Tau], aList: List[TypeA]):
        assert all(not any(a1.equals(a2) for a2 in aList) for a1 in self.aList)
        self.q.substitute(self.tList, self.aList)
        self.q.substitute(tList, aList)
        return self.q

    def entails(self, p: AbstractP, gc: AbstractGC, gamma: AbstractGamma):
        if any(element.c.q.equals(GammaQ(self)) for element in p.elements):
            return p.wellFormed(gc, gamma)
        else:
            qiList = p.getQiFromQ(self.q)
            return (all(t.wellTyped(gamma, gc) for t in self.tList)
                    and p.wellFormed(gc, gamma)
                    and all(QSubst(self.tList, self.aList, qi).entails(p, gc, gamma) for qi in qiList))

    def evaluate(self):
        evaluated = deepcopy(self)
        evaluated = evaluated.q.substitute(self.aList, self.tList)
        return evaluated

    def elaborate(self):
        tList = list(map(lambda t: t.elaborate(), self.tList))
        aList = list(map(lambda a: a.elaborate(), self.aList))
        return IQSubst(tList, aList, self.q.elaborate())

    def getDictionary(self, p: AbstractP, gc: AbstractGC, gamma: AbstractGamma):
        if any(element.c.q.equals(GammaQ(self)) for element in p.elements):
            delta = gamma.getDeltaOfGammaQ(GammaQ(self))
            return DictionaryDelta(delta)
        else:
            sj = list(map(lambda t: t.elaborate, self.tList))
            di = list(map(lambda q: QSubst(self.tList, self.aList, q).getDictionary(p, gc, gamma), p.getQiFromQ(self.q)))
            d = p.getDFromQ(self.q)
            return DictionarySigma(d, sj, di)


class C(AbstractC):
    def __init__(self, aList: List[TypeA], qList: List[Q], q: Q):
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

    def wellFormed(self, gamma: AbstractGamma, gc: AbstractGC):
        gammaNew = deepcopy(gamma)
        gammaNew.elements = deepcopy(gamma.elements)
        aj = list(map(lambda x: GammaA(x), self.aList))
        gammaNew.addElements(aj)
        return (all(not gamma.contains(a) for a in aj)
                and all(q.wellFormed(gammaNew, gc) for q in self.qList)
                and self.q.wellFormed(gammaNew, gc))

    def equals(self, constraint):
        return (isinstance(constraint, C)
                and self.q.equals(constraint.q)
                and len(self.aList) == len(constraint.aList)
                and all(any(a.equals(aj) for aj in constraint.aList) for a in self.aList)
                and len(self.qList) == len(constraint.qList)
                and all(any(q.equals(qj) for qj in constraint.qList) for q in self.qList))

    def unambiguous(self):
        fv = self.q.tc.t.getFreeVars()
        return all(any(aj.equals(a) for a in fv) for aj in self.aList)

    def elaborate(self):
        return IC(list(map(lambda a: a.elaborate, self.aList)), list(map(lambda q: q.elaborate, self.qList)), self.q.elaborate())
