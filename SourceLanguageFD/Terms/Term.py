from copy import deepcopy

from IntermediateLanguage.Dictionaries.Dictionary import DictionaryDelta
from IntermediateLanguage.Terms.Term import ITermLet, ITermApp, ITermAbs, ITermQAbs, ITermTypeAbs, ITermFalse, \
    ITermTrue, ITermX, ITermESigma, ITermED, ITermM
from SourceLanguageFD.Constraint.TC import FDTCTau
from SourceLanguageFD.Constraint.constraint import FDQSubst, FDQ
from SourceLanguageFD.Environment.Element import FDGammaX, FDGammaA, FDGammaQ
from SourceLanguageFD.Terms.AbstractTerm import FDTerm
from SourceLanguageFD.Types.AbstractTypes import FDTau, FDRho, FDSigma
from SourceLanguageFD.Types.Rho import FDRhoConstr
from SourceLanguageFD.Types.Sigma import FDSigmaForall
from SourceLanguageFD.Types.Tau import FDTypeBool, FDTypeArrow, FDTypeSubst
from SourceLanguageFD.Environment.environment import FDP, FDGC, FDGamma
from exceptions import TypeNotMatchingError


class FDTermTrue(FDTerm):
    def show(self):
        print("True", end='')

    def getType(self, p: FDP, gc: FDGC, gamma: FDGamma):
        return FDTypeBool()

    def hasType(self, p: FDP, gc: FDGC, gamma: FDGamma, tau: FDTau):
        return isinstance(tau, FDTypeBool) or (isinstance(tau, FDTypeSubst) and isinstance(tau.evaluate(), FDTypeBool))

    def equals(self, e: FDTerm):
        return isinstance(e, FDTermTrue)

    def elaborate(self, p, gc, gamma):
        return ITermTrue()

    def elaborateWithType(self, p, gc, gamma, tau):
        return ITermTrue()


class FDTermFalse(FDTerm):

    def show(self):
        print("False", end='')

    def getType(self, p: FDP, gc: FDGC, gamma: FDGamma):
        return FDTypeBool()

    def hasType(self, p: FDP, gc: FDGC, gamma: FDGamma, tau: FDTau):
        return isinstance(tau, FDTypeBool) or (isinstance(tau, FDTypeSubst) and isinstance(tau.evaluate(), FDTypeBool))

    def equals(self, e: FDTerm):
        return isinstance(e, FDTermFalse)

    def elaborate(self, p, gc, gamma):
        return ITermFalse()

    def elaborateWithType(self, p, gc, gamma, tau):
        return ITermFalse()


class FDTermX(FDTerm):
    def __init__(self, x: str):
        super().__init__()
        self.x = x

    def show(self):
        print(self.x, end='')

    def getType(self, p: FDP, gc: FDGC, gamma: FDGamma):
        tau = gamma.getSigmaFromX(self.x).getTau()
        if self.hasType(p, gc, gamma, tau):
            return tau
        pass

    def hasType(self, p: FDP, gc: FDGC, gamma: FDGamma, tau: FDTau):
        if not isinstance(tau, FDTypeSubst):
            t = FDTypeSubst([], [], tau)
        else:
            t = tau
        sigma = gamma.getSigmaFromX(self.x)
        aList = sigma.getVariables()
        qiList = sigma.getConstraints()

        return (len(aList) == len(t.aList)
                and all(any(a1.equals(a2) for a2 in t.aList) for a1 in aList)
                and (t.tau.equals(sigma.getTau())
                     or (isinstance(t.tau, FDTypeSubst) and t.tau.evaluate().equals(sigma.getTau())))
                and all(FDQSubst(t.tList, t.aList, qi).entails(p, gc, gamma) for qi in qiList)
                and sigma.unambiguous(p, gc)
                and all(ti.wellTyped(gamma, gc) for ti in t.tList)
                and p.wellFormed(gc, gamma))

    def equals(self, e: FDTerm):
        return isinstance(e, FDTermX) and self.x == e.x

    def elaborate(self, p, gc, gamma):
        pass

    def elaborateWithType(self, p: FDP, gc: FDGC, gamma: FDGamma, tau: FDTau):
        sigma = gamma.getSigmaFromX(self.x)
        qiList = sigma.getConstraints()
        if isinstance(tau, FDTypeSubst):
            tList = tau.tList
            aList = tau.aList
        else:
            tList = []
            aList = []
        di = list(map(lambda q: FDQSubst(tList, aList, q).getDictionary(p, gc, gamma), qiList))
        sj = list(map(lambda t: t.elaborate(gc), tList))
        x = ITermX(self.x)
        for s in sj:
            x = ITermESigma(x, s)
        for d in di:
            x = ITermED(x, d)
        return x


class FDTermM(FDTerm):
    def __init__(self, m: str):
        super().__init__()
        self.m = m

    def show(self):
        print(self.m, end='')

    def getType(self, p: FDP, gc: FDGC, gamma: FDGamma):
        pass

    def hasType(self, p: FDP, gc: FDGC, gamma: FDGamma, tau: FDTau):
        if isinstance(tau, FDTypeSubst) and isinstance(tau.tau, FDTypeSubst):
            sigma = gc.getSigmaFromMethod(self.m)
            tc = gc.getTCFromMethod(self.m)
            tNew = tau.tau.tau
            tList = tau.tau.tList
            aList = tau.tau.aList
            ajList = sigma.getVariables()
            if isinstance(sigma, FDSigmaForall):
                sigmaNew = deepcopy(sigma)
                sigmaNew.addElements(tc.tList)
            elif isinstance(sigma, FDRho) or isinstance(sigma, FDTau):
                sigmaNew = FDSigmaForall(tc.tList, sigma)
            else:
                sigmaNew = deepcopy(sigma)
            qiList = sigma.getConstraints()
            return (sigmaNew.unambiguous(p, gc)
                    and (tNew.equals(sigma.getTau())
                         or (isinstance(tNew, FDTypeSubst) and tNew.evaluate().equals(sigma.getTau())))
                    and len(aList) == len(tc.tList)
                    and all(aList[i].equals(tc.tList[i]) for i in range(len(aList)))
                    and all(any(ai.equals(aj) for aj in ajList) for ai in tau.aList)
                    and FDQ(FDTCTau(tc.name, tList)).entails(p, gc, gamma)
                    and all(t.wellTyped(gamma, gc) for t in tList)
                    and all(
                        FDQSubst(tau.tList, tau.aList, FDQSubst(tau.tau.tList, tau.tau.aList, qi)).entails(p, gc, gamma)
                        for qi in qiList)
                    and all(tj.wellTyped(gamma, gc) for tj in tau.tList)
                    and tNew.equals(sigma.getRho().getTau())
                    and p.wellFormed(gc, gamma))
        return False

    def equals(self, e: FDTerm):
        return isinstance(e, FDTermM) and self.m == e.m

    def elaborate(self, p, gc, gamma):
        pass

    def elaborateWithType(self, p: FDP, gc: FDGC, gamma: FDGamma, tau: FDTau):
        assert isinstance(tau, FDTypeSubst) and isinstance(tau.tau, FDTypeSubst)
        tc = gc.getTCFromMethod(self.m)
        d = FDQ(FDTCTau(tc.name, tau.tau.tList)).getDictionary(p, gc, gamma)
        term = ITermM(d, self.m)
        sj = list(map(lambda tj: tj.elaborate(gc), tau.tList))
        for s in sj:
            term = ITermESigma(term, s)
        sigma = gc.getSigmaFromMethod(self.m)
        tList = tau.tList
        aList = tau.aList
        t = tau.tau.tList
        a = tau.tau.aList
        di = list(map(lambda q: FDQSubst(tList, aList, FDQSubst(t, a, q)).elaborate(gc), sigma.getConstraints()))
        for dictionary in di:
            term = ITermED(term, dictionary)
        return term


class FDTermAbs(FDTerm):
    def __init__(self, x: str, e: FDTerm):
        super().__init__()
        self.x = x
        self.e = e

    def show(self):
        print("\\" + self.x + ". ", end='')
        self.e.show()

    def getType(self, p: FDP, gc: FDGC, gamma: FDGamma):
        pass

    def hasType(self, p: FDP, gc: FDGC, gamma: FDGamma, tau: FDTau):
        if isinstance(tau, FDTypeSubst):
            tau = tau.evaluate()
        if isinstance(tau, FDTypeArrow):
            gammaNew = deepcopy(gamma)
            gammaNew.elements = deepcopy(gamma.elements)
            gammaNew.addElement(FDGammaX(self.x, tau.t1))
            return (all(not (isinstance(element, FDGammaX) and element.x == self.x) for element in gamma.elements)
                    and self.e.hasType(p, gc, gammaNew, tau.t2)
                    and tau.t1.wellTyped(gamma, gc))
        return False

    def equals(self, e: FDTerm):
        return isinstance(e, FDTermAbs) and self.x == e.x and self.e.equals(e.e)

    def elaborate(self, p, gc, gamma):
        pass

    def elaborateWithType(self, p: FDP, gc: FDGC, gamma: FDGamma, tau: FDTau):
        if isinstance(tau, FDTypeSubst):
            tau = tau.evaluate()
        assert isinstance(tau, FDTypeArrow)
        sigma = tau.t1.elaborate(gc)
        gammaNew = deepcopy(gamma)
        gammaNew.elements = deepcopy(gamma.elements)
        gammaNew.addElement(FDGammaX(self.x, tau.t1))
        e = self.e.elaborateWithType(p, gc, gammaNew, tau.t2)
        return ITermAbs(self.x, sigma, e)


class FDTermApp(FDTerm):
    def __init__(self, e1: FDTerm, e2: FDTerm):
        super().__init__()
        self.e1 = e1
        self.e2 = e2

    def show(self):
        self.e1.show()
        self.e2.show()

    def getType(self, p: FDP, gc: FDGC, gamma: FDGamma):
        t1 = self.e2.getType(p, gc, gamma)
        tArrow = self.e1.getType(p, gc, gamma)
        if isinstance(tArrow, FDTypeSubst):
            tArrow = tArrow.evaluate()
        if isinstance(tArrow, FDTypeArrow) and tArrow.t1.equals(t1):
            return tArrow.t2
        else:
            raise TypeNotMatchingError("Types in application don't match")

    def hasType(self, p: FDP, gc: FDGC, gamma: FDGamma, tau: FDTau):
        return tau.equals(self.getType(p, gc, gamma))

    def equals(self, e: FDTerm):
        return isinstance(e, FDTermApp) and self.e1.equals(e.e1) and self.e2.equals(e.e2)

    def elaborate(self, p: FDP, gc: FDGC, gamma: FDGamma):
        t1 = self.e2.getType(p, gc, gamma)
        tArrow = self.e1.getType(p, gc, gamma)
        if isinstance(tArrow, FDTypeSubst):
            tArrow = tArrow.evaluate()
        if not (isinstance(tArrow, FDTypeArrow) and tArrow.t1.equals(t1)):
            raise TypeNotMatchingError("Types in application don't match")
        return ITermApp(self.e1.elaborateWithType(p, gc, gamma, tArrow), self.e2.elaborateWithType(p, gc, gamma, t1))

    def elaborateWithType(self, p: FDP, gc: FDGC, gamma: FDGamma, tau: FDTau):
        return self.elaborate(p, gc, gamma)


class FDTermLet(FDTerm):
    def __init__(self, x: str, sigma: FDSigma, e1: FDTerm, e2: FDTerm):
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

    def getType(self, p: FDP, gc: FDGC, gamma: FDGamma):
        assert self.sigma.unambiguous(p, gc)
        assert all(not (isinstance(g, FDGammaX) and self.x == g.x) for g in gamma.elements)
        qk = gc.closure(self.sigma.getConstraints())
        t1 = self.sigma.getTau()
        aList = self.sigma.getVariables()
        sigmaNew = FDSigmaForall(aList, FDRhoConstr(qk, deepcopy(t1)))
        assert sigmaNew.wellTyped(gamma, gc)
        gammaNew = deepcopy(gamma)
        gammaNew.elements = deepcopy(gamma.elements)
        gammaNew.addElements(list(map(lambda a: FDGammaA(a), aList)))
        gammaNew.addElements(list(map(lambda q: FDGammaQ(q), qk)))
        assert self.e1.hasType(p, gc, gammaNew, t1)
        gammaNew2 = deepcopy(gamma)
        gammaNew2.elements = deepcopy(gamma.elements)
        gammaNew2.addElement(FDGammaX(self.x, sigmaNew))
        return self.e2.getType(p, gc, gammaNew2)

    def hasType(self, p: FDP, gc: FDGC, gamma: FDGamma, tau: FDTau):
        return tau.equals(self.getType(p, gc, gamma))

    def equals(self, e: FDTerm):
        return isinstance(e, FDTermLet) and self.x == e.x and self.sigma.equals(e.sigma) and self.e1.equals(
            e.e1) and self.e2.equals(e.e2)

    def elaborate(self, p: FDP, gc: FDGC, gamma: FDGamma):
        qk = gc.closure(self.sigma.getConstraints())
        t1 = self.sigma.getTau()
        aList = self.sigma.getVariables()

        sigmaNew = FDSigmaForall(aList, FDRhoConstr(qk, deepcopy(t1)))
        sigmaElaborated = sigmaNew.elaborate(gc)
        delta = gamma.getDeltaIndex() + len(qk)

        gammaNew = deepcopy(gamma)
        gammaNew.elements = deepcopy(gamma.elements)
        gammaNew.addElements(list(map(lambda a: FDGammaA(a), aList)))
        gammaNew.addElements(list(map(lambda q: FDGammaQ(q), qk)))
        gammaNew2 = deepcopy(gamma)
        gammaNew2.elements = deepcopy(gamma.elements)
        gammaNew2.addElement(FDGammaX(self.x, sigmaNew))
        e1Elaborated = self.e1.elaborateWithType(p, gc, gammaNew, self.sigma.getTau())

        for i in range(1, len(qk) + 1):
            e1Elaborated = ITermQAbs(DictionaryDelta(delta), qk[-i].elaborate(), e1Elaborated)
            delta -= 1

        for i in range(1, len(aList) + 1):
            e1Elaborated = ITermTypeAbs(aList[-i].elaborate(), e1Elaborated)

        return ITermLet(self.x, sigmaElaborated, e1Elaborated,
                        self.e2.elaborateWithType(p, gc, gammaNew2, self.e2.getType(p, gc, gammaNew2)))

    def elaborateWithType(self, p: FDP, gc: FDGC, gamma: FDGamma, tau: FDTau):
        return self.elaborate(p, gc, gamma)


class FDTermDecl(FDTerm):
    def __init__(self, e: FDTerm, tau: FDTau):
        super().__init__()
        self.e = e
        self.tau = tau

    def show(self):
        self.e.show()
        print(" :: ", end=" ")
        self.tau.show()

    def getType(self, p: FDP, gc: FDGC, gamma: FDGamma):
        if self.e.hasType(p, gc, gamma, self.tau):
            return self.tau
        else:
            raise TypeNotMatchingError("Declared type doesnt match actual type")

    def hasType(self, p: FDP, gc: FDGC, gamma: FDGamma, tau: FDTau):
        return tau.equals(self.getType(p, gc, gamma))

    def equals(self, e: FDTerm):
        return isinstance(e, FDTermDecl) and self.e.equals(e.e) and self.tau.equals(e.tau)

    def elaborate(self, p: FDP, gc: FDGC, gamma: FDGamma):
        return self.e.elaborateWithType(p, gc, gamma, self.tau)

    def elaborateWithType(self, p: FDP, gc: FDGC, gamma: FDGamma, tau: FDTau):
        t1 = self.tau
        t = self.tau
        if isinstance(t1, FDTypeSubst):
            t1 = t1.evaluate()
        t2 = tau
        if isinstance(t2, FDTypeSubst):
            t = tau
            t2 = t2.evaluate()
        assert t1.equals(t2)
        return self.e.elaborateWithType(p, gc, gamma, t)
