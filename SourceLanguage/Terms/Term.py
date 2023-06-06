from copy import deepcopy

from IntermediateLanguage.Dictionaries.Dictionary import DictionaryDelta
from IntermediateLanguage.Terms.Term import ITermTrue, ITermFalse, ITermApp, ITermQAbs, ITermTypeAbs, ITermLet, ITermX, \
    ITermESigma, ITermED, ITermAbs, ITermM
from SourceLanguage.Constraint.TC import TcTau
from SourceLanguage.Constraint.constraint import QSubst, Q
from SourceLanguage.Environment.Element import GammaX, GammaA, GammaQ
from SourceLanguage.Terms.AbstractTerm import Term
from SourceLanguage.Types.AbstractTypes import Tau, Rho, Sigma
from SourceLanguage.Types.Rho import RhoConstr
from SourceLanguage.Types.Sigma import SigmaForall
from SourceLanguage.Types.Tau import TypeBool, TypeArrow, TypeSubst
from SourceLanguage.Environment.environment import P, GC, Gamma
from exceptions import TypeNotMatchingError


class TermTrue(Term):
    def show(self):
        print("True", end='')

    def getType(self, p: P, gc: GC, gamma: Gamma):
        return TypeBool()

    def hasType(self, p: P, gc: GC, gamma: Gamma, tau: Tau):
        return isinstance(tau, TypeBool) or (isinstance(tau, TypeSubst) and isinstance(tau.evaluate(), TypeBool))

    def equals(self, e: Term):
        return isinstance(e, TermTrue)

    def elaborate(self, p: P, gc: GC, gamma: Gamma):
        return ITermTrue()

    def elaborateWithType(self, p: P, gc: GC, gamma: Gamma, tau: Tau):
        return ITermTrue()


class TermFalse(Term):

    def show(self):
        print("False", end='')

    def getType(self, p: P, gc: GC, gamma: Gamma):
        return TypeBool()

    def hasType(self, p: P, gc: GC, gamma: Gamma, tau: Tau):
        return isinstance(tau, TypeBool) or (isinstance(tau, TypeSubst) and isinstance(tau.evaluate(), TypeBool))

    def equals(self, e: Term):
        return isinstance(e, TermFalse)

    def elaborate(self, p: P, gc: GC, gamma: Gamma):
        return ITermFalse()

    def elaborateWithType(self, p: P, gc: GC, gamma: Gamma, tau: Tau):
        return ITermFalse()


class TermX(Term):
    def __init__(self, x: str):
        super().__init__()
        self.x = x

    def show(self):
        print(self.x, end='')

    def getType(self, p: P, gc: GC, gamma: Gamma):
        tau = gamma.getSigmaFromX(self.x).getTau()
        if self.hasType(p, gc, gamma, tau):
            return tau
        pass

    def hasType(self, p: P, gc: GC, gamma: Gamma, tau: Tau):
        if not isinstance(tau, TypeSubst):
            t = TypeSubst([], [], tau)
        else:
            t = tau
        sigma = gamma.getSigmaFromX(self.x)
        aList = sigma.getVariables()
        qiList = sigma.getConstraints()

        return (len(aList) == len(t.aList)
                and all(any(a1.equals(a2) for a2 in t.aList) for a1 in aList)
                and (t.tau.equals(sigma.getTau())
                     or (isinstance(t.tau, TypeSubst) and t.tau.evaluate().equals(sigma.getTau())))
                and all(QSubst(t.tList, t.aList, qi).entails(p, gc, gamma) for qi in qiList)
                and sigma.unambiguous()
                and all(ti.wellTyped(gamma, gc) for ti in t.tList)
                and p.wellFormed(gc, gamma))

    def equals(self, e: Term):
        return isinstance(e, TermX) and self.x == e.x

    def elaborate(self, p, gc, gamma):
        pass

    def elaborateWithType(self, p: P, gc: GC, gamma: Gamma, tau: Tau):
        sigma = gamma.getSigmaFromX(self.x)
        qiList = sigma.getConstraints()
        if isinstance(tau, TypeSubst):
            tList = tau.tList
            aList = tau.aList
        else:
            tList = []
            aList = []
        di = list(map(lambda q: QSubst(tList, aList, q).getDictionary(p, gc, gamma), qiList))
        sj = list(map(lambda t: t.elaborate(), tList))
        x = ITermX(self.x)
        for s in sj:
            x = ITermESigma(x, s)
        for d in di:
            x = ITermED(x, d)
        return x


class TermM(Term):
    def __init__(self, m: str):
        super().__init__()
        self.m = m

    def show(self):
        print(self.m, end='')

    def getType(self, p: P, gc: GC, gamma: Gamma):
        pass

    def hasType(self, p: P, gc: GC, gamma: Gamma, tau: Tau):
        if isinstance(tau, TypeSubst) and isinstance(tau.tau, TypeSubst) and len(tau.tau.aList) == 1:
            sigma = gc.getSigmaFromMethod(self.m)
            tc = gc.getTCFromMethod(self.m)
            tNew = tau.tau.tau
            assert len(tau.tau.aList) == 1 and len(tau.tau.tList) == 1
            t = tau.tau.tList[0]
            a = tau.tau.aList[0]
            ajList = sigma.getVariables()
            if isinstance(sigma, SigmaForall):
                sigmaNew = deepcopy(sigma)
                sigmaNew.aList.append(tc.t)
            elif isinstance(sigma, Rho) or isinstance(sigma, Tau):
                sigmaNew = SigmaForall([tc.t], sigma)
            else:
                sigmaNew = deepcopy(sigma)
            qiList = sigma.getConstraints()
            return (sigmaNew.unambiguous()
                    and (tNew.equals(sigma.getTau())
                         or (isinstance(tNew, TypeSubst) and tNew.evaluate().equals(sigma.getTau())))
                    and a.equals(tc.t)
                    and all(any(ai.equals(aj) for aj in ajList) for ai in tau.aList)
                    and Q(TcTau(tc.name, t)).entails(p, gc, gamma)
                    and t.wellTyped(gamma, gc)
                    and all(QSubst(tau.tList, tau.aList, QSubst(tau.tau.tList, tau.tau.aList, qi)).entails(p, gc, gamma) for qi in qiList)
                    and all(tj.wellTyped(gamma, gc) for tj in tau.tList)
                    and tNew.equals(sigma.getRho().getTau())
                    and p.wellFormed(gc, gamma))
        return False

    def equals(self, e: Term):
        return isinstance(e, TermM) and self.m == e.m

    def elaborate(self, p, gc, gamma):
        pass

    def elaborateWithType(self, p: P, gc: GC, gamma: Gamma, tau: Tau):
        assert isinstance(tau, TypeSubst) and isinstance(tau.tau, TypeSubst)
        assert len(tau.tau.tList) == 1
        tc = gc.getTCFromMethod(self.m)
        d = Q(TcTau(tc.name, tau.tau.tList[0])).getDictionary(p, gc, gamma)
        term = ITermM(d, self.m)
        sj = list(map(lambda tj: tj.elaborate(gc), tau.tList))
        for s in sj:
            term = ITermESigma(term, s)
        sigma = gc.getSigmaFromMethod(self.m)
        tList = tau.tList
        aList = tau.aList
        t = tau.tau.tList
        a = tau.tau.aList
        di = list(map(lambda q: QSubst(tList, aList, QSubst(t, a, q)).elaborate(), sigma.getConstraints()))
        for dictionary in di:
            term = ITermED(term, dictionary)
        return term


class TermAbs(Term):
    def __init__(self, x: str, e: Term):
        super().__init__()
        self.x = x
        self.e = e

    def show(self):
        print("\\" + self.x + ". ", end='')
        self.e.show()

    def getType(self, p: P, gc: GC, gamma: Gamma):
        pass

    def hasType(self, p: P, gc: GC, gamma: Gamma, tau: Tau):
        if isinstance(tau, TypeSubst):
            tau = tau.evaluate()
        if isinstance(tau, TypeArrow):
            gammaNew = deepcopy(gamma)
            gammaNew.elements = deepcopy(gamma.elements)
            gammaNew.addElement(GammaX(self.x, tau.t1))
            return (all(not (isinstance(element, GammaX) and element.x == self.x) for element in gamma.elements)
                    and self.e.hasType(p, gc, gammaNew, tau.t2)
                    and tau.t1.wellTyped(gamma, gc))
        return False

    def equals(self, e: Term):
        return isinstance(e, TermAbs) and self.x == e.x and self.e.equals(e.e)

    def elaborate(self, p, gc, gamma):
        pass

    def elaborateWithType(self, p: P, gc: GC, gamma: Gamma, tau: Tau):
        assert isinstance(tau, TypeArrow)
        sigma = tau.t1.elaborate()
        gammaNew = deepcopy(gamma)
        gammaNew.elements = deepcopy(gamma.elements)
        gammaNew.addElement(GammaX(self.x, tau.t1))
        e = self.e.elaborateWithType(p, gc, gammaNew, tau.t2)
        return ITermAbs(self.x, sigma, e)


class TermApp(Term):
    def __init__(self, e1: Term, e2: Term):
        super().__init__()
        self.e1 = e1
        self.e2 = e2

    def show(self):
        self.e1.show()
        self.e2.show()

    def getType(self, p: P, gc: GC, gamma: Gamma):
        t1 = self.e2.getType(p, gc, gamma)
        tArrow = self.e1.getType(p, gc, gamma)
        if isinstance(tArrow, TypeSubst):
            tArrow = tArrow.evaluate()
        if isinstance(tArrow, TypeArrow) and tArrow.t1.equals(t1):
            return tArrow.t2
        else:
            raise TypeNotMatchingError("Types in application don't match")

    def hasType(self, p: P, gc: GC, gamma: Gamma, tau: Tau):
        return tau.equals(self.getType(p, gc, gamma))

    def equals(self, e: Term):
        return isinstance(e, TermApp) and self.e1.equals(e.e1) and self.e2.equals(e.e2)

    def elaborate(self, p: P, gc: GC, gamma: Gamma):
        t1 = self.e2.getType(p, gc, gamma)
        tArrow = self.e1.getType(p, gc, gamma)
        if isinstance(tArrow, TypeSubst):
            tArrow = tArrow.evaluate()
        if not (isinstance(tArrow, TypeArrow) and tArrow.t1.equals(t1)):
            raise TypeNotMatchingError("Types in application don't match")
        return ITermApp(self.e1.elaborateWithType(p, gc, gamma, tArrow), self.e2.elaborateWithType(p, gc, gamma, t1))

    def elaborateWithType(self, p: P, gc: GC, gamma: Gamma, tau: Tau):
        return self.elaborate(p, gc, gamma)


class TermLet(Term):
    def __init__(self, x: str, sigma: Sigma, e1: Term, e2: Term):
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

    def getType(self, p: P, gc: GC, gamma: Gamma):
        assert self.sigma.unambiguous()
        assert all(not (isinstance(g, GammaX) and self.x == g.x) for g in gamma.elements)
        qk = gc.closure(self.sigma.getConstraints())
        t1 = self.sigma.getTau()
        aList = self.sigma.getVariables()
        sigmaNew = SigmaForall(aList, RhoConstr(qk, deepcopy(t1)))
        assert sigmaNew.wellTyped(gamma, gc)
        gammaNew = deepcopy(gamma)
        gammaNew.elements = deepcopy(gamma.elements)
        gammaNew.addElements(list(map(lambda a: GammaA(a), aList)))
        gammaNew.addElements(list(map(lambda q: GammaQ(q), qk)))
        assert self.e1.hasType(p, gc, gammaNew, t1)
        gammaNew2 = deepcopy(gamma)
        gammaNew2.elements = deepcopy(gamma.elements)
        gammaNew2.addElement(GammaX(self.x, sigmaNew))
        return self.e2.getType(p, gc, gammaNew2)

    def hasType(self, p: P, gc: GC, gamma: Gamma, tau: Tau):
        return tau.equals(self.getType(p, gc, gamma))

    def equals(self, e: Term):
        return isinstance(e, TermLet) and self.x == e.x and self.sigma.equals(e.sigma) and self.e1.equals(
            e.e1) and self.e2.equals(e.e2)

    def elaborate(self, p: P, gc: GC, gamma: Gamma):
        qk = gc.closure(self.sigma.getConstraints())
        t1 = self.sigma.getTau()
        aList = self.sigma.getVariables()

        sigmaNew = SigmaForall(aList, RhoConstr(qk, deepcopy(t1)))
        sigmaElaborated = sigmaNew.elaborate()
        delta = gamma.getDeltaIndex() + len(qk)

        gammaNew = deepcopy(gamma)
        gammaNew.elements = deepcopy(gamma.elements)
        gammaNew.addElements(list(map(lambda a: GammaA(a), aList)))
        gammaNew.addElements(list(map(lambda q: GammaQ(q), qk)))
        gammaNew2 = deepcopy(gamma)
        gammaNew2.elements = deepcopy(gamma.elements)
        gammaNew2.addElement(GammaX(self.x, sigmaNew))
        e1Elaborated = self.e1.elaborateWithType(p, gc, gammaNew, self.sigma.getTau())

        for i in range(1, len(qk)+1):
            e1Elaborated = ITermQAbs(DictionaryDelta(delta), qk[-i].elaborate(), e1Elaborated)
            delta -= 1

        for i in range(1, len(aList)+1):
            e1Elaborated = ITermTypeAbs(aList[-i].elaborate(), e1Elaborated)

        return ITermLet(self.x, sigmaElaborated, e1Elaborated, self.e2.elaborateWithType(p, gc, gammaNew2, self.e2.getType(p, gc, gammaNew2)))

    def elaborateWithType(self, p, gc, gamma, tau):
        return self.elaborate(p, gc, gamma)


class TermDecl(Term):
    def __init__(self, e: Term, tau: Tau):
        super().__init__()
        self.e = e
        self.tau = tau

    def show(self):
        self.e.show()
        print(" :: ", end=" ")
        self.tau.show()

    def getType(self, p: P, gc: GC, gamma: Gamma):
        if self.e.hasType(p, gc, gamma, self.tau):
            return self.tau
        else:
            raise TypeNotMatchingError("Declared type doesnt match actual type")

    def hasType(self, p: P, gc: GC, gamma: Gamma, tau: Tau):
        return tau.equals(self.getType(p, gc, gamma))

    def equals(self, e: Term):
        return isinstance(e, TermDecl) and self.e.equals(e.e) and self.tau.equals(e.tau)

    def elaborateWithType(self, p: P, gc: GC, gamma: Gamma, tau: Tau):
        t1 = self.tau
        t = self.tau
        if isinstance(t1, TypeSubst):
            t1 = t1.evaluate()
        t2 = tau
        if isinstance(t2, TypeSubst):
            t = tau
            t2 = t2.evaluate()
        assert t1.equals(t2)
        return self.e.elaborateWithType(p, gc, gamma, t)

    def elaborate(self, p, gc, gamma):
        return self.e.elaborateWithType(p, gc, gamma, self.tau)
