from typing import List

from IntermediateLanguage.Constraint.TC import ITCA
from IntermediateLanguage.Environment.Element import IGCElem, IGammaX, IGammaA, IGammaQ
from IntermediateLanguage.Types.Sigma import ITypeA
from SourceLanguageFD.Constraint.AbstractConstraint import FDAbstractQ, FDAbstractC
from SourceLanguageFD.Constraint.TC import FDTCA
from SourceLanguageFD.Environment.AbstractElement import FDGammaElem, FDPElemAbstract, FDGCElemAbstract
from SourceLanguageFD.Environment.AbstractEnvironment import FDAbstractGamma
from SourceLanguageFD.Programs.FD import FD
from SourceLanguageFD.Terms.AbstractTerm import FDTerm
from SourceLanguageFD.Types.AbstractTypes import FDSigma
from SourceLanguageFD.Types.Tau import FDTypeA


class FDGammaX(FDGammaElem):
    def __init__(self, x: str, sigma: FDSigma):
        super().__init__()
        self.x = x
        self.sigma = sigma

    def show(self):
        print(self.x + " : ", end=' ')
        self.sigma.show()

    def equals(self, element: FDGammaElem):
        return isinstance(element, FDGammaX) and self.x == element.x and self.sigma.equals(element.sigma)

    def elaborate(self, p, gc):
        return IGammaX(self.x, self.sigma.elaborate(p, gc))


class FDGammaA(FDGammaElem):
    def __init__(self, a: FDTypeA):
        super().__init__()
        self.a = a

    def show(self):
        self.a.show()

    def equals(self, element: FDGammaElem):
        return isinstance(element, FDGammaA) and self.a.equals(element.a)

    def elaborate(self, p, gc):
        return IGammaA(self.a.elaborate(p, gc))


class FDGammaQ(FDGammaElem):
    def __init__(self, q: FDAbstractQ):
        super().__init__()
        self.q = q

    def show(self):
        self.q.show()

    def equals(self, element: FDGammaElem):
        return isinstance(element, FDGammaQ) and self.q.equals(element.q)

    def elaborate(self, p, gc):
        return IGammaQ(self.q.elaborate(p, gc))


class FDGCElem(FDGCElemAbstract):
    def __init__(self, m: str, tcList: List[FDTCA], tc: FDTCA, sigma: FDSigma, fd: FD):
        super().__init__(m, tcList, tc, sigma, fd)

    def show(self):
        self.m.show()
        print(" : ", end=' ')
        for tc in self.tcList:
            tc.show()
            print(" => ")
        self.tc.show()
        print(" : ", end=' ')
        self.sigma.show()
        print(" | [ ", end=' ')
        for a in self.fd.aList1:
            a.show()
        print(" ] ~> [ ", end=" ")
        for a in self.fd.aList2:
            a.show()
        print(" ] ", end=" ")

    def equals(self, element: FDGCElemAbstract):
        return (isinstance(element, FDGCElem)
                and self.m == element.m
                and len(self.tcList) == len(element.tcList)
                and all(any(tci1.equals(tci2) for tci2 in element.tcList) for tci1 in self.tcList)
                and self.tc.equals(element.tc)
                and self.sigma.equals(element.sigma)
                and self.fd.equals(element.fd))

    def elaborate(self, gc):
        return IGCElem(self.m, ITCA(self.tc.name, ITypeA("a")), ITypeA("a"))


class FDPElem(FDPElemAbstract):
    def __init__(self, c: FDAbstractC, m: str, gamma: FDAbstractGamma, e: FDTerm):
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

    def equals(self, element: FDPElemAbstract):
        return (isinstance(element, FDPElem)
                and self.m == element.m
                and self.c.equals(element.c)
                and self.e.equals(element.e)
                and len(self.gamma.elements) == len(element.gamma.elements)
                and all(self.gamma.elements[i].equals(element.gamma.elements[i]) for i in range(len(self.gamma.elements))))
