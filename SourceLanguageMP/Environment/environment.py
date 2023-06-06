from copy import deepcopy
from typing import List

from IntermediateLanguage.Dictionaries.Dictionary import DictionaryDelta
from IntermediateLanguage.Environment.Element import IPElem
from IntermediateLanguage.Environment.environment import IP, IGC, IGamma
from IntermediateLanguage.Terms.Term import ITermQAbs, ITermTypeAbs
from SourceLanguageMP.Constraint.TC import MPTCA
from SourceLanguageMP.Constraint.constraint import MPQ, MPQSubst
from SourceLanguageMP.Environment.AbstractElement import MPGammaElem, MPGCElemAbstract, MPPElemAbstract
from SourceLanguageMP.Environment.AbstractEnvironment import MPAbstractP, MPAbstractGC, MPAbstractGamma
from SourceLanguageMP.Environment.Element import MPGammaX, MPGammaA, MPGammaQ
from SourceLanguageMP.Types.AbstractTypes import MPSigma, MPTau
from SourceLanguageMP.Types.Tau import MPTypeSubst, MPTypeA
from exceptions import NotFoundError


class MPGC(MPAbstractGC):
    elements = []

    def __init__(self, gcList: List[MPGCElemAbstract]):
        super().__init__()
        self.elements = gcList

    def addElement(self, element: MPGCElemAbstract):
        self.elements.append(element)

    def addElements(self, elements: List[MPGCElemAbstract]):
        self.elements = self.elements + elements

    def getSigmaFromName(self, name: str) -> MPSigma:
        for elem in self.elements:
            if elem.tc.name == name:
                return elem.sigma
        raise NotFoundError("Typeclass with name " + name + "was not found in the context.")

    def getSigmaFromMethod(self, m: str) -> MPSigma:
        for elem in self.elements:
            if elem.m == m:
                return elem.sigma
        raise NotFoundError("Method with name " + m + "was not found in the context.")

    def getAFromName(self, name: str):
        for elem in self.elements:
            if elem.tc.name == name:
                return elem.tc.tList
        raise NotFoundError("Typeclass with name " + name + "was not found in the context.")

    def getGC1FromName(self, name: str):
        result = []
        for elem in self.elements:
            if elem.tc.name == name:
                return MPGC(result)
            else:
                result.append(elem)
        raise NotFoundError("Typeclass with name " + name + "was not found in the context.")

    def getTCFromMethod(self, m: str) -> MPTCA:
        for elem in self.elements:
            if elem.m == m:
                return elem.tc
        raise NotFoundError("Method with name " + m + "was not found in the context.")

    def getTCListFromMethod(self, m: str) -> List[MPTCA]:
        for elem in self.elements:
            if elem.m == m:
                return elem.tcList
        raise NotFoundError("Method with name " + m + "was not found in the context.")

    def getTCListFromName(self, name: str) -> List[MPTCA]:
        for elem in self.elements:
            if elem.tc.name == name:
                return elem.tcList
        raise NotFoundError("Typeclass with name " + name + "was not found in the context.")

    def closure(self, qList: List[MPQ]):
        if len(qList) == 0:
            return []
        else:
            qiNew = deepcopy(qList)
            q = qiNew.pop()
            qm = self.getTCListFromName(q.tc.name)
            qiNew += list(map(lambda tc: MPQ(tc), qm))
            tList = q.tc.tList
            aList = self.getAFromName(q.tc.name)
            assert len(tList) == len(aList)
            assert all(tList[i].equals(aList[i]) for i in range(len(tList)))
            return self.closure(qiNew) + [q]

    def elaborate(self):
        gcE = deepcopy(self)
        gcE.elements = deepcopy(self.elements)
        gcNew = IGC([])
        while len(gcE.elements) > 0:
            element = gcE.removeLastElement()
            gcNew.insertElement(element.elaborate(self))
        return gcNew

    def inGC(self, aList: List[MPTypeA], tau: MPTau):
        for element in self.elements:
            tList = element.tc.tList
            if element.sigma.getTau().equals(tau) and len(tList) == len(aList) and all(
                    tList[i].equals(aList[i]) for i in range(len(aList))):
                return True
        return False


class MPGamma(MPAbstractGamma):
    elements = []

    def __init__(self, gammaList: List[MPGammaElem]):
        super().__init__()
        self.elements = gammaList

    def addElement(self, element: MPGammaElem):
        self.elements.append(element)

    def addElements(self, elements: List[MPGammaElem]):
        self.elements = self.elements + elements

    def contains(self, item: MPGammaElem) -> bool:
        return any(element.equals(item) for element in self.elements)

    def containsTypeVar(self, item: MPTypeA) -> bool:
        return any(element.equals(MPGammaA(item)) for element in self.elements)

    def getSigmaFromX(self, x: str) -> MPSigma:
        for element in self.elements:
            if isinstance(element, MPGammaX) and element.x == x:
                return element.sigma
        raise NotFoundError("Variable with name " + x + "was not found in the context.")

    def equals(self, gamma: MPAbstractGamma):
        return (len(gamma.elements) == len(self.elements)
                and all(gamma.elements[i].equals(self.elements[i]) for i in range(len(self.elements))))

    def setElements(self, elements: List[MPGammaElem]):
        self.elements = elements

    def elaborate(self, gc: MPAbstractGC):
        gammaE = deepcopy(self)
        gammaE.elements = deepcopy(self.elements)
        gammaNew = IGamma([])
        while len(gammaE.elements) > 0:
            element = gammaE.removeLastElement()
            gammaNew.insertElement(element.elaborate(gc))
        return gammaNew

    def getDeltaIndex(self):
        i = 0
        for element in self.elements:
            if isinstance(element, MPGammaQ):
                i += 1
        return i

    def getDeltaOfGammaQ(self, gammaQ: MPGammaQ):
        i = 0
        for element in self.elements:
            if isinstance(element, MPGammaQ):
                if element.equals(gammaQ):
                    return i
                else:
                    i += 1
        raise NotFoundError("Constraint was not found in the context.")


class MPP(MPAbstractP):
    elements = []

    def __init__(self):
        super().__init__()
        self.elements = []

    def addElement(self, element: MPPElemAbstract):
        self.elements.append(element)

    def addElements(self, elements: List[MPPElemAbstract]):
        self.elements = self.elements + elements

    def wellFormed(self, gc: MPGC, gamma: MPGamma) -> bool:
        if len(self.elements) == 0:
            if len(gamma.elements) == 0:
                if len(gc.elements) == 0:
                    # sCtx-empty
                    return True
                else:
                    # sCtx-clsEnv
                    gcNew = deepcopy(gc)
                    gcNew.elements = deepcopy(gc.elements)
                    element = gcNew.removeLastElement()
                    gammaNew = MPGamma(list(map(lambda a: MPGammaA(a), element.tc.tList)))
                    sigma = element.sigma
                    aj = sigma.getVariables() + element.tc.tList
                    return (sigma.wellTyped(gammaNew, gcNew)
                            and all(any(a.equals(fv) for fv in sigma.getTau().getFreeVars()) for a in aj)
                            and all(MPQ(tc).wellFormed(gammaNew, gcNew) for tc in element.tcList)
                            and all(not (element.m == gcElem.m) for gcElem in gcNew.elements)
                            and all(not (element.tc.name == gcElem.tc.name) for gcElem in gcNew.elements)
                            and self.wellFormed(gcNew, gamma))
            else:
                gammaNew = deepcopy(gamma)
                gammaNew.elements = deepcopy(gamma.elements)
                element = gammaNew.removeLastElement()
                if isinstance(element, MPGammaX):
                    # sCtx-TyEnvTm
                    return (element.sigma.wellTyped(gammaNew, gc)
                            and all(not (isinstance(g, MPGammaX) and g.x == element.x) for g in gammaNew.elements)
                            and self.wellFormed(gc, gammaNew))
                elif isinstance(element, MPGammaA):
                    # sCtx-TyEnvTy
                    return (all(not (isinstance(g, MPGammaA) and g.equals(element)) for g in gammaNew.elements)
                            and self.wellFormed(gc, gammaNew))
                elif isinstance(element, MPGammaQ):
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
            tList = element.c.q.tc.tList
            bj = element.c.aList
            gammaElements = list(map(lambda a: MPGammaA(a), bj))
            gammaElements += list(map(lambda q: MPGammaQ(q), element.c.qList))
            tc = gc.getTCFromMethod(element.m)
            sigma = gc.getSigmaFromMethod(element.m)
            gammaElements += list(map(lambda a: MPGammaA(a), sigma.getVariables()))
            gammaElements += list(map(lambda q: MPGammaQ(MPQSubst(tList, tc.tList, q)), sigma.getConstraints()))
            gammaNew = MPGamma(gammaElements)
            tauSubst = MPTypeSubst(tList, tc.tList, sigma.getTau())
            for i in range(len(pNew.elements)):
                if pNew.elements[i].c.q.tc.name == tc.name:
                    bk = pNew.elements[i].c.aList
                    tOtherList = pNew.elements[i].c.q.tc.tList
                    if all(tList[j].equalsWithVars(bj, tOtherList[j], bk) for j in range(len(tList))):
                        return False

            return (element.gamma.equals(gammaNew)
                    and element.c.unambiguous()
                    and element.c.wellFormed(MPGamma([]), gc)
                    and element.e.hasType(pNew, gc, gammaNew, tauSubst)
                    and sigma.wellTyped(MPGamma(list(map(lambda a: MPGammaA(a), tc.tList))), gc)
                    and pNew.wellFormed(gc, gamma))

    def getQiFromQ(self, q: MPQ):
        for element in self.elements:
            if element.c.q.equals(q):
                return element.c.qList
        raise NotFoundError("Instantiation with typeclass " + q.tc.name + "was not found in the context.")

    def getDFromQ(self, q: MPQ):
        for i in range(len(self.elements)):
            element = self.elements[i]
            if element.c.q.equals(q):
                return i
        raise NotFoundError("Instantiation with typeclass " + q.tc.name + "was not found in the context.")

    def elaborate(self, gc: MPGC):
        pE = deepcopy(self)
        pE.elements = deepcopy(self.elements)
        pNew = IP()

        while len(pE.elements) > 0:
            element = pE.removeLastElement()
            bj = element.c.aList
            qi = element.c.qList
            sigma = gc.getSigmaFromName(element.c.q.tc.name)
            ak = sigma.getVariables()
            qh = sigma.getConstraints()
            t = element.c.q.tc.tList
            a = gc.getAFromName(element.c.q.tc.name)
            tNew = sigma.getTau()
            gammaNew = MPGamma(list(map(lambda bi: MPGammaA(bi), bj))
                               + list(map(lambda qj: MPGammaQ(qj), qi))
                               + list(map(lambda ai: MPGammaA(ai), ak))
                               + list(map(lambda qj: MPGammaQ(qj), qh)))
            e = element.e.elaborateWithType(pE, gc, gammaNew, MPTypeSubst(t, a, tNew))
            delta = len(qi) + len(qh)
            for q in qh:
                e = ITermQAbs(DictionaryDelta(delta), MPQSubst(t, a, q).elaborate(gc), e)
                delta -= 1
            for a in ak:
                e = ITermTypeAbs(a.elaborate(), e)
            for q in qi:
                e = ITermQAbs(DictionaryDelta(delta), q.elaborate(), e)
                delta -= 1
            for a in bj:
                e = ITermTypeAbs(a.elaborate(), e)
            pNew.insertElement(IPElem(element.c.elaborate(gc), element.m, e))
        return pNew
