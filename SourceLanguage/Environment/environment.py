from copy import deepcopy
from typing import List

from IntermediateLanguage.Dictionaries.Dictionary import DictionaryDelta
from IntermediateLanguage.Environment.Element import IPElem
from IntermediateLanguage.Environment.environment import IP, IGC, IGamma
from IntermediateLanguage.Terms.Term import ITermQAbs, ITermTypeAbs
from SourceLanguage.Constraint.TC import TcA
from SourceLanguage.Constraint.constraint import Q, QSubst
from SourceLanguage.Environment.AbstractElement import GammaElem, GCElemAbstract, PElemAbstract
from SourceLanguage.Environment.AbstractEnvironment import AbstractP, AbstractGC, AbstractGamma
from SourceLanguage.Environment.Element import GammaX, GammaA, GammaQ
from SourceLanguage.Types.AbstractTypes import Sigma
from SourceLanguage.Types.Tau import TypeSubst, TypeA
from exceptions import NotFoundError


class Gamma(AbstractGamma):
    elements = []

    def __init__(self, gammaList: List[GammaElem]):
        super().__init__()
        self.elements = gammaList

    def addElement(self, element: GammaElem):
        self.elements.append(element)

    def addElements(self, elements: List[GammaElem]):
        self.elements = self.elements + elements

    def contains(self, item: GammaElem) -> bool:
        return any(element.equals(item) for element in self.elements)

    def containsTypeVar(self, item: TypeA) -> bool:
        return any(element.equals(GammaA(item)) for element in self.elements)

    def getSigmaFromX(self, x: str) -> Sigma:
        for element in self.elements:
            if isinstance(element, GammaX) and element.x == x:
                return element.sigma
        raise NotFoundError("Variable with name " + x + "was not found in the context.")

    def equals(self, gamma: AbstractGamma):
        return (len(gamma.elements) == len(self.elements)
                and all(gamma.elements[i].equals(self.elements[i]) for i in range(len(self.elements))))

    def setElements(self, elements: List[GammaElem]):
        self.elements = elements

    def getDeltaIndex(self):
        i = 0
        for element in self.elements:
            if isinstance(element, GammaQ):
                i += 1
        return i

    def getDeltaOfGammaQ(self, gammaQ: GammaQ):
        i = 0
        for element in self.elements:
            if isinstance(element, GammaQ):
                if element.equals(gammaQ):
                    return i
                else:
                    i += 1
        raise NotFoundError("Constraint was not found in the context.")

    def insertElement(self, element: GammaElem):
        self.elements.insert(0, element)

    def elaborate(self):
        gammaE = deepcopy(self)
        gammaE.elements = deepcopy(self.elements)
        gammaNew = IGamma([])
        while len(gammaE.elements) > 0:
            element = gammaE.removeLastElement()
            gammaNew.insertElement(element.elaborate())
        return gammaNew


class GC(AbstractGC):
    elements = []

    def __init__(self, gcList: List[GCElemAbstract]):
        super().__init__()
        self.elements = gcList

    def addElement(self, element: GCElemAbstract):
        self.elements.append(element)

    def addElements(self, elements: List[GCElemAbstract]):
        self.elements = self.elements + elements

    def getSigmaFromName(self, name: str) -> Sigma:
        for elem in self.elements:
            if elem.tc.name == name:
                return elem.sigma
        raise NotFoundError("Typeclass with name " + name + "was not found in the context.")

    def getSigmaFromMethod(self, m: str) -> Sigma:
        for elem in self.elements:
            if elem.m == m:
                return elem.sigma
        raise NotFoundError("Method with name " + m + "was not found in the context.")

    def getAFromName(self, name: str):
        for elem in self.elements:
            if elem.tc.name == name:
                return elem.tc.t
        raise NotFoundError("Typeclass with name " + name + "was not found in the context.")

    def getGC1FromName(self, name: str):
        result = []
        for elem in self.elements:
            if elem.tc.name == name:
                return GC(result)
            else:
                result.append(elem)
        raise NotFoundError("Typeclass with name " + name + "was not found in the context.")

    def getTCFromMethod(self, m: str) -> TcA:
        for elem in self.elements:
            if elem.m == m:
                return elem.tc
        raise NotFoundError("Method with name " + m + "was not found in the context.")

    def getTCListFromMethod(self, m: str) -> List[TcA]:
        for elem in self.elements:
            if elem.m == m:
                return elem.tcList
        raise NotFoundError("Method with name " + m + "was not found in the context.")

    def getTCListFromName(self, name: str) -> List[TcA]:
        for elem in self.elements:
            if elem.tc.name == name:
                return elem.tcList
        raise NotFoundError("Typeclass with name " + name + "was not found in the context.")

    def closure(self, qList: List[Q]):
        if len(qList) == 0:
            return []
        else:
            qiNew = deepcopy(qList)
            q = qiNew.pop()
            qm = self.getTCListFromName(q.tc.name)
            qiNew += list(map(lambda tc: Q(tc), qm))
            assert q.tc.t.equals(self.getAFromName(q.tc.name))
            return self.closure(qiNew) + [q]

    def insertElement(self, element: GCElemAbstract):
        self.elements.insert(0, element)

    def elaborate(self):
        gcE = deepcopy(self)
        gcE.elements = deepcopy(self.elements)
        gcNew = IGC([])
        while len(gcE.elements) > 0:
            element = gcE.removeLastElement()
            gcNew.insertElement(element.elaborate())
        return gcNew


class P(AbstractP):
    elements = []

    def __init__(self):
        super().__init__()
        self.elements = []

    def addElement(self, element: PElemAbstract):
        self.elements.append(element)

    def addElements(self, elements: List[PElemAbstract]):
        self.elements = self.elements + elements

    def wellFormed(self, gc: GC, gamma: Gamma) -> bool:
        if len(self.elements) == 0:
            if len(gamma.elements) == 0:
                if len(gc.elements) == 0:
                    # sCtx-empty
                    return True
                else:
                    # sCtx-clsEnv
                    gcNew = deepcopy(gc)
                    element = gcNew.removeLastElement()
                    gammaNew = Gamma([GammaA(element.tc.t)])
                    sigma = element.sigma
                    aj = sigma.getVariables() + [element.tc.t]
                    return (sigma.wellTyped(gammaNew, gcNew)
                            and all(any(a.equals(fv) for fv in sigma.getTau().getFreeVars()) for a in aj)
                            and all(Q(tc).wellFormed(gammaNew, gcNew) for tc in element.tcList)
                            and all(not (element.m == gcElem.m) for gcElem in gcNew.elements)
                            and all(not (element.tc.name == gcElem.tc.name) for gcElem in gcNew.elements)
                            and self.wellFormed(gcNew, gamma))
            else:
                gammaNew = deepcopy(gamma)
                gammaNew.elements = deepcopy(gamma.elements)
                element = gammaNew.removeLastElement()
                if isinstance(element, GammaX):
                    # sCtx-TyEnvTm
                    return (element.sigma.wellTyped(gammaNew, gc)
                            and all(not (isinstance(g, GammaX) and g.x == element.x) for g in gammaNew.elements)
                            and self.wellFormed(gc, gammaNew))
                elif isinstance(element, GammaA):
                    # sCtx-TyEnvTy
                    return (all(not (isinstance(g, GammaA) and g.equals(element)) for g in gammaNew.elements)
                            and self.wellFormed(gc, gammaNew))
                elif isinstance(element, GammaQ):
                    # sCtx-TyEnvD
                    return (element.q.wellFormed(gammaNew, gc)
                            and self.wellFormed(gc, gammaNew))
                else:
                    return False
        else:
            # sCtx-PgmInst
            pNew = deepcopy(self)
            pNew.elements = deepcopy(self.elements)
            element = pNew.removeLastElement()
            tau = element.c.q.tc.t
            bj = element.c.aList
            gammaElements = list(map(lambda a: GammaA(a), bj))
            gammaElements += list(map(lambda q: GammaQ(q), element.c.qList))
            tc = gc.getTCFromMethod(element.m)
            sigma = gc.getSigmaFromMethod(element.m)
            gammaElements += list(map(lambda a: GammaA(a), sigma.getVariables()))
            gammaElements += list(map(lambda q: GammaQ(QSubst([tau], [tc.t], q)), sigma.getConstraints()))
            gammaNew = Gamma(gammaElements)
            tauSubst = TypeSubst([tau], [tc.t], sigma.getTau())
            for i in range(len(pNew.elements)):
                if pNew.elements[i].c.q.tc.name == tc.name:
                    bk = pNew.elements[i].c.aList
                    tOther = pNew.elements[i].c.q.tc.t
                    if tau.equalsWithVars(bj, tOther, bk):
                        return False

            return (element.gamma.equals(gammaNew)
                    and element.c.unambiguous()
                    and element.c.wellFormed(Gamma([]), gc)
                    and element.e.hasType(pNew, gc, gammaNew, tauSubst)
                    and sigma.wellTyped(Gamma([GammaA(tc.t)]), gc)
                    and pNew.wellFormed(gc, gamma))

    def getQiFromQ(self, q: Q):
        for element in self.elements:
            if element.c.q.equals(q):
                return element.c.qList
        raise NotFoundError("Instantiation with typeclass " + q.tc.name + "was not found in the context.")

    def getDFromQ(self, q: Q):
        for i in range(len(self.elements)):
            element = self.elements[i]
            if element.c.q.equals(q):
                return i
        raise NotFoundError("Instantiation with typeclass " + q.tc.name + "was not found in the context.")

    def elaborate(self, gc: GC):
        pE = deepcopy(self)
        pE.elements = deepcopy(self.elements)
        pNew = IP()

        while len(pE.elements) > 0:
            element = pE.removeLastElement()
            bj = element.c.aList
            qi = element.c.qList
            sigma = gc.getSigmaFromName(element.c.tc.name)
            ak = sigma.getVariables()
            qh = sigma.getConstraints()
            t = element.c.tc.t
            a = gc.getAFromName(element.c.tc.name)
            tNew = sigma.getTau()
            gammaNew = Gamma(list(map(lambda bi: GammaA(bi), bj))
                             + list(map(lambda qj: GammaQ(qj), qi))
                             + list(map(lambda ai: GammaA(ai), ak))
                             + list(map(lambda qj: GammaQ(qj), qh)))
            e = element.e.elaborateWithType(pE, gc, gammaNew, ([t], [a], TypeSubst([t], [a], tNew)))
            delta = len(qi) + len(qh)
            for q in qh:
                e = ITermQAbs(DictionaryDelta(delta), QSubst([t], [a], q).elaborate(), e)
                delta -= 1
            for a in ak:
                e = ITermTypeAbs(a.elaborate(), e)
            for q in qi:
                e = ITermQAbs(DictionaryDelta(delta), q.elaborate(), e)
                delta -= 1
            for a in bj:
                e = ITermTypeAbs(a.elaborate(), e)
            pNew.insertElement(IPElem(element.c.elaborate(), element.m, e))
        return pNew

    def insertElement(self, element: PElemAbstract):
        self.elements.insert(0, element)
