from IntermediateLanguage.Constraint.constraint import IQ
from IntermediateLanguage.Dictionaries.Dictionary import Dictionary, DictionaryDelta
from IntermediateLanguage.Terms.AbstractTerm import ITerm, IValue
from IntermediateLanguage.Types.AbstractType import ISigma
from IntermediateLanguage.Types.Sigma import ITypeA


class ITermTrue(IValue):
    def show(self):
        print("True", end='')

    def equals(self, e: ITerm):
        return isinstance(e, ITermTrue)


class ITermFalse(IValue):

    def show(self):
        print("False", end='')

    def equals(self, e: ITerm):
        return isinstance(e, ITermFalse)


class ITermX(ITerm):
    def __init__(self, x: str):
        super().__init__()
        self.x = x

    def show(self):
        print(self.x, end='')

    def equals(self, e: ITerm):
        return isinstance(e, ITermX) and self.x == e.x


class ITermM(ITerm):
    def __init__(self, d: Dictionary, m: str):
        super().__init__()
        self.d = d
        self.m = m

    def show(self):
        self.d.show()
        print(self.m, end='')

    def equals(self, e: ITerm):
        return isinstance(e, ITermM) and self.m == e.m and self.d.equals(e.d)


class ITermAbs(IValue):
    def __init__(self, x: str, sigma: ISigma, e: ITerm):
        super().__init__()
        self.x = x
        self.sigma = sigma
        self.e = e

    def show(self):
        print("\\" + self.x + ". ", end='')
        self.sigma.show()
        print(". ", end='')
        self.e.show()

    def equals(self, e: ITerm):
        return isinstance(e, ITermAbs) and self.x == e.x and self.e.equals(e.e) and self.sigma.equals(e.sigma)


class ITermApp(ITerm):
    def __init__(self, e1: ITerm, e2: ITerm):
        super().__init__()
        self.e1 = e1
        self.e2 = e2

    def show(self):
        self.e1.show()
        self.e2.show()

    def equals(self, e: ITerm):
        return isinstance(e, ITermApp) and self.e1.equals(e.e1) and self.e2.equals(e.e2)


class ITermLet(ITerm):
    def __init__(self, x: str, sigma: ISigma, e1: ITerm, e2: ITerm):
        super().__init__()
        self.x = x
        self.sigma = sigma
        self.e1 = e1
        self.e2 = e2

    def show(self):
        print("Let " + self.x + " : ", end=' ')
        self.sigma.show()
        print(" = ", " ")
        self.e1.show()
        print(" in ", end='')
        self.e2.show()

    def equals(self, e: ITerm):
        return isinstance(e, ITermLet) and self.x == e.x and self.sigma.equals(e.sigma) and self.e1.equals(
            e.e1) and self.e2.equals(e.e2)


class ITermQAbs(IValue):
    def __init__(self, d: DictionaryDelta, q: IQ, e: ITerm):
        super().__init__()
        self.d = d
        self.q = q
        self.e = e

    def show(self):
        print("\\", end='')
        self.d.show()
        print(" : ", end='')
        self.q.show()
        print(". ", end='')
        self.e.show()

    def equals(self, e: ITerm):
        return isinstance(e, ITermQAbs) and self.d.equals(e.d) and self.e.equals(e.e) and self.q.equals(e.q)


class ITermTypeAbs(IValue):
    def __init__(self, a: ITypeA, e: ITerm):
        super().__init__()
        self.a = a
        self.e = e

    def show(self):
        print("/\\", end='')
        self.a.show()
        print(". ", end='')
        self.e.show()

    def equals(self, e: ITerm):
        return isinstance(e, ITermTypeAbs) and self.a.equals(e.a) and self.e.equals(e.e)


class ITermED(ITerm):
    def __init__(self, e: ITerm, d: Dictionary):
        super().__init__()
        self.e = e
        self.d = d

    def show(self):
        self.e.show()
        self.d.show()

    def equals(self, e):
        return isinstance(e, ITermED) and self.e.equals(e.e) and self.d.equals(e.d)


class ITermESigma(ITerm):
    def __init__(self, e: ITerm, s: ISigma):
        super().__init__()
        self.e = e
        self.s = s

    def show(self):
        self.e.show()
        self.s.show()

    def equals(self, e):
        return isinstance(e, ITermESigma) and self.e.equals(e.e) and self.s.equals(e.s)
