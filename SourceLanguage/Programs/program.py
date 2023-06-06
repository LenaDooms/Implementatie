from abc import ABC, abstractmethod
from copy import deepcopy
from typing import List

from SourceLanguage.Environment.Element import GammaA, GCElem, GammaQ, PElem
from SourceLanguage.Environment.environment import P, GC, Gamma
from SourceLanguage.Terms.Term import Term
from SourceLanguage.Constraint.constraint import Q, C, QSubst
from SourceLanguage.Constraint.TC import TcA, TcTau
from SourceLanguage.Types.Rho import RhoConstr
from SourceLanguage.Types.Sigma import Sigma, SigmaForall
from SourceLanguage.Types.Tau import TypeSubst


class Inst:
    def __init__(self, qList: List[Q], tc: TcTau, m: str, e: Term):
        self.qList = qList
        self.tc = tc
        self.m = m
        self.e = e

    def show(self):
        print("instance ", end=" ")
        for q in self.qList:
            q.show()
            print(" => ")
        self.tc.show()
        print(" where { m = ", end=" ")
        self.e.show()
        print(" } ", end=" ")

    def addToP(self, p: P, gc: GC):
        tcA = gc.getTCFromMethod(self.m)
        assert tcA.name == self.tc.name
        tau = self.tc.t
        bk = tau.getFreeVars()
        bGamma = Gamma(list(map(lambda a: GammaA(a), bk)))
        assert tau.wellTyped(bGamma, gc)
        qq = gc.closure(self.qList)
        c = C(bk, qq, Q(self.tc))
        assert c.unambiguous()
        assert all(q.wellFormed(bGamma, gc) for q in qq)
        qi = gc.getTCListFromMethod(self.m)
        bqGamma = deepcopy(bGamma)
        bqGamma.elements = deepcopy(bGamma.elements)
        bqGamma.addElements(list(map(lambda q: GammaQ(q), qq)))
        assert all(QSubst([tau], [tcA.t], Q(q)).entails(p, gc, bqGamma) for q in qi)
        gammaNew = deepcopy(bqGamma)
        gammaNew.elements = deepcopy(bqGamma.elements)
        sigma = gc.getSigmaFromMethod(self.m)
        gammaNew.addElements(list(map(lambda a: GammaA(a), sigma.getVariables())))
        gammaNew.addElements(list(map(lambda q: GammaQ(QSubst([tau], [tcA.t], q)), sigma.getConstraints())))
        assert self.e.hasType(p, gc, gammaNew, TypeSubst([tau], [tcA.t], sigma.getTau()))
        assert all(element.c.q.tc.name != tcA.name or not tau.equalsWithVars(bk, element.c.q.tc.t, element.c.aList) for element in p.elements)
        pElem = PElem(c, self.m, gammaNew, self.e)
        p.addElement(pElem)


class Cls:
    def __init__(self, tcList: List[TcA], tc: TcA, m: str, sigma: Sigma):
        self.tcList = tcList
        self.tc = tc
        self.m = m
        self.sigma = sigma

    def show(self):
        print("class ", end=" ")
        for tc in self.tcList:
            tc.show()
            print(" => ")
        self.tc.show()
        print(" where { m : ", end=" ")
        self.sigma.show()
        print(" } ", end=" ")

    def addToGC(self, gc: GC):
        assert all(element.m != self.m for element in gc.elements)
        assert all(element.tc.name != self.tc.name for element in gc.elements)
        qp = gc.closure(self.sigma.getConstraints())
        sigmaNew = SigmaForall(self.sigma.getVariables(), RhoConstr(qp, self.sigma.getTau()))
        a = self.tc.t
        assert sigmaNew.wellTyped(Gamma([GammaA(a)]), gc)
        sigmaA = deepcopy(sigmaNew)
        sigmaA.aList.append(a)
        assert sigmaA.unambiguous()
        assert all(Q(tc).wellFormed(Gamma([GammaA(a)]), gc) for tc in self.tcList)
        gcElem = GCElem(self.m, self.tcList, self.tc, sigmaNew)
        gc.addElement(gcElem)


class Pgm(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def show(self):
        pass

    @abstractmethod
    def getType(self, p: P, gc: GC):
        pass

    @abstractmethod
    def elaborate(self, p: P, gc: GC):
        pass


class PgmE(Pgm):
    def __init__(self, e: Term):
        super().__init__()
        self.e = e

    def show(self):
        self.e.show()

    def getType(self, p: P, gc: GC):
        result = self.e.getType(p, gc, Gamma([]))
        if isinstance(result, TypeSubst):
            result = result.evaluate()
        return result

    def elaborate(self, p: P, gc: GC):
        return self.e.elaborate(p, gc, Gamma([]))


class PgmInst(Pgm):
    def __init__(self, inst: Inst, pgm: Pgm):
        super().__init__()
        self.inst = inst
        self.pgm = pgm

    def show(self):
        self.inst.show()
        print("; ", end=" ")
        self.pgm.show()

    def getType(self, p: P, gc: GC):
        self.inst.addToP(p, gc)
        return self.pgm.getType(p, gc)

    def elaborate(self, p: P, gc: GC):
        self.inst.addToP(p, gc)
        return self.pgm.elaborate(p, gc)


class PgmCls(Pgm):
    def __init__(self, cls: Cls, pgm: Pgm):
        super().__init__()
        self.cls = cls
        self.pgm = pgm

    def show(self):
        self.cls.show()
        print("; ", end=" ")
        self.pgm.show()

    def getType(self, p: P, gc: GC):
        self.cls.addToGC(gc)
        return self.pgm.getType(p, gc)

    def elaborate(self, p: P, gc: GC):
        self.cls.addToGC(gc)
        return self.pgm.elaborate(p, gc)
