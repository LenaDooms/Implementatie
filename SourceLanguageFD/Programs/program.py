from abc import ABC, abstractmethod
from copy import deepcopy
from typing import List

from SourceLanguageFD.Environment.Element import FDGammaA, FDGCElem, FDGammaQ, FDPElem
from SourceLanguageFD.Environment.environment import FDP, FDGC, FDGamma
from SourceLanguageFD.Programs.FD import FD
from SourceLanguageFD.Terms.Term import FDTerm
from SourceLanguageFD.Constraint.constraint import FDQ, FDC, FDQSubst
from SourceLanguageFD.Constraint.TC import FDTCA, FDTCTau
from SourceLanguageFD.Types.Rho import FDRhoConstr
from SourceLanguageFD.Types.Sigma import FDSigma, FDSigmaForall
from SourceLanguageFD.Types.Tau import FDTypeSubst
from exceptions import AlreadyExistsError


class FDInst:
    def __init__(self, qList: List[FDQ], tc: FDTCTau, m: str, e: FDTerm):
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

    def addToP(self, p: FDP, gc: FDGC):
        tcA = gc.getTCFromMethod(self.m)
        assert len(self.tc.tList) == len(tcA.tList)
        assert tcA.name == self.tc.name
        assert len(tcA.tList) == len(self.tc.tList)
        if p.hasFunctionalDependency(gc, self.tc):
            raise AlreadyExistsError("An instance with the same functional dependency already exists")
        tList = self.tc.tList
        bk = []
        for t in tList:
            bk += t.getFreeVars()
        bGamma = FDGamma(list(map(lambda a: FDGammaA(a), bk)))
        assert all(tau.wellTyped(bGamma, gc) for tau in tList)
        qq = gc.closure(self.qList)
        c = FDC(bk, qq, FDQ(self.tc))
        assert c.unambiguous(p, gc)
        assert all(q.wellFormed(bGamma, gc) for q in qq)
        qi = gc.getTCListFromMethod(self.m)
        bqGamma = FDGamma(bGamma.elements)
        bqGamma.addElements(list(map(lambda q: FDGammaQ(q), qq)))
        assert all(FDQSubst(tList, tcA.tList, FDQ(q)).entails(p, gc, bqGamma) for q in qi)
        gammaNew = FDGamma(bqGamma.elements)
        sigma = gc.getSigmaFromMethod(self.m)
        gammaNew.addElements(list(map(lambda a: FDGammaA(a), sigma.getVariables())))
        gammaNew.addElements(list(map(lambda q: FDGammaQ(FDQSubst(tList, tcA.tList, q)), sigma.getConstraints())))
        assert self.e.hasType(p, gc, gammaNew, FDTypeSubst(tList, tcA.tList, sigma.getTau()))
        assert (all(element.c.q.tc.name != tcA.name
                    or any(not tList[i].equalsWithVars(bk, element.c.q.tc.tList[i], element.c.aList) for i in range(len(tList)))
                    for element in p.elements))
        pElem = FDPElem(c, self.m, gammaNew, self.e)
        p.addElement(pElem)


class FDCls:
    def __init__(self, tcList: List[FDTCA], tc: FDTCA, m: str, sigma: FDSigma, fd: FD):
        #  check that all variables in FD are in typeclass variables
        assert all(any(a1.equals(a2) for a2 in tc.tList) for a1 in fd.aList1)
        assert all(any(a1.equals(a2) for a2 in tc.tList) for a1 in fd.aList2)
        self.tcList = tcList
        self.tc = tc
        self.m = m
        self.sigma = sigma
        self.fd = fd

    def show(self):
        print("class ", end=" ")
        for tc in self.tcList:
            tc.show()
            print(" => ")
        self.tc.show()
        print(" where { m : ", end=" ")
        self.sigma.show()
        print(" } ", end=" ")

    def addToGC(self, p: FDP, gc: FDGC):
        assert all(element.m != self.m for element in gc.elements)
        assert all(element.tc.name != self.tc.name for element in gc.elements)
        qp = gc.closure(self.sigma.getConstraints())
        sigmaNew = FDSigmaForall(self.sigma.getVariables(), FDRhoConstr(qp, self.sigma.getTau()))
        aList = self.tc.tList
        gammaNew = FDGamma(list(map(lambda a: FDGammaA(a), aList)))
        assert sigmaNew.wellTyped(gammaNew, gc)
        sigmaA = deepcopy(sigmaNew)
        sigmaA.addElements(aList)
        assert sigmaA.unambiguous(p, gc)
        assert all(FDQ(tc).wellFormed(gammaNew, gc) for tc in self.tcList)
        gcElem = FDGCElem(self.m, self.tcList, self.tc, sigmaNew, self.fd)
        gc.addElement(gcElem)


class FDPgm(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def show(self):
        pass

    @abstractmethod
    def getType(self, p: FDP, gc: FDGC):
        pass

    @abstractmethod
    def elaborate(self, p: FDP, gc: FDGC):
        pass


class FDPgmE(FDPgm):
    def __init__(self, e: FDTerm):
        super().__init__()
        self.e = e

    def show(self):
        self.e.show()

    def getType(self, p: FDP, gc: FDGC):
        result = self.e.getType(p, gc, FDGamma([]))
        if isinstance(result, FDTypeSubst):
            result = result.evaluate()
        return result

    def elaborate(self, p: FDP, gc: FDGC):
        return self.e.elaborate(p, gc, FDGamma([]))


class FDPgmInst(FDPgm):
    def __init__(self, inst: FDInst, pgm: FDPgm):
        super().__init__()
        self.inst = inst
        self.pgm = pgm

    def show(self):
        self.inst.show()
        print("; ", end=" ")
        self.pgm.show()

    def getType(self, p: FDP, gc: FDGC):
        self.inst.addToP(p, gc)
        return self.pgm.getType(p, gc)

    def elaborate(self, p: FDP, gc: FDGC):
        self.inst.addToP(p, gc)
        return self.pgm.elaborate(p, gc)


class FDPgmCls(FDPgm):
    def __init__(self, cls: FDCls, pgm: FDPgm):
        super().__init__()
        self.cls = cls
        self.pgm = pgm

    def show(self):
        self.cls.show()
        print("; ", end=" ")
        self.pgm.show()

    def getType(self, p: FDP, gc: FDGC):
        self.cls.addToGC(p, gc)
        return self.pgm.getType(p, gc)

    def elaborate(self, p: FDP, gc: FDGC):
        self.cls.addToGC(p, gc)
        return self.pgm.elaborate(p, gc)
