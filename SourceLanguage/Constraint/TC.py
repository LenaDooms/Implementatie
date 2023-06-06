from abc import ABC, abstractmethod

from IntermediateLanguage.Constraint.TC import ITCA, ITCTau
from SourceLanguage.Types.AbstractTypes import Tau
from SourceLanguage.Types.Tau import TypeA


class TC(ABC):
    def __init__(self, name: str, t: Tau):
        self.name = name
        self.t = t

    def show(self):
        print(self.name + " ", end=' ')
        self.t.show()

    def getType(self):
        return self.t

    def getName(self):
        return self.name

    def equals(self, tc):
        return isinstance(tc, TC) and self.t.equals(tc.t) and self.name == tc.name

    @abstractmethod
    def elaborate(self):
        pass


class TcA(TC):
    def __init__(self, name: str, a: TypeA):
        super().__init__(name, a)

    def elaborate(self):
        return ITCA(self.name, self.t.elaborate())


class TcTau(TC):
    def __init__(self, name: str, t: Tau):
        super().__init__(name, t)

    def elaborate(self):
        return ITCTau(self.name, self.t.elaborate())
