from copy import deepcopy
from typing import List

from IntermediateLanguage.Dictionaries.Dictionary import DictionaryDelta
from IntermediateLanguage.Environment.Element import IPElem
from IntermediateLanguage.Environment.environment import IP, IGC, IGamma
from IntermediateLanguage.Terms.Term import ITermQAbs, ITermTypeAbs
from SourceLanguageFD.Constraint.TC import FDTCA, FDTCTau
from SourceLanguageFD.Constraint.constraint import FDQ, FDQSubst
from SourceLanguageFD.Environment.AbstractElement import FDGammaElem, FDGCElemAbstract, FDPElemAbstract
from SourceLanguageFD.Environment.AbstractEnvironment import FDAbstractP, FDAbstractGC, FDAbstractGamma
from SourceLanguageFD.Environment.Element import FDGammaX, FDGammaA, FDGammaQ
from SourceLanguageFD.Types.AbstractTypes import FDSigma, FDTau
from SourceLanguageFD.Types.Tau import FDTypeSubst, FDTypeA
from exceptions import NotFoundError


class FDGC(FDAbstractGC):
    elements = []

    def __init__(self, gcList: List[FDGCElemAbstract]):
        super().__init__()
        self.elements = gcList

    def addElement(self, element: FDGCElemAbstract):
        self.elements.append(element)

    def addElements(self, elements: List[FDGCElemAbstract]):
        self.elements = self.elements + elements

    def getSigmaFromName(self, name: str) -> FDSigma:
        for elem in self.elements:
            if elem.tc.name == name:
                return elem.sigma
        raise NotFoundError("Typeclass with name " + name + "was not found in the context.")

    def getSigmaFromMethod(self, m: str) -> FDSigma:
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
                return FDGC(result)
            else:
                result.append(elem)
        raise NotFoundError("Typeclass with name " + name + "was not found in the context.")

    def getTCFromMethod(self, m: str) -> FDTCA:
        for elem in self.elements:
            if elem.m == m:
                return elem.tc
        raise NotFoundError("Method with name " + m + "was not found in the context.")

    def getTCListFromMethod(self, m: str) -> List[FDTCA]:
        for elem in self.elements:
            if elem.m == m:
                return elem.tcList
        raise NotFoundError("Method with name " + m + "was not found in the context.")

    def getTCListFromName(self, name: str) -> List[FDTCA]:
        for elem in self.elements:
            if elem.tc.name == name:
                return elem.tcList
        raise NotFoundError("Typeclass with name " + name + "was not found in the context.")

    def closure(self, qList: List[FDQ]):
        if len(qList) == 0:
            return []
        else:
            qiNew = deepcopy(qList)
            q = qiNew.pop()
            qm = self.getTCListFromName(q.tc.name)
            qiNew += qm
            tList = q.tc.tList
            aList = self.getAFromName(q.tc.name)
            assert len(tList) == len(aList)
            assert all(tList[i].equals(aList[i]) for i in range(len(tList)))
            return self.closure(qiNew) + [q.tc]

    def elaborate(self):
        gcE = deepcopy(self)
        gcE.elements = deepcopy(self.elements)
        gcNew = IGC([])
        while len(gcE.elements) > 0:
            element = gcE.removeLastElement()
            gcNew.insertElement(element.elaborate(self))
        return gcNew

    def inGC(self, aList: List[FDTypeA], tau: FDTau):
        for element in self.elements:
            tList = element.tc.tList
            if element.sigma.getTau().equals(tau) and len(tList) == len(aList) and all(
                    tList[i].equals(aList[i]) for i in range(len(aList))):
                return True
        return False

    def getFDFromName(self, name):
        for elem in self.elements:
            if elem.tc.name == name:
                return elem.fd
        raise NotFoundError("Typeclass with name " + name + "was not found in the context.")

    def getDependants(self, tc):
        aList = self.getAFromName(tc.name)
        fdList = self.getFDFromName(tc.name).aList2
        return substitute(tc.tList, aList, fdList)


class FDGamma(FDAbstractGamma):
    elements = []

    def __init__(self, gammaList: List[FDGammaElem]):
        super().__init__()
        self.elements = gammaList

    def addElement(self, element: FDGammaElem):
        self.elements.append(element)

    def addElements(self, elements: List[FDGammaElem]):
        self.elements = self.elements + elements

    def contains(self, item: FDGammaElem) -> bool:
        return any(element.equals(item) for element in self.elements)

    def containsTypeVar(self, item: FDTypeA) -> bool:
        return any(element.equals(FDGammaA(item)) for element in self.elements)

    def getSigmaFromX(self, x: str) -> FDSigma:
        for element in self.elements:
            if isinstance(element, FDGammaX) and element.x == x:
                return element.sigma
        raise NotFoundError("Variable with name " + x + "was not found in the context.")

    def equals(self, gamma: FDAbstractGamma):
        return (len(gamma.elements) == len(self.elements)
                and all(gamma.elements[i].equals(self.elements[i]) for i in range(len(self.elements))))

    def setElements(self, elements: List[FDGammaElem]):
        self.elements = elements

    def elaborate(self, p: FDAbstractP, gc: FDAbstractGC):
        gammaE = deepcopy(self)
        gammaE.elements = deepcopy(self.elements)
        gammaNew = IGamma([])
        while len(gammaE.elements) > 0:
            element = gammaE.removeLastElement()
            gammaNew.insertElement(element.elaborate(p, gc))
        return gammaNew

    def getDeltaIndex(self):
        i = 0
        for element in self.elements:
            if isinstance(element, FDGammaQ):
                i += 1
        return i

    def getDeltaOfGammaQ(self, gammaQ: FDGammaQ):
        i = 0
        for element in self.elements:
            if isinstance(element, FDGammaQ):
                if element.equals(gammaQ):
                    return i
                else:
                    i += 1
        raise NotFoundError("Constraint was not found in the context.")


def substitute(tList, aList1, aList2):
    assert len(tList) == len(aList1)
    result = deepcopy(aList2)
    for i in range(len(aList1)):
        for j in range(len(aList2)):
            if aList1[i] == aList2[j]:
                result[j] = tList[i]
    return result


class FDP(FDAbstractP):
    elements = []

    def __init__(self):
        super().__init__()
        self.elements = []

    def addElement(self, element: FDPElemAbstract):
        self.elements.append(element)

    def addElements(self, elements: List[FDPElemAbstract]):
        self.elements = self.elements + elements

    def wellFormed(self, gc: FDGC, gamma: FDGamma) -> bool:
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
                    gammaNew = FDGamma(list(map(lambda a: FDGammaA(a), element.tc.tList)))
                    sigma = element.sigma
                    aj = sigma.getVariables() + element.tc.tList
                    return (sigma.wellTyped(gammaNew, gcNew)
                            and all(any(a.equals(fv) for fv in sigma.getTau().getFreeVars()) for a in aj)
                            and all(FDQ(tc).wellFormed(gammaNew, gcNew) for tc in element.tcList)
                            and all(not (element.m == gcElem.m) for gcElem in gcNew.elements)
                            and all(not (element.tc.name == gcElem.tc.name) for gcElem in gcNew.elements)
                            and self.wellFormed(gcNew, gamma))
            else:
                gammaNew = deepcopy(gamma)
                gammaNew.elements = deepcopy(gamma.elements)
                element = gammaNew.removeLastElement()
                if isinstance(element, FDGammaX):
                    # sCtx-TyEnvTm
                    return (element.sigma.wellTyped(gammaNew, gc)
                            and all(not (isinstance(g, FDGammaX) and g.x == element.x) for g in gammaNew.elements)
                            and self.wellFormed(gc, gammaNew))
                elif isinstance(element, FDGammaA):
                    # sCtx-TyEnvTy
                    return (all(not (isinstance(g, FDGammaA) and g.equals(element)) for g in gammaNew.elements)
                            and self.wellFormed(gc, gammaNew))
                elif isinstance(element, FDGammaQ):
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
            gammaElements = list(map(lambda a: FDGammaA(a), bj))
            gammaElements += list(map(lambda q: FDGammaQ(q), element.c.qList))
            tc = gc.getTCFromMethod(element.m)
            sigma = gc.getSigmaFromMethod(element.m)
            gammaElements += list(map(lambda a: FDGammaA(a), sigma.getVariables()))
            gammaElements += list(map(lambda q: FDGammaQ(FDQSubst(tList, tc.tList, q)), sigma.getConstraints()))
            gammaNew = FDGamma(gammaElements)
            tauSubst = FDTypeSubst(tList, tc.tList, sigma.getTau())
            for i in range(len(pNew.elements)):
                if pNew.elements[i].c.q.tc.name == tc.name:
                    bk = pNew.elements[i].c.aList
                    tOtherList = pNew.elements[i].c.q.tc.tList
                    if all(tList[j].equalsWithVars(bj, tOtherList[j], bk) for j in range(len(tList))):
                        return False

            return (element.gamma.equals(gammaNew)
                    and element.c.unambiguous(pNew, gc)
                    and element.c.wellFormed(FDGamma([]), gc)
                    and element.e.hasType(pNew, gc, gammaNew, tauSubst)
                    and sigma.wellTyped(FDGamma(list(map(lambda a: FDGammaA(a), tc.tList))), gc)
                    and pNew.wellFormed(gc, gamma))

    def getQiFromQ(self, q: FDQ):
        for element in self.elements:
            if element.c.q.equals(q):
                return element.c.qList
        raise NotFoundError("Instantiation with typeclass " + q.tc.name + "was not found in the context.")

    def getDFromQ(self, q: FDQ):
        for i in range(len(self.elements)):
            element = self.elements[i]
            if element.c.q.equals(q):
                return i
        raise NotFoundError("Instantiation with typeclass " + q.tc.name + "was not found in the context.")

    def elaborate(self, gc: FDGC):
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
            gammaNew = FDGamma(list(map(lambda bi: FDGammaA(bi), bj))
                               + list(map(lambda qj: FDGammaQ(qj), qi))
                               + list(map(lambda ai: FDGammaA(ai), ak))
                               + list(map(lambda qj: FDGammaQ(qj), qh)))
            e = element.e.elaborateWithType(pE, gc, gammaNew, FDTypeSubst(t, a, tNew))
            delta = len(qi) + len(qh)
            for q in qh:
                e = ITermQAbs(DictionaryDelta(delta), FDQSubst(t, a, q).elaborate(pNew, gc), e)
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

    def hasFunctionalDependency(self, gc: FDGC, tc: FDTCTau):
        aList = gc.getAFromName(tc.name)
        tList = tc.tList
        fdList = gc.getFDFromName(tc.name).aList1
        fdResult = substitute(tList, aList, fdList)
        if len(fdList) == 0:
            return False
        for element in self.elements:
            if element.c.q.tc.name == tc.name:
                fdResult2 = substitute(element.c.q.tc.tList, aList, fdList)
                if all(fdResult[i].equals(fdResult2[i]) for i in range(len(fdResult))):
                    return True
        return False

    def getFunctionalDependency(self, gc: FDGC, tc: FDTCTau):
        aList = gc.getAFromName(tc.name)
        tList = tc.tList
        fdList = gc.getFDFromName(tc.name).aList1
        fdResult = substitute(tList, aList, fdList)
        for element in self.elements:
            if element.c.q.tc.name == tc.name:
                fdResult2 = substitute(element.c.q.tc.tList, aList, fdList)
                if all(fdResult[i].equals(fdResult2[i]) for i in range(len(fdResult))):
                    return element.c.q.tc
