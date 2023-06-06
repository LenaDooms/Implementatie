from copy import deepcopy
from typing import List

from IntermediateLanguage.Constraint.AbstractConstraint import IAbstractQ
from IntermediateLanguage.Types.AbstractType import ISigma


class ITypeA(ISigma):
    def __init__(self, a: str):
        super().__init__()
        self.a = a

    def show(self):
        print(self.a, end=' ')

    def equals(self, s: ISigma):
        return isinstance(s, ITypeA) and s.a == self.a

    def substitute(self, tList, aList):
        assert len(tList) == len(aList)
        for i in range(len(aList)):
            if self.equals(aList[i]):
                return tList[i]
        return self


class ITypeBool(ISigma):

    def show(self):
        print("Bool", end=' ')

    def equals(self, s: ISigma):
        return isinstance(s, ITypeBool)

    def substitute(self, tList, aList):
        return self


class ITypeArrow(ISigma):
    def __init__(self, s1: ISigma, s2: ISigma):
        super().__init__()
        self.s1 = s1
        self.s2 = s2

    def show(self):
        self.s1.show()
        print(" --> ", end=' ')
        self.s2.show()

    def equals(self, s: ISigma):
        return isinstance(s, ITypeArrow) and self.s1.equals(s.s1) and self.s2.equals(s.s2)

    def substitute(self, tList, aList):
        self.s1 = self.s1.substitute(tList, aList)
        self.s2 = self.s2.substitute(tList, aList)
        return self


class ITypeConstr(ISigma):

    def __init__(self, q: IAbstractQ, s: ISigma):
        super().__init__()
        self.q = q
        self.s = s

    def show(self):
        self.q.show()
        print(" => ", end=' ')
        self.s.show()

    def equals(self, s):
        return isinstance(s, ITypeConstr) and self.q.equals(s.q) and self.s.equals(s.s)

    def substitute(self, tList, aList):
        self.s = self.s.substitute(tList, aList)
        return self


class ITypeVar(ISigma):
    def __init__(self, a: ITypeA, s: ISigma):
        super().__init__()
        self.a = a
        self.s = s

    def show(self):
        print("Forall ", end=' ')
        self.a.show()
        print(". ", end=' ')
        self.s.show()

    def equals(self, s):
        return isinstance(s, ITypeVar) and self.a.equals(s.a) and self.s.equals(s.s)

    def substitute(self, tList, aList):
        assert not any(self.a.equals(a1) for a1 in aList)
        self.s = self.s.substitute(tList, aList)
        return self


class ITypeSubst(ISigma):
    def show(self):
        pass

    def equals(self, s):
        pass

    def __init__(self, tList: List[ISigma], aList: List[ITypeA], sigma: ISigma):
        super().__init__()
        self.tList = tList
        self.aList = aList
        self.sigma = sigma

    def substitute(self, tList, aList):
        assert all(not any(a1.equals(a2) for a2 in self.aList) for a1 in aList)
        self.sigma = self.sigma.substitute(tList, aList)
        return self.sigma

    def evaluate(self):
        evaluated = deepcopy(self)
        evaluated = evaluated.sigma.substitute(self.tList, self.aList)
        return evaluated
