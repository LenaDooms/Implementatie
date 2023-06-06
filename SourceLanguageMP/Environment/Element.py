from typing import List

from IntermediateLanguage.Constraint.TC import ITCA
from IntermediateLanguage.Environment.Element import IGCElem, IGammaX, IGammaA, IGammaQ
from IntermediateLanguage.Types.Sigma import ITypeA
from SourceLanguageMP.Constraint.AbstractConstraint import MPAbstractQ, MPAbstractC
from SourceLanguageMP.Constraint.TC import MPTCA
from SourceLanguageMP.Environment.AbstractElement import MPGammaElem, MPPElemAbstract, MPGCElemAbstract
from SourceLanguageMP.Environment.AbstractEnvironment import MPAbstractGamma
from SourceLanguageMP.Terms.AbstractTerm import MPTerm
from SourceLanguageMP.Types.AbstractTypes import MPSigma
from SourceLanguageMP.Types.Tau import MPTypeA


class MPGammaX(MPGammaElem):
    def __init__(self, x: str, sigma: MPSigma):
        super().__init__()
        self.x = x
        self.sigma = sigma

    def show(self):
        print(self.x + " : ", end=' ')
        self.sigma.show()

    def equals(self, element: MPGammaElem):
        return isinstance(element, MPGammaX) and self.x == element.x and self.sigma.equals(element.sigma)

    def elaborate(self, gc):
        return IGammaX(self.x, self.sigma.elaborate(gc))


class MPGammaA(MPGammaElem):
    def __init__(self, a: MPTypeA):
        super().__init__()
        self.a = a

    def show(self):
        self.a.show()

    def equals(self, element: MPGammaElem):
        return isinstance(element, MPGammaA) and self.a.equals(element.a)

    def elaborate(self, gc):
        return IGammaA(self.a.elaborate(gc))


class MPGammaQ(MPGammaElem):
    def __init__(self, q: MPAbstractQ):
        super().__init__()
        self.q = q

    def show(self):
        self.q.show()

    def equals(self, element: MPGammaElem):
        return isinstance(element, MPGammaQ) and self.q.equals(element.q)

    def elaborate(self, gc):
        return IGammaQ(self.q.elaborate(gc))


class MPGCElem(MPGCElemAbstract):
    def __init__(self, m: str, tcList: List[MPTCA], tc: MPTCA, sigma: MPSigma):
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

    def equals(self, element: MPGCElemAbstract):
        return (isinstance(element, MPGCElem)
                and self.m == element.m
                and len(self.tcList) == len(element.tcList)
                and all(any(tci1.equals(tci2) for tci2 in element.tcList) for tci1 in self.tcList)
                and self.tc.equals(element.tc)
                and self.sigma.equals(element.sigma))

    def elaborate(self, gc):
        return IGCElem(self.m, ITCA(self.tc.name, ITypeA("a")), ITypeA("a"))


class MPPElem(MPPElemAbstract):
    def __init__(self, c: MPAbstractC, m: str, gamma: MPAbstractGamma, e: MPTerm):
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

    def equals(self, element: MPPElemAbstract):
        return (isinstance(element, MPPElem)
                and self.m == element.m
                and self.c.equals(element.c)
                and self.e.equals(element.e)
                and len(self.gamma.elements) == len(element.gamma.elements)
                and all(self.gamma.elements[i].equals(element.gamma.elements[i]) for i in range(len(self.gamma.elements))))
