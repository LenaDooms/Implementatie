import unittest

from SourceLanguageFD.Programs.FD import FD
from SourceLanguageFD.Constraint.TC import FDTCA, FDTCTau
from SourceLanguageFD.Constraint.constraint import FDC, FDQ
from SourceLanguageFD.Environment.Element import FDGammaX, FDPElem, FDGCElem, FDGammaA
from SourceLanguageFD.Environment.environment import FDP, FDGC, FDGamma
from SourceLanguageFD.Programs.program import FDInst, FDCls
from SourceLanguageFD.Terms.Term import FDTermTrue, FDTermFalse, FDTermX, FDTermM, FDTermAbs, FDTermDecl, FDTermApp, FDTermLet
from SourceLanguageFD.Types.Rho import FDRhoConstr
from SourceLanguageFD.Types.Sigma import FDSigmaForall
from SourceLanguageFD.Types.Tau import FDTypeBool, FDTypeA, FDTypeSubst, FDTypeArrow
from exceptions import NotFoundError, TypeNotMatchingError, AlreadyExistsError


class general(unittest.TestCase):

    def test_fv(self):
        a = FDTypeA("a")
        b = FDTypeA("b")
        sigma = FDSigmaForall([a], FDTypeArrow(a, b))
        self.assertTrue(len(sigma.getFreeVars()) == 1)
        self.assertTrue(b.equals(sigma.getFreeVars()[0]))


class Types(unittest.TestCase):

    def test_true(self):
        true = FDTermTrue()
        boolean = FDTypeBool()
        a = FDTypeA("a")
        self.assertTrue(true.hasType(FDP(), FDGC([]), FDGamma([]), boolean))
        self.assertFalse(true.hasType(FDP(), FDGC([]), FDGamma([]), a))
        self.assertTrue(true.getType(FDP(), FDGC([]), FDGamma([])).equals(boolean))
        self.assertFalse(true.getType(FDP(), FDGC([]), FDGamma([])).equals(a))

    def test_false(self):
        false = FDTermFalse()
        boolean = FDTypeBool()
        a = FDTypeA("a")
        self.assertTrue(false.hasType(FDP(), FDGC([]), FDGamma([]), boolean))
        self.assertFalse(false.hasType(FDP(), FDGC([]), FDGamma([]), a))
        self.assertTrue(false.getType(FDP(), FDGC([]), FDGamma([])).equals(boolean))
        self.assertFalse(false.getType(FDP(), FDGC([]), FDGamma([])).equals(a))

    def test_substitute(self):
        tau = FDTypeA("a")
        with self.assertRaises(AssertionError):
            FDTypeSubst([FDTypeBool(), FDTypeBool()], [FDTypeA("a")], tau)
        tauSubst = FDTypeSubst([FDTypeBool()], [FDTypeA("a")], tau)
        evaluated = tauSubst.evaluate()
        self.assertTrue(evaluated.equals(FDTypeBool()))

    def test_var(self):
        x = FDTermX("x")
        tau = FDTypeA("a")
        tauSubst1 = FDTypeSubst([FDTypeBool()], [FDTypeA("a")], tau)
        sigma1 = FDSigmaForall([FDTypeA("a")], FDRhoConstr([], tau))
        tauSubst2 = FDTypeSubst([FDTypeBool()], [FDTypeA("b")], tau)
        with self.assertRaises(NotFoundError):
            x.hasType(FDP(), FDGC([]), FDGamma([]), tauSubst1)
        self.assertTrue(x.hasType(FDP(), FDGC([]), FDGamma([FDGammaX("x", sigma1)]), tauSubst1))
        self.assertFalse(x.hasType(FDP(), FDGC([]), FDGamma([FDGammaX("x", sigma1)]), tauSubst2))

    def test_let(self):
        term = FDTermLet("x", FDTypeBool(), FDTermTrue(), FDTermX("x"))
        self.assertFalse(term.hasType(FDP(), FDGC([]), FDGamma([]), FDTypeA("a")))
        self.assertTrue(term.hasType(FDP(), FDGC([]), FDGamma([]), FDTypeBool()))

    def test_method_fail_type(self):
        m = FDTermM("m")
        tauFail = FDTypeArrow(FDTypeA("a"), FDTypeA("b"))  # a -> b
        tauSubFail = FDTypeSubst([FDTypeBool(), FDTypeA("c")], [FDTypeA("a"), FDTypeA("b")], tauFail)
        tauSubSubFail = FDTypeSubst([FDTypeBool()], [FDTypeA("c")], tauSubFail)
        tau = FDTypeA("a")  # a
        sigma = FDSigmaForall([], FDRhoConstr([], tau))
        gcElem = FDGCElem("m", [], FDTCA("TC", [FDTypeA("a")]), sigma, FD([], []))
        c = FDC([], [], FDQ(FDTCTau("TC", [FDTypeBool()])))
        pElem = FDPElem(c, "m", FDGamma([]), FDTermTrue())
        p = FDP()
        p.addElement(pElem)
        self.assertFalse(m.hasType(p, FDGC([gcElem]), FDGamma([]), tauSubSubFail))

    def test_method_empty_context(self):
        m = FDTermM("m")
        tau = FDTypeA("a")  # a
        tauSub = FDTypeSubst([FDTypeBool()], [FDTypeA("a")], tau)
        tauSubSub = FDTypeSubst([], [], tauSub)
        with self.assertRaises(NotFoundError):
            m.hasType(FDP(), FDGC([]), FDGamma([]), tauSubSub)

    def test_method(self):
        m = FDTermM("m")
        tau = FDTypeA("a")  # a
        tauSub = FDTypeSubst([FDTypeBool()], [FDTypeA("a")], tau)
        tauSubSub = FDTypeSubst([], [], tauSub)
        sigma = FDSigmaForall([], FDRhoConstr([], tau))
        gcElem = FDGCElem("m", [], FDTCA("TC", [FDTypeA("a")]), sigma, FD([], []))
        c = FDC([], [], FDQ(FDTCTau("TC", [FDTypeBool()])))
        pElem = FDPElem(c, "m", FDGamma([]), FDTermTrue())
        p = FDP()
        p.addElement(pElem)
        self.assertTrue(m.hasType(p, FDGC([gcElem]), FDGamma([]), tauSubSub))

    def test_abstraction(self):
        term = FDTermAbs("x", FDTermX("x"))
        type1 = FDTypeArrow(FDTypeBool(), FDTypeBool())  # bool -> bool
        self.assertTrue(term.hasType(FDP(), FDGC([]), FDGamma([]), type1))
        a = FDTypeA("a")
        type2 = FDTypeArrow(a, a)  # a -> a
        self.assertTrue(term.hasType(FDP(), FDGC([]), FDGamma([FDGammaA(a)]), type2))
        type3 = FDTypeArrow(a, FDTypeA("b"))  # a -> b
        self.assertFalse(term.hasType(FDP(), FDGC([]), FDGamma([FDGammaA(a), FDGammaA(FDTypeA("b"))]), type3))
        type4 = FDTypeArrow(a, FDTypeBool())  # a -> bool
        self.assertFalse(term.hasType(FDP(), FDGC([]), FDGamma([FDGammaA(a)]), type4))

    def test_declaration(self):
        term = FDTermDecl(FDTermTrue(), FDTypeBool())
        self.assertTrue(term.hasType(FDP(), FDGC([]), FDGamma([]), FDTypeBool()))
        self.assertFalse(term.hasType(FDP(), FDGC([]), FDGamma([]), FDTypeArrow(FDTypeBool(), FDTypeBool())))

    def test_application(self):
        term = FDTermApp(FDTermAbs("x", FDTermX("x")), FDTermTrue())  # \x.x true
        with self.assertRaises(TypeNotMatchingError):
            term.hasType(FDP(), FDGC([]), FDGamma([]), FDTypeBool())
        term2 = FDTermApp(FDTermDecl(FDTermAbs("x", FDTermX("x")), FDTypeArrow(FDTypeBool(), FDTypeBool())), FDTermTrue())
        self.assertTrue(term2.hasType(FDP(), FDGC([]), FDGamma([]), FDTypeBool()))


class ClassDecls(unittest.TestCase):
    def test_functional_dependency(self):
        a = FDTypeA("a")
        b = FDTypeA("b")
        with self.assertRaises(AssertionError):
            FD([a], [b, a])
        with self.assertRaises(AssertionError):
            FD([], [b, a])
        with self.assertRaises(AssertionError):
            FD([a], [])
        fd1 = FD([a], [b])
        self.assertIsInstance(fd1, FD)
        fd2 = FD([], [])
        self.assertIsInstance(fd2, FD)
        
    def test_class(self):
        a = FDTypeA("a")
        b = FDTypeA("b")
        c = FDTypeA("c")
        tau = FDTypeArrow(a, FDTypeArrow(b, b))
        with self.assertRaises(AssertionError):
            FDCls([], FDTCA("TC1", [a, b]), "m1", tau, FD([c], [a]))
        with self.assertRaises(AssertionError):
            FDCls([], FDTCA("TC1", [a, b]), "m1", tau, FD([a], [c]))
        cls1 = FDCls([], FDTCA("TC1", [a, b]), "m1", tau, FD([a], [b]))
        self.assertIsInstance(cls1, FDCls)
        cls2 = FDCls([], FDTCA("TC2", [a, b]), "m2", tau, FD([], []))
        self.assertIsInstance(cls2, FDCls)

    def test_gc(self):
        a = FDTypeA("a")
        b = FDTypeA("b")
        tau = FDTypeArrow(a, FDTypeArrow(b, b))
        cls = FDCls([], FDTCA("TC1", [a, b]), "m1", tau, FD([a], [b]))
        gc = FDGC([])
        cls.addToGC(FDP(), gc)
        self.assertTrue(len(gc.elements) == 1)
        expectedElement = FDGCElem("m1", [], FDTCA("TC1", [a, b]), tau, FD([a], [b]))
        self.assertTrue(expectedElement.equals(gc.elements[0]))


class ClassInsts(unittest.TestCase):

    def test_same_fd(self):
        a = FDTypeA("a")
        b = FDTypeA("b")
        boolean = FDTypeBool()
        tau = FDTypeArrow(a, FDTypeArrow(b, b))
        cls = FDCls([], FDTCA("TC", [a, b]), "m", tau, FD([a], [b]))
        self.assertIsInstance(cls, FDCls)
        gc = FDGC([])
        cls.addToGC(FDP(), gc)
        m = FDTermAbs("x", FDTermAbs("y", FDTermApp(FDTermX("x"), FDTermX("y"))))
        inst1 = FDInst([], FDTCTau("TC", [FDTypeArrow(boolean, boolean), boolean]), "m", m)
        p = FDP()
        inst1.addToP(p, gc)
        self.assertTrue(len(p.elements) == 1)
        #  exact same instance
        inst2 = FDInst([], FDTCTau("TC", [FDTypeArrow(boolean, boolean), boolean]), "m", m)
        with self.assertRaises(AlreadyExistsError):
            inst2.addToP(p, gc)
        self.assertTrue(len(p.elements) == 1)
        #  instance with same a (bool->bool) but different b
        m2 = FDTermAbs("x", FDTermAbs("y", FDTermX("y")))
        inst3 = FDInst([], FDTCTau("TC", [FDTypeArrow(boolean, boolean), FDTypeArrow(boolean, boolean)]), "m", m2)
        with self.assertRaises(AlreadyExistsError):
            inst3.addToP(p, gc)
        self.assertTrue(len(p.elements) == 1)

    def test_no_fd(self):
        a = FDTypeA("a")
        b = FDTypeA("b")
        boolean = FDTypeBool()
        tau = FDTypeArrow(a, FDTypeArrow(b, b))
        cls = FDCls([], FDTCA("TC", [a, b]), "m", tau, FD([], []))
        self.assertIsInstance(cls, FDCls)
        gc = FDGC([])
        cls.addToGC(FDP(), gc)
        m = FDTermAbs("x", FDTermAbs("y", FDTermApp(FDTermX("x"), FDTermX("y"))))
        inst1 = FDInst([], FDTCTau("TC", [FDTypeArrow(boolean, boolean), boolean]), "m", m)
        p = FDP()
        inst1.addToP(p, gc)
        self.assertTrue(len(p.elements) == 1)
        #  exact same instance
        inst2 = FDInst([], FDTCTau("TC", [FDTypeArrow(boolean, boolean), boolean]), "m", m)
        with self.assertRaises(AssertionError):
            inst2.addToP(p, gc)
        self.assertTrue(len(p.elements) == 1)
        #  instance with same a (bool->bool) but different b
        m2 = FDTermAbs("x", FDTermAbs("y", FDTermX("y")))
        inst3 = FDInst([], FDTCTau("TC", [FDTypeArrow(boolean, boolean), FDTypeArrow(boolean, boolean)]), "m", m2)
        inst3.addToP(p, gc)
        self.assertTrue(len(p.elements) == 2)

    def test_other_tc(self):
        a = FDTypeA("a")
        b = FDTypeA("b")
        boolean = FDTypeBool()
        tau = FDTypeArrow(a, FDTypeArrow(b, b))
        cls1 = FDCls([], FDTCA("TC1", [a, b]), "m1", tau, FD([], []))
        gc = FDGC([])
        cls1.addToGC(FDP(), gc)
        cls2 = FDCls([], FDTCA("TC2", [a, b]), "m2", tau, FD([], []))
        cls2.addToGC(FDP(), gc)
        m = FDTermAbs("x", FDTermAbs("y", FDTermApp(FDTermX("x"), FDTermX("y"))))
        inst1 = FDInst([], FDTCTau("TC1", [FDTypeArrow(boolean, boolean), boolean]), "m1", m)
        p = FDP()
        inst1.addToP(p, gc)
        self.assertTrue(len(p.elements) == 1)
        #  exact same tau for different typeclass
        inst2 = FDInst([], FDTCTau("TC2", [FDTypeArrow(boolean, boolean), boolean]), "m2", m)
        inst2.addToP(p, gc)
        self.assertTrue(len(p.elements) == 2)

    def test_succes(self):
        a = FDTypeA("a")
        b = FDTypeA("b")
        boolean = FDTypeBool()
        tau = FDTypeArrow(a, FDTypeArrow(b, b))
        cls = FDCls([], FDTCA("TC", [a, b]), "m", tau, FD([a], [b]))
        self.assertIsInstance(cls, FDCls)
        gc = FDGC([])
        cls.addToGC(FDP(), gc)
        #  \x.\y. x y
        m = FDTermAbs("x", FDTermAbs("y", FDTermApp(FDTermX("x"), FDTermX("y"))))
        inst1 = FDInst([], FDTCTau("TC", [FDTypeArrow(boolean, boolean), boolean]), "m", m)
        p = FDP()
        inst1.addToP(p, gc)
        self.assertTrue(len(p.elements) == 1)
        #  instance with different a
        #  \x.\y. y
        m2 = FDTermAbs("x", FDTermAbs("y", FDTermX("y")))
        inst2 = FDInst([], FDTCTau("TC", [boolean, FDTypeArrow(boolean, boolean)]), "m", m2)
        inst2.addToP(p, gc)
        self.assertTrue(len(p.elements) == 2)


class Unambiguity(unittest.TestCase):

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
        sigmaNew = sigma.applyFunctionalDependencies(p, gc)
        #  TC bool bool => TC bool bool => bool -> bool
        expectedSigma = FDRhoConstr([FDQ(FDTCTau("TC", [boolean, boolean])), FDQ(FDTCTau("TC", [boolean, boolean]))], FDTypeArrow(boolean, boolean))
        self.assertTrue(sigmaNew.equals(expectedSigma))
        self.assertTrue(sigmaNew.unambiguous(p, gc))
        self.assertTrue(sigma.unambiguous(p, gc))

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
        cNew = c.applyFunctionalDependencies(p, gc)
        #  TC bool bool => TC bool bool => TC bool bool
        expectedC = FDC([], [FDQ(FDTCTau("TC", [boolean, boolean])), FDQ(FDTCTau("TC", [boolean, boolean]))], FDQ(FDTCTau("TC", [boolean, boolean])))
        self.assertTrue(cNew.equals(expectedC))
        self.assertTrue(cNew.unambiguous(p, gc))
        self.assertTrue(c.unambiguous(p, gc))



if __name__ == '__main__':
    unittest.main()
