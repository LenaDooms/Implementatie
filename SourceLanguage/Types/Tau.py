from copy import deepcopy
from typing import List

from IntermediateLanguage.Types.Sigma import ITypeBool, ITypeArrow, ITypeA
from SourceLanguage.Environment.AbstractEnvironment import AbstractGamma, AbstractGC
from SourceLanguage.Types.AbstractTypes import Tau, Sigma


class TypeA(Tau):
    def __init__(self, a: str):
        super().__init__()
        self.a = a

    def show(self):
        print(self.a, end=' ')

    def wellTyped(self, gamma: AbstractGamma, gc: AbstractGC):
        return gamma.containsTypeVar(self)

    def equals(self, t: Sigma):
        tau = t.getTau()
        if isinstance(tau, TypeSubst):
            tau = tau.evaluate()
        return (len(t.getVariables()) == 0 and len(t.getConstraints()) == 0
                and isinstance(tau, TypeA) and tau.a == self.a)

    def substitute(self, aList, tList):
        assert len(aList) == len(tList)
        for i in range(len(aList)):
            if self.equals(aList[i]):
                return tList[i]
        return self

    def equalsWithVars(self, aList, tau: Tau, bList):
        return (any(self.equals(a) for a in aList)
                or (isinstance(tau, TypeA) and any(tau.equals(b) for b in bList))
                or self.equals(tau))

    def getTau(self):
        return self

    def getRho(self):
        return self

    def getFreeVars(self):
        return [self]

    def unambiguous(self):
        return True

    def elaborate(self):
        return ITypeA(self.a)


class TypeBool(Tau):

    def show(self):
        print("Bool", end=' ')

    def wellTyped(self, gamma: AbstractGamma, gc: AbstractGC):
        return True

    def equals(self, t: Sigma):
        tau = t.getTau()
        if isinstance(tau, TypeSubst):
            tau = tau.evaluate()
        return (len(t.getVariables()) == 0 and len(t.getConstraints()) == 0
                and isinstance(tau, TypeBool))

    def substitute(self, aList: List[TypeA], tList: List[Tau]):
        return self

    def equalsWithVars(self, aList: List[TypeA], tau: Tau, bList: List[TypeA]):
        return ((isinstance(tau, TypeA) and any(tau.equals(b) for b in bList))
                or self.equals(tau))

    def getTau(self):
        return self

    def getRho(self):
        return self

    def getFreeVars(self):
        return []

    def unambiguous(self):
        return True

    def elaborate(self):
        return ITypeBool()


class TypeArrow(Tau):
    def __init__(self, t1: Tau, t2: Tau):
        super().__init__()
        self.t1 = t1
        self.t2 = t2

    def show(self):
        self.t1.show()
        print(" --> ", end=' ')
        self.t2.show()

    def wellTyped(self, gamma: AbstractGamma, gc: AbstractGC):
        return self.t1.wellTyped(gamma, gc) and self.t2.wellTyped(gamma, gc)

    def equals(self, t: Sigma):
        tau = t.getTau()
        if isinstance(tau, TypeSubst):
            tau = tau.evaluate()
        return (len(t.getVariables()) == 0 and len(t.getConstraints()) == 0
                and isinstance(tau, TypeArrow) and self.t1.equals(tau.t1) and self.t2.equals(tau.t2))

    def substitute(self, aList, tList):
        self.t1 = self.t1.substitute(aList, tList)
        self.t2 = self.t2.substitute(aList, tList)
        return self

    def equalsWithVars(self, aList: List[TypeA], tau: Tau, bList: List[TypeA]):
        return ((isinstance(tau, TypeArrow) and self.t1.equalsWithVars(aList, tau.t1, bList) and self.t2.equalsWithVars(
            aList, tau.t2, bList))
                or (isinstance(tau, TypeA) and any(tau.equals(b) for b in bList))
                or self.equals(tau))

    def getTau(self):
        return self

    def getRho(self):
        return self

    def getFreeVars(self):
        return self.t1.getFreeVars() + self.t2.getFreeVars()

    def unambiguous(self):
        return self.t1.unambiguous() and self.t2.unambiguous()

    def elaborate(self):
        return ITypeArrow(self.t1.elaborate(), self.t2.elaborate())


class TypeSubst(Tau):

    def __init__(self, tList: List[Tau], aList: List[TypeA], tau: Tau):
        super().__init__()
        assert len(tList) == len(aList)
        self.aList = aList
        self.tList = tList
        self.tau = tau

    def show(self):
        print("[ ", end=" ")
        for t in self.tList:
            t.show()
            print(", ", end=' ')
        print(" / ", end=' ')
        for a in self.aList:
            a.show()
            print(", ", end=' ')
        print(" ] ", end=' ')
        self.tau.show()

    def wellTyped(self, gamma, gc):
        newTau = deepcopy(self.tau)
        newTau.substitute(self.aList, self.tList)
        return newTau.wellTyped(gamma, gc)

    def equals(self, t: Sigma):
        if len(t.getVariables()) != 0 or len(t.getConstraints()) != 0:
            return False
        tau = t.getTau()
        if isinstance(tau, TypeSubst):
            return (len(self.tList) == len(tau.tList)
                    and all(any(t1.equals(t2) for t2 in tau.tList) for t1 in self.tList)
                    and all(any(a1.equals(a2) for a2 in tau.aList) for a1 in self.aList)
                    and tau.tau.equals(self.tau)
                    )
        else:
            return tau.equals(self.evaluate())

    def substitute(self, aList, tList):
        assert all(not any(a1.equals(a2) for a2 in self.aList) for a1 in aList)
        self.tau = self.tau.substitute(aList + self.aList, tList + self.tList)
        return self.tau

    def equalsWithVars(self, aList: List[TypeA], tau: Tau, bList: List[TypeA]):
        tauSubstituted = deepcopy(self.tau)
        tauSubstituted.substitute(self.aList, self.tList)
        return ((isinstance(tau, TypeA) and any(tau.equals(b) for b in bList))
                or self.equals(tau)
                or tauSubstituted.equalsWithVars(aList, tau, bList))

    def evaluate(self):
        evaluated = deepcopy(self)
        evaluated = evaluated.tau.substitute(self.aList, self.tList)
        return evaluated

    def getTau(self):
        return self

    def getRho(self):
        return self

    def getFreeVars(self):
        tauNew = deepcopy(self.tau)
        tauNew.substitute(self.aList, self.tList)
        return tauNew.getFreeVars()

    def unambiguous(self):
        tauNew = deepcopy(self.tau)
        tauNew.substitute(self.aList, self.tList)
        return tauNew.unambiguous()

    def elaborate(self):
        t = self.evaluate()
        return t.elaborate()
