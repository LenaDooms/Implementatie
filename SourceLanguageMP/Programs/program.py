from abc import ABC, abstractmethod
from copy import deepcopy
from typing import List

from SourceLanguageMP.Environment.Element import MPGammaA, MPGCElem, MPGammaQ, MPPElem
from SourceLanguageMP.Environment.environment import MPP, MPGC, MPGamma
from SourceLanguageMP.Terms.Term import MPTerm
from SourceLanguageMP.Constraint.constraint import MPQ, MPC, MPQSubst
from SourceLanguageMP.Constraint.TC import MPTCA, MPTCTau
from SourceLanguageMP.Types.Rho import MPRhoConstr
from SourceLanguageMP.Types.Sigma import MPSigma, MPSigmaForall
from SourceLanguageMP.Types.Tau import MPTypeSubst


class MPInst:
    def __init__(self, qList: List[MPQ], tc: MPTCTau, m: str, e: MPTerm):
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

    def addToP(self, p: MPP, gc: MPGC):
        tcA = gc.getTCFromMethod(self.m)
        assert len(self.tc.tList) == len(tcA.tList)
        assert tcA.name == self.tc.name
        assert len(tcA.tList) == len(self.tc.tList)
        tList = self.tc.tList
        bk = []
        for t in tList:
            bk += t.getFreeVars()
        bGamma = MPGamma(list(map(lambda a: MPGammaA(a), bk)))
        assert all(tau.wellTyped(bGamma, gc) for tau in tList)
        qq = gc.closure(self.qList)
        c = MPC(bk, qq, MPQ(self.tc))
        assert c.unambiguous()
        assert all(q.wellFormed(bGamma, gc) for q in qq)
        qi = gc.getTCListFromMethod(self.m)
        bqGamma = MPGamma(bGamma.elements)
        bqGamma.addElements(list(map(lambda q: MPGammaQ(q), qq)))
        assert all(MPQSubst(tList, tcA.tList, MPQ(q)).entails(p, gc, bqGamma) for q in qi)
        gammaNew = MPGamma(bqGamma.elements)
        sigma = gc.getSigmaFromMethod(self.m)
        gammaNew.addElements(list(map(lambda a: MPGammaA(a), sigma.getVariables())))
        gammaNew.addElements(list(map(lambda q: MPGammaQ(MPQSubst(tList, tcA.tList, q)), sigma.getConstraints())))
        assert self.e.hasType(p, gc, gammaNew, MPTypeSubst(tList, tcA.tList, sigma.getTau()))
        assert (all(element.c.q.tc.name != tcA.name
                    or any(not tList[i].equalsWithVars(bk, element.c.q.tc.tList[i], element.c.aList) for i in range(len(tList)))
                    for element in p.elements))
        pElem = MPPElem(c, self.m, gammaNew, self.e)
        p.addElement(pElem)


class MPCls:
    def __init__(self, tcList: List[MPTCA], tc: MPTCA, m: str, sigma: MPSigma):
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

    def addToGC(self, gc: MPGC):
        assert all(element.m != self.m for element in gc.elements)
        assert all(element.tc.name != self.tc.name for element in gc.elements)
        qp = gc.closure(self.sigma.getConstraints())
        sigmaNew = MPSigmaForall(self.sigma.getVariables(), MPRhoConstr(qp, self.sigma.getTau()))
        aList = self.tc.tList
        gammaNew = MPGamma(list(map(lambda a: MPGammaA(a), aList)))
        assert sigmaNew.wellTyped(gammaNew, gc)
        sigmaA = deepcopy(sigmaNew)
        sigmaA.addElements(aList)
        assert sigmaA.unambiguous()
        assert all(MPQ(tc).wellFormed(gammaNew, gc) for tc in self.tcList)
        gcElem = MPGCElem(self.m, self.tcList, self.tc, sigmaNew)
        gc.addElement(gcElem)


class MPPgm(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def show(self):
        pass

    @abstractmethod
    def getType(self, p: MPP, gc: MPGC):
        pass

    @abstractmethod
    def elaborate(self, p: MPP, gc: MPGC):
        pass


class MPPgmE(MPPgm):
    def __init__(self, e: MPTerm):
        super().__init__()
        self.e = e

    def show(self):
        self.e.show()

    def getType(self, p: MPP, gc: MPGC):
        result = self.e.getType(p, gc, MPGamma([]))
        if isinstance(result, MPTypeSubst):
            result = result.evaluate()
        return result

    def elaborate(self, p: MPP, gc: MPGC):
        return self.e.elaborate(p, gc, MPGamma([]))


class MPPgmInst(MPPgm):
    def __init__(self, inst: MPInst, pgm: MPPgm):
        super().__init__()
        self.inst = inst
        self.pgm = pgm

    def show(self):
        self.inst.show()
        print("; ", end=" ")
        self.pgm.show()

    def getType(self, p: MPP, gc: MPGC):
        self.inst.addToP(p, gc)
        return self.pgm.getType(p, gc)

    def elaborate(self, p: MPP, gc: MPGC):
        self.inst.addToP(p, gc)
        return self.pgm.elaborate(p, gc)


class MPPgmCls(MPPgm):
    def __init__(self, cls: MPCls, pgm: MPPgm):
        super().__init__()
        self.cls = cls
        self.pgm = pgm

    def show(self):
        self.cls.show()
        print("; ", end=" ")
        self.pgm.show()

    def getType(self, p: MPP, gc: MPGC):
        self.cls.addToGC(gc)
        return self.pgm.getType(p, gc)

    def elaborate(self, p: MPP, gc: MPGC):
        self.cls.addToGC(gc)
        return self.pgm.elaborate(p, gc)
