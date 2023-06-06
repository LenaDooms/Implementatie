from typing import List

from IntermediateLanguage.Constraint.AbstractConstraint import IAbstractQ, IAbstractC
from IntermediateLanguage.Constraint.TC import ITC
from IntermediateLanguage.Types.AbstractType import ISigma
from IntermediateLanguage.Types.Sigma import ITypeA
from copy import deepcopy


class IQ(IAbstractQ):
    def __init__(self, tc: ITC):
        super().__init__()
        self.tc = tc

    def show(self):
        self.tc.show()

    def equals(self, constraint):
        return isinstance(constraint, IQ) and self.tc.equals(constraint.tc)

    def substitute(self, tList: List[ISigma], aList: List[ITypeA]):
        for i in range(len(aList)):
            if self.tc.t.equals(aList[i]):
                self.tc.t = tList[i]
                return


class IQSubst(IAbstractQ):

    def __init__(self, tList: List[ISigma], aList: List[ITypeA], q: IAbstractQ):
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

    def equals(self, constraint):
        if isinstance(constraint, IQSubst):
            q1New = deepcopy(self.q)
            q1New.substitute(self.tList, self.aList)
            q2New = deepcopy(constraint.q)
            q2New.substitute(self.tList, self.aList)
            return q1New.equals(q2New)
        return False

    def substitute(self, tList: List[ISigma], aList: List[ITypeA]):
        assert all(not any(a1.equals(a2) for a2 in aList) for a1 in self.aList)
        self.q.substitute(self.tList, self.aList)
        self.q.substitute(tList, aList)
        return self.q


class IC(IAbstractC):
    def __init__(self, aList: List[ITypeA], qList: List[IQ], q: IQ):
        super().__init__()
        self.aList = aList
        self.qList = qList
        self.q = q

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

    def equals(self, constraint):
        return (isinstance(constraint, IC)
                and self.q.equals(constraint.q)
                and len(self.aList) == len(constraint.aList)
                and all(any(a.equals(aj) for aj in constraint.aList) for a in self.aList)
                and len(self.qList) == len(constraint.qList)
                and all(any(q.equals(qj) for qj in constraint.qList) for q in self.qList))
