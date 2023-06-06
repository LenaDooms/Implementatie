import unittest

from IntermediateLanguage.Constraint.TC import ITCTau
from IntermediateLanguage.Constraint.constraint import IQ, IC
from IntermediateLanguage.Types.Sigma import ITypeConstr, ITypeArrow, ITypeBool
from SourceLanguageFD.Programs.FD import FD
from SourceLanguageFD.Constraint.TC import FDTCA, FDTCTau
from SourceLanguageFD.Constraint.constraint import FDC, FDQ
from SourceLanguageFD.Environment.Element import FDGammaX, FDPElem, FDGCElem, FDGammaA
from SourceLanguageFD.Environment.environment import FDP, FDGC, FDGamma
from SourceLanguageFD.Programs.program import FDInst, FDCls
from SourceLanguageFD.Terms.Term import FDTermTrue, FDTermFalse, FDTermX, FDTermM, FDTermAbs, FDTermDecl, FDTermApp, \
    FDTermLet
from SourceLanguageFD.Types.Rho import FDRhoConstr
from SourceLanguageFD.Types.Sigma import FDSigmaForall
from SourceLanguageFD.Types.Tau import FDTypeBool, FDTypeA, FDTypeSubst, FDTypeArrow
from exceptions import NotFoundError, TypeNotMatchingError, AlreadyExistsError


class functionalDependencies(unittest.TestCase):

    def test_sigma(self):
        a = FDTypeA("a")
        b = FDTypeA("b")
        boolean = FDTypeBool()
        tau = FDTypeArrow(a, FDTypeArrow(b, b))
        #  TC a b | a ~> b
        cls = FDCls([], FDTCA("TC", [a, b]), "m", tau, FD([a], [b]))
        gc = FDGC([])
        cls.addToGC(FDP(), gc)
        #  \x.\y. y
        m = FDTermAbs("x", FDTermAbs("y", FDTermX("y")))
        #  TC bool bool
        inst1 = FDInst([], FDTCTau("TC", [boolean, boolean]), "m", m)
        p = FDP()
        inst1.addToP(p, gc)
        x = FDTypeA("x")
        y = FDTypeA("y")
        q1 = FDQ(FDTCTau("TC", [x, y]))
        q2 = FDQ(FDTCTau("TC", [boolean, x]))
        #  Forall x y. TC x y => TC bool x => bool -> y
        sigma = FDSigmaForall([x, y], FDRhoConstr([q1, q2], FDTypeArrow(boolean, y)))
        sigmaNew = sigma.elaborate(p, gc)
        #  bool -> bool -> bool
        arrow = ITypeArrow(ITypeBool(), ITypeArrow(ITypeBool(), ITypeBool()))
        #  TC bool->bool->bool => TC bool->bool->bool => bool -> bool
        itc = IQ(ITCTau("TC", arrow))

        expectedSigma = ITypeConstr(itc, ITypeConstr(itc, ITypeArrow(ITypeBool(), ITypeBool())))
        self.assertTrue(sigmaNew.equals(expectedSigma))

    def test_constraint(self):
        a = FDTypeA("a")
        b = FDTypeA("b")
        boolean = FDTypeBool()
        tau = FDTypeArrow(a, FDTypeArrow(b, b))
        #  TC a b | a ~> b
        cls = FDCls([], FDTCA("TC", [a, b]), "m", tau, FD([a], [b]))
        gc = FDGC([])
        cls.addToGC(FDP(), gc)
        #  \x.\y. y
        m = FDTermAbs("x", FDTermAbs("y", FDTermX("y")))
        #  TC bool bool
        inst1 = FDInst([], FDTCTau("TC", [boolean, boolean]), "m", m)
        p = FDP()
        inst1.addToP(p, gc)
        x = FDTypeA("x")
        y = FDTypeA("y")
        q1 = FDQ(FDTCTau("TC", [x, y]))
        q2 = FDQ(FDTCTau("TC", [boolean, x]))
        q = FDQ(FDTCTau("TC", [y, boolean]))
        #  Forall x y. TC x y => TC bool x => TC y Bool
        c = FDC([x, y], [q1, q2], q)
        cNew = c.elaborate(p, gc)
        #  bool -> bool -> bool
        arrow = ITypeArrow(ITypeBool(), ITypeArrow(ITypeBool(), ITypeBool()))
        #  TC bool->bool->bool => TC bool->bool->bool => TC bool->bool->bool
        itc = IQ(ITCTau("TC", arrow))
        expectedC = IC([], [itc, itc], itc)
        self.assertTrue(cNew.equals(expectedC))


if __name__ == '__main__':
    unittest.main()
