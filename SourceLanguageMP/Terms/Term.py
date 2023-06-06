from copy import deepcopy

from IntermediateLanguage.Dictionaries.Dictionary import DictionaryDelta
from IntermediateLanguage.Terms.Term import ITermLet, ITermApp, ITermAbs, ITermQAbs, ITermTypeAbs, ITermFalse, \
    ITermTrue, ITermX, ITermESigma, ITermED, ITermM
from SourceLanguageMP.Constraint.TC import MPTCTau
from SourceLanguageMP.Constraint.constraint import MPQSubst, MPQ
from SourceLanguageMP.Environment.Element import MPGammaX, MPGammaA, MPGammaQ
from SourceLanguageMP.Terms.AbstractTerm import MPTerm
from SourceLanguageMP.Types.AbstractTypes import MPTau, MPRho, MPSigma
from SourceLanguageMP.Types.Rho import MPRhoConstr
from SourceLanguageMP.Types.Sigma import MPSigmaForall
from SourceLanguageMP.Types.Tau import MPTypeBool, MPTypeArrow, MPTypeSubst
from SourceLanguageMP.Environment.environment import MPP, MPGC, MPGamma
from exceptions import TypeNotMatchingError


class MPTermTrue(MPTerm):
    def show(self):
        print("True", end='')

    def getType(self, p: MPP, gc: MPGC, gamma: MPGamma):
        return MPTypeBool()

    def hasType(self, p: MPP, gc: MPGC, gamma: MPGamma, tau: MPTau):
        return isinstance(tau, MPTypeBool) or (isinstance(tau, MPTypeSubst) and isinstance(tau.evaluate(), MPTypeBool))

    def equals(self, e: MPTerm):
        return isinstance(e, MPTermTrue)

    def elaborate(self, p, gc, gamma):
        return ITermTrue()

    def elaborateWithType(self, p, gc, gamma, tau):
        return ITermTrue()


class MPTermFalse(MPTerm):

    def show(self):
        print("False", end='')

    def getType(self, p: MPP, gc: MPGC, gamma: MPGamma):
        return MPTypeBool()

    def hasType(self, p: MPP, gc: MPGC, gamma: MPGamma, tau: MPTau):
        return isinstance(tau, MPTypeBool) or (isinstance(tau, MPTypeSubst) and isinstance(tau.evaluate(), MPTypeBool))

    def equals(self, e: MPTerm):
        return isinstance(e, MPTermFalse)

    def elaborate(self, p, gc, gamma):
        return ITermFalse()

    def elaborateWithType(self, p, gc, gamma, tau):
        return ITermFalse()


class MPTermX(MPTerm):
    def __init__(self, x: str):
        super().__init__()
        self.x = x

    def show(self):
        print(self.x, end='')

    def getType(self, p: MPP, gc: MPGC, gamma: MPGamma):
        tau = gamma.getSigmaFromX(self.x).getTau()
        if self.hasType(p, gc, gamma, tau):
            return tau
        pass

    def hasType(self, p: MPP, gc: MPGC, gamma: MPGamma, tau: MPTau):
        if not isinstance(tau, MPTypeSubst):
            t = MPTypeSubst([], [], tau)
        else:
            t = tau
        sigma = gamma.getSigmaFromX(self.x)
        aList = sigma.getVariables()
        qiList = sigma.getConstraints()

        return (len(aList) == len(t.aList)
                and all(any(a1.equals(a2) for a2 in t.aList) for a1 in aList)
                and (t.tau.equals(sigma.getTau())
                     or (isinstance(t.tau, MPTypeSubst) and t.tau.evaluate().equals(sigma.getTau())))
                and all(MPQSubst(t.tList, t.aList, qi).entails(p, gc, gamma) for qi in qiList)
                and sigma.unambiguous()
                and all(ti.wellTyped(gamma, gc) for ti in t.tList)
                and p.wellFormed(gc, gamma))

    def equals(self, e: MPTerm):
        return isinstance(e, MPTermX) and self.x == e.x

    def elaborate(self, p, gc, gamma):
        pass

    def elaborateWithType(self, p: MPP, gc: MPGC, gamma: MPGamma, tau: MPTau):
        sigma = gamma.getSigmaFromX(self.x)
        qiList = sigma.getConstraints()
        if isinstance(tau, MPTypeSubst):
            tList = tau.tList
            aList = tau.aList
        else:
            tList = []
            aList = []
        di = list(map(lambda q: MPQSubst(tList, aList, q).getDictionary(p, gc, gamma), qiList))
        sj = list(map(lambda t: t.elaborate(gc), tList))
        x = ITermX(self.x)
        for s in sj:
            x = ITermESigma(x, s)
        for d in di:
            x = ITermED(x, d)
        return x


class MPTermM(MPTerm):
    def __init__(self, m: str):
        super().__init__()
        self.m = m

    def show(self):
        print(self.m, end='')

    def getType(self, p: MPP, gc: MPGC, gamma: MPGamma):
        pass

    def hasType(self, p: MPP, gc: MPGC, gamma: MPGamma, tau: MPTau):
        if isinstance(tau, MPTypeSubst) and not isinstance(tau.tau, MPTypeSubst):
            tau = MPTypeSubst([], [], tau)
        if isinstance(tau, MPTypeSubst) and isinstance(tau.tau, MPTypeSubst):
            sigma = gc.getSigmaFromMethod(self.m)
            tc = gc.getTCFromMethod(self.m)
            tNew = tau.tau.tau
            tList = tau.tau.tList
            aList = tau.tau.aList
            ajList = sigma.getVariables()
            if isinstance(sigma, MPSigmaForall):
                sigmaNew = deepcopy(sigma)
                sigmaNew.addElements(tc.tList)
            elif isinstance(sigma, MPRho) or isinstance(sigma, MPTau):
                sigmaNew = MPSigmaForall(tc.tList, sigma)
            else:
                sigmaNew = deepcopy(sigma)
            qiList = sigma.getConstraints()
            return (sigmaNew.unambiguous()
                    and (tNew.equals(sigma.getTau())
                         or (isinstance(tNew, MPTypeSubst) and tNew.evaluate().equals(sigma.getTau())))
                    and len(aList) == len(tc.tList)
                    and all(aList[i].equals(tc.tList[i]) for i in range(len(aList)))
                    and all(any(ai.equals(aj) for aj in ajList) for ai in tau.aList)
                    and MPQ(MPTCTau(tc.name, tList)).entails(p, gc, gamma)
                    and all(t.wellTyped(gamma, gc) for t in tList)
                    and all(
                        MPQSubst(tau.tList, tau.aList, MPQSubst(tau.tau.tList, tau.tau.aList, qi)).entails(p, gc, gamma)
                        for qi in qiList)
                    and all(tj.wellTyped(gamma, gc) for tj in tau.tList)
                    and tNew.equals(sigma.getRho().getTau())
                    and p.wellFormed(gc, gamma))
        return False

    def equals(self, e: MPTerm):
        return isinstance(e, MPTermM) and self.m == e.m

    def elaborate(self, p, gc, gamma):
        pass

    def elaborateWithType(self, p: MPP, gc: MPGC, gamma: MPGamma, tau: MPTau):
        assert isinstance(tau, MPTypeSubst) and isinstance(tau.tau, MPTypeSubst)
        tc = gc.getTCFromMethod(self.m)
        d = MPQ(MPTCTau(tc.name, tau.tau.tList)).getDictionary(p, gc, gamma)
        term = ITermM(d, self.m)
        sj = list(map(lambda tj: tj.elaborate(gc), tau.tList))
        for s in sj:
            term = ITermESigma(term, s)
        sigma = gc.getSigmaFromMethod(self.m)
        tList = tau.tList
        aList = tau.aList
        t = tau.tau.tList
        a = tau.tau.aList
        di = list(map(lambda q: MPQSubst(tList, aList, MPQSubst(t, a, q)).elaborate(gc), sigma.getConstraints()))
        for dictionary in di:
            term = ITermED(term, dictionary)
        return term


class MPTermAbs(MPTerm):
    def __init__(self, x: str, e: MPTerm):
        super().__init__()
        self.x = x
        self.e = e

    def show(self):
        print("\\" + self.x + ". ", end='')
        self.e.show()

    def getType(self, p: MPP, gc: MPGC, gamma: MPGamma):
        pass

    def hasType(self, p: MPP, gc: MPGC, gamma: MPGamma, tau: MPTau):
        if isinstance(tau, MPTypeSubst):
            tau = tau.evaluate()
        if isinstance(tau, MPTypeArrow):
            gammaNew = deepcopy(gamma)
            gammaNew.elements = deepcopy(gamma.elements)
            gammaNew.addElement(MPGammaX(self.x, tau.t1))
            return (all(not (isinstance(element, MPGammaX) and element.x == self.x) for element in gamma.elements)
                    and self.e.hasType(p, gc, gammaNew, tau.t2)
                    and tau.t1.wellTyped(gamma, gc))
        return False

    def equals(self, e: MPTerm):
        return isinstance(e, MPTermAbs) and self.x == e.x and self.e.equals(e.e)

    def elaborate(self, p, gc, gamma):
        pass

    def elaborateWithType(self, p: MPP, gc: MPGC, gamma: MPGamma, tau: MPTau):
        if isinstance(tau, MPTypeSubst):
            tau = tau.evaluate()
        assert isinstance(tau, MPTypeArrow)
        sigma = tau.t1.elaborate(gc)
        gammaNew = deepcopy(gamma)
        gammaNew.elements = deepcopy(gamma.elements)
        gammaNew.addElement(MPGammaX(self.x, tau.t1))
        e = self.e.elaborateWithType(p, gc, gammaNew, tau.t2)
        return ITermAbs(self.x, sigma, e)


class MPTermApp(MPTerm):
    def __init__(self, e1: MPTerm, e2: MPTerm):
        super().__init__()
        self.e1 = e1
        self.e2 = e2

    def show(self):
        self.e1.show()
        self.e2.show()

    def getType(self, p: MPP, gc: MPGC, gamma: MPGamma):
        t1 = self.e2.getType(p, gc, gamma)
        tArrow = self.e1.getType(p, gc, gamma)
        if isinstance(tArrow, MPTypeSubst):
            tArrow = tArrow.evaluate()
        if isinstance(tArrow, MPTypeArrow) and tArrow.t1.equals(t1):
            return tArrow.t2
        else:
            raise TypeNotMatchingError("Types in application don't match")

    def hasType(self, p: MPP, gc: MPGC, gamma: MPGamma, tau: MPTau):
        return tau.equals(self.getType(p, gc, gamma))

    def equals(self, e: MPTerm):
        return isinstance(e, MPTermApp) and self.e1.equals(e.e1) and self.e2.equals(e.e2)

    def elaborate(self, p: MPP, gc: MPGC, gamma: MPGamma):
        t1 = self.e2.getType(p, gc, gamma)
        tArrow = self.e1.getType(p, gc, gamma)
        if isinstance(tArrow, MPTypeSubst):
            tArrow = tArrow.evaluate()
        if not (isinstance(tArrow, MPTypeArrow) and tArrow.t1.equals(t1)):
            raise TypeNotMatchingError("Types in application don't match")
        return ITermApp(self.e1.elaborateWithType(p, gc, gamma, tArrow), self.e2.elaborateWithType(p, gc, gamma, t1))

    def elaborateWithType(self, p: MPP, gc: MPGC, gamma: MPGamma, tau: MPTau):
        return self.elaborate(p, gc, gamma)


class MPTermLet(MPTerm):
    def __init__(self, x: str, sigma: MPSigma, e1: MPTerm, e2: MPTerm):
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

    def getType(self, p: MPP, gc: MPGC, gamma: MPGamma):
        assert self.sigma.unambiguous()
        assert all(not (isinstance(g, MPGammaX) and self.x == g.x) for g in gamma.elements)
        qk = gc.closure(self.sigma.getConstraints())
        t1 = self.sigma.getTau()
        aList = self.sigma.getVariables()
        sigmaNew = MPSigmaForall(aList, MPRhoConstr(qk, deepcopy(t1)))
        assert sigmaNew.wellTyped(gamma, gc)
        gammaNew = deepcopy(gamma)
        gammaNew.elements = deepcopy(gamma.elements)
        gammaNew.addElements(list(map(lambda a: MPGammaA(a), aList)))
        gammaNew.addElements(list(map(lambda q: MPGammaQ(q), qk)))
        assert self.e1.hasType(p, gc, gammaNew, t1)
        gammaNew2 = deepcopy(gamma)
        gammaNew2.elements = deepcopy(gamma.elements)
        gammaNew2.addElement(MPGammaX(self.x, sigmaNew))
        return self.e2.getType(p, gc, gammaNew2)

    def hasType(self, p: MPP, gc: MPGC, gamma: MPGamma, tau: MPTau):
        return tau.equals(self.getType(p, gc, gamma))

    def equals(self, e: MPTerm):
        return isinstance(e, MPTermLet) and self.x == e.x and self.sigma.equals(e.sigma) and self.e1.equals(
            e.e1) and self.e2.equals(e.e2)

    def elaborate(self, p: MPP, gc: MPGC, gamma: MPGamma):
        qk = gc.closure(self.sigma.getConstraints())
        t1 = self.sigma.getTau()
        aList = self.sigma.getVariables()

        sigmaNew = MPSigmaForall(aList, MPRhoConstr(qk, deepcopy(t1)))
        sigmaElaborated = sigmaNew.elaborate(gc)
        delta = gamma.getDeltaIndex() + len(qk)

        gammaNew = deepcopy(gamma)
        gammaNew.elements = deepcopy(gamma.elements)
        gammaNew.addElements(list(map(lambda a: MPGammaA(a), aList)))
        gammaNew.addElements(list(map(lambda q: MPGammaQ(q), qk)))
        gammaNew2 = deepcopy(gamma)
        gammaNew2.elements = deepcopy(gamma.elements)
        gammaNew2.addElement(MPGammaX(self.x, sigmaNew))
        e1Elaborated = self.e1.elaborateWithType(p, gc, gammaNew, self.sigma.getTau())

        for i in range(1, len(qk) + 1):
            e1Elaborated = ITermQAbs(DictionaryDelta(delta), qk[-i].elaborate(), e1Elaborated)
            delta -= 1

        for i in range(1, len(aList) + 1):
            e1Elaborated = ITermTypeAbs(aList[-i].elaborate(), e1Elaborated)

        return ITermLet(self.x, sigmaElaborated, e1Elaborated,
                        self.e2.elaborateWithType(p, gc, gammaNew2, self.e2.getType(p, gc, gammaNew2)))

    def elaborateWithType(self, p: MPP, gc: MPGC, gamma: MPGamma, tau: MPTau):
        return self.elaborate(p, gc, gamma)


class MPTermDecl(MPTerm):
    def __init__(self, e: MPTerm, tau: MPTau):
        super().__init__()
        self.e = e
        self.tau = tau

    def show(self):
        self.e.show()
        print(" :: ", end=" ")
        self.tau.show()

    def getType(self, p: MPP, gc: MPGC, gamma: MPGamma):
        if self.e.hasType(p, gc, gamma, self.tau):
            return self.tau
        else:
            raise TypeNotMatchingError("Declared type doesnt match actual type")

    def hasType(self, p: MPP, gc: MPGC, gamma: MPGamma, tau: MPTau):
        return tau.equals(self.getType(p, gc, gamma))

    def equals(self, e: MPTerm):
        return isinstance(e, MPTermDecl) and self.e.equals(e.e) and self.tau.equals(e.tau)

    def elaborate(self, p: MPP, gc: MPGC, gamma: MPGamma):
        return self.e.elaborateWithType(p, gc, gamma, self.tau)

    def elaborateWithType(self, p: MPP, gc: MPGC, gamma: MPGamma, tau: MPTau):
        t1 = self.tau
        t = self.tau
        if isinstance(t1, MPTypeSubst):
            t1 = t1.evaluate()
        t2 = tau
        if isinstance(t2, MPTypeSubst):
            t = tau
            t2 = t2.evaluate()
        assert t1.equals(t2)
        return self.e.elaborateWithType(p, gc, gamma, t)
