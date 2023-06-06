from IntermediateLanguage.Constraint.AbstractConstraint import IAbstractQ, IAbstractC
from IntermediateLanguage.Constraint.TC import ITCA
from IntermediateLanguage.Environment.AbstractElement import IGammaElem, IPElemAbstract, IGCElemAbstract
from IntermediateLanguage.Terms.AbstractTerm import ITerm
from IntermediateLanguage.Types.AbstractType import ISigma
from IntermediateLanguage.Types.Sigma import ITypeA


class IGammaX(IGammaElem):
    def __init__(self, x: str, sigma: ISigma):
        super().__init__()
        self.x = x
        self.sigma = sigma

    def show(self):
        print(self.x + " : ", end=' ')
        self.sigma.show()

    def equals(self, element: IGammaElem):
        return isinstance(element, IGammaX) and self.x == element.x and self.sigma.equals(element.sigma)


class IGammaA(IGammaElem):
    def __init__(self, a: ITypeA):
        super().__init__()
        self.a = a

    def show(self):
        self.a.show()

    def equals(self, element: IGammaElem):
        return isinstance(element, IGammaA) and self.a.equals(element.a)


class IGammaQ(IGammaElem):
    def __init__(self, q: IAbstractQ):
        super().__init__()
        self.q = q

    def show(self):
        self.q.show()

    def equals(self, element: IGammaElem):
        return isinstance(element, IGammaQ) and self.q.equals(element.q)


class IGCElem(IGCElemAbstract):
    def __init__(self, m: str, tc: ITCA, sigma: ISigma):
        super().__init__(m, tc, sigma)

    def show(self):
        self.m.show()
        print(" : ", end=' ')
        self.tc.show()
        print(" : ", end=' ')
        self.sigma.show()

    def equals(self, element: IGCElemAbstract):
        return (isinstance(element, IGCElem)
                and self.m == element.m
                and self.tc.equals(element.tc)
                and self.sigma.equals(element.sigma))


class IPElem(IPElemAbstract):
    def __init__(self, c: IAbstractC, m: str, e: ITerm):
        super().__init__(c, m, e)

    def show(self):
        print("(", end='')
        self.c.show()
        print(").", end='')
        self.m.show()
        print(" |-> ", end=' ')
        self.e.show()

    def equals(self, element: IPElemAbstract):
        return (isinstance(element, IPElem)
                and self.m == element.m
                and self.c.equals(element.c)
                and self.e.equals(element.e))
