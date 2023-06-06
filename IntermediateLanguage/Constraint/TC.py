from abc import ABC

from IntermediateLanguage.Types.AbstractType import ISigma
from IntermediateLanguage.Types.Sigma import ITypeA


class ITC(ABC):
    def __init__(self, name: str, t: ISigma):
        self.name = name
        self.t = t

    def show(self):
        print(self.name + " ", end=' ')
        self.t.show()

    def equals(self, tc):
        return isinstance(tc, ITC) and self.t.equals(tc.t) and self.name == tc.name


class ITCA(ITC):
    def __init__(self, name: str, a: ITypeA):
        super().__init__(name, a)


class ITCTau(ITC):
    def __init__(self, name: str, t: ISigma):
        super().__init__(name, t)
