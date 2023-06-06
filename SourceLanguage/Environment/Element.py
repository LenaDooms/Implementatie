from typing import List

from IntermediateLanguage.Environment.Element import IGammaX, IGammaA, IGammaQ, IGCElem
from SourceLanguage.Constraint.AbstractConstraint import AbstractQ, AbstractC
from SourceLanguage.Constraint.TC import TcA
from SourceLanguage.Environment.AbstractElement import GammaElem, PElemAbstract, GCElemAbstract
from SourceLanguage.Environment.AbstractEnvironment import AbstractGamma
from SourceLanguage.Terms.AbstractTerm import Term
from SourceLanguage.Types.AbstractTypes import Sigma
from SourceLanguage.Types.Tau import TypeA


class GammaX(GammaElem):
    def __init__(self, x: str, sigma: Sigma):
        super().__init__()
        self.x = x
        self.sigma = sigma

    def show(self):
        print(self.x + " : ", end=' ')
        self.sigma.show()

    def equals(self, element: GammaElem):
        return isinstance(element, GammaX) and self.x == element.x and self.sigma.equals(element.sigma)

    def elaborate(self):
        return IGammaX(self.x, self.sigma.elaborate())


class GammaA(GammaElem):
    def __init__(self, a: TypeA):
        super().__init__()
        self.a = a

    def show(self):
        self.a.show()

    def equals(self, element: GammaElem):
        return isinstance(element, GammaA) and self.a.equals(element.a)

    def elaborate(self):
        return IGammaA(self.a.elaborate())


class GammaQ(GammaElem):
    def __init__(self, q: AbstractQ):
        super().__init__()
        self.q = q

    def show(self):
        self.q.show()

    def equals(self, element: GammaElem):
        return isinstance(element, GammaQ) and self.q.equals(element.q)

    def elaborate(self):
        return IGammaQ(self.q.elaborate())


class GCElem(GCElemAbstract):
    def __init__(self, m: str, tcList: List[TcA], tc: TcA, sigma: Sigma):
        super().__init__(m, tcList, tc, sigma)

    def show(self):
        self.m.show()
        print(" : ", end=' ')
        for tc in self.tcList:
            tc.show()
            print(" => ")
        self.tc.show()
        print(" : ", end=' ')
        self.sigma.show()

    def equals(self, element: GCElemAbstract):
        return (isinstance(element, GCElem)
                and self.m == element.m
                and len(self.tcList) == len(element.tcList)
                and all(any(tci1.equals(tci2) for tci2 in element.tcList) for tci1 in self.tcList)
                and self.tc.equals(element.tc)
                and self.sigma.equals(element.sigma))

    def elaborate(self):
        return IGCElem(self.m, self.tc.elaborate(), self.sigma.elaborate())


class PElem(PElemAbstract):
    def __init__(self, c: AbstractC, m: str, gamma: AbstractGamma, e: Term):
        super().__init__(c, m, gamma, e)

    def show(self):
        print("(", end='')
        self.c.show()
        print(").", end='')
        self.m.show()
        print(" |-> ", end=' ')
        self.gamma.show()
        print(" : ", end=' ')
        self.e.show()

    def equals(self, element: PElemAbstract):
        return (isinstance(element, PElem)
                and self.m == element.m
                and self.c.equals(element.c)
                and self.e.equals(element.e)
                and len(self.gamma.elements) == len(element.gamma.elements)
                and all(
                    self.gamma.elements[i].equals(element.gamma.elements[i]) for i in range(len(self.gamma.elements))))
