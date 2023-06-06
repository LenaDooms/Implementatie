import unittest

from SourceLanguageMP.Constraint.TC import MPTCA, MPTCTau
from SourceLanguageMP.Constraint.constraint import MPC, MPQ
from SourceLanguageMP.Environment.Element import MPGammaX, MPPElem, MPGCElem, MPGammaA
from SourceLanguageMP.Environment.environment import MPP, MPGC, MPGamma
from SourceLanguageMP.Programs.program import MPInst, MPCls, MPPgmE, MPPgmInst, MPPgmCls
from SourceLanguageMP.Terms.Term import MPTermTrue, MPTermFalse, MPTermX, MPTermM, MPTermAbs, MPTermDecl, MPTermApp, MPTermLet
from SourceLanguageMP.Types.Rho import MPRhoConstr
from SourceLanguageMP.Types.Sigma import MPSigmaForall
from SourceLanguageMP.Types.Tau import MPTypeBool, MPTypeA, MPTypeSubst, MPTypeArrow
from exceptions import NotFoundError, TypeNotMatchingError


class general(unittest.TestCase):

    def test_fv(self):
        a = MPTypeA("a")
        b = MPTypeA("b")
        sigma = MPSigmaForall([a], MPTypeArrow(a, b))
        self.assertTrue(len(sigma.getFreeVars()) == 1)
        self.assertTrue(b.equals(sigma.getFreeVars()[0]))


class Types(unittest.TestCase):

    def test_true(self):
        true = MPTermTrue()
        boolean = MPTypeBool()
        a = MPTypeA("a")
        self.assertTrue(true.hasType(MPP(), MPGC([]), MPGamma([]), boolean))
        self.assertFalse(true.hasType(MPP(), MPGC([]), MPGamma([]), a))
        self.assertTrue(true.getType(MPP(), MPGC([]), MPGamma([])).equals(boolean))
        self.assertFalse(true.getType(MPP(), MPGC([]), MPGamma([])).equals(a))

    def test_false(self):
        false = MPTermFalse()
        boolean = MPTypeBool()
        a = MPTypeA("a")
        self.assertTrue(false.hasType(MPP(), MPGC([]), MPGamma([]), boolean))
        self.assertFalse(false.hasType(MPP(), MPGC([]), MPGamma([]), a))
        self.assertTrue(false.getType(MPP(), MPGC([]), MPGamma([])).equals(boolean))
        self.assertFalse(false.getType(MPP(), MPGC([]), MPGamma([])).equals(a))

    def test_substitute(self):
        tau = MPTypeA("a")
        with self.assertRaises(AssertionError):
            MPTypeSubst([MPTypeBool(), MPTypeBool()], [MPTypeA("a")], tau)
        tauSubst = MPTypeSubst([MPTypeBool()], [MPTypeA("a")], tau)
        evaluated = tauSubst.evaluate()
        self.assertTrue(evaluated.equals(MPTypeBool()))

    def test_var(self):
        x = MPTermX("x")
        tau = MPTypeA("a")
        tauSubst1 = MPTypeSubst([MPTypeBool()], [MPTypeA("a")], tau)
        sigma1 = MPSigmaForall([MPTypeA("a")], MPRhoConstr([], tau))
        tauSubst2 = MPTypeSubst([MPTypeBool()], [MPTypeA("b")], tau)
        with self.assertRaises(NotFoundError):
            x.hasType(MPP(), MPGC([]), MPGamma([]), tauSubst1)
        self.assertTrue(x.hasType(MPP(), MPGC([]), MPGamma([MPGammaX("x", sigma1)]), tauSubst1))
        self.assertFalse(x.hasType(MPP(), MPGC([]), MPGamma([MPGammaX("x", sigma1)]), tauSubst2))

    def test_let(self):
        term = MPTermLet("x", MPTypeBool(), MPTermTrue(), MPTermX("x"))
        self.assertFalse(term.hasType(MPP(), MPGC([]), MPGamma([]), MPTypeA("a")))
        self.assertTrue(term.hasType(MPP(), MPGC([]), MPGamma([]), MPTypeBool()))

    def test_method_fail_type(self):
        m = MPTermM("m")
        tauFail = MPTypeArrow(MPTypeA("a"), MPTypeA("b"))  # a -> b
        tauSubFail = MPTypeSubst([MPTypeBool(), MPTypeA("c")], [MPTypeA("a"), MPTypeA("b")], tauFail)
        tauSubSubFail = MPTypeSubst([MPTypeBool()], [MPTypeA("c")], tauSubFail)
        tau = MPTypeA("a")  # a
        sigma = MPSigmaForall([], MPRhoConstr([], tau))
        gcElem = MPGCElem("m", [], MPTCA("TC", [MPTypeA("a")]), sigma)
        c = MPC([], [], MPQ(MPTCTau("TC", [MPTypeBool()])))
        pElem = MPPElem(c, "m", MPGamma([]), MPTermTrue())
        p = MPP()
        p.addElement(pElem)
        self.assertFalse(m.hasType(p, MPGC([gcElem]), MPGamma([]), tauSubSubFail))

    def test_method_empty_context(self):
        m = MPTermM("m")
        tau = MPTypeA("a")  # a
        tauSub = MPTypeSubst([MPTypeBool()], [MPTypeA("a")], tau)
        tauSubSub = MPTypeSubst([], [], tauSub)
        with self.assertRaises(NotFoundError):
            m.hasType(MPP(), MPGC([]), MPGamma([]), tauSubSub)

    def test_method(self):
        m = MPTermM("m")
        tau = MPTypeA("a")  # a
        tauSub = MPTypeSubst([MPTypeBool()], [MPTypeA("a")], tau)
        tauSubSub = MPTypeSubst([], [], tauSub)
        sigma = MPSigmaForall([], MPRhoConstr([], tau))
        gcElem = MPGCElem("m", [], MPTCA("TC", [MPTypeA("a")]), sigma)
        c = MPC([], [], MPQ(MPTCTau("TC", [MPTypeBool()])))
        pElem = MPPElem(c, "m", MPGamma([]), MPTermTrue())
        p = MPP()
        p.addElement(pElem)
        self.assertTrue(m.hasType(p, MPGC([gcElem]), MPGamma([]), tauSubSub))

    def test_abstraction(self):
        term = MPTermAbs("x", MPTermX("x"))
        type1 = MPTypeArrow(MPTypeBool(), MPTypeBool())  # bool -> bool
        self.assertTrue(term.hasType(MPP(), MPGC([]), MPGamma([]), type1))
        a = MPTypeA("a")
        type2 = MPTypeArrow(a, a)  # a -> a
        self.assertTrue(term.hasType(MPP(), MPGC([]), MPGamma([MPGammaA(a)]), type2))
        type3 = MPTypeArrow(a, MPTypeA("b"))  # a -> b
        self.assertFalse(term.hasType(MPP(), MPGC([]), MPGamma([MPGammaA(a), MPGammaA(MPTypeA("b"))]), type3))
        type4 = MPTypeArrow(a, MPTypeBool())  # a -> bool
        self.assertFalse(term.hasType(MPP(), MPGC([]), MPGamma([MPGammaA(a)]), type4))

    def test_declaration(self):
        term = MPTermDecl(MPTermTrue(), MPTypeBool())
        self.assertTrue(term.hasType(MPP(), MPGC([]), MPGamma([]), MPTypeBool()))
        self.assertFalse(term.hasType(MPP(), MPGC([]), MPGamma([]), MPTypeArrow(MPTypeBool(), MPTypeBool())))

    def test_application(self):
        term = MPTermApp(MPTermAbs("x", MPTermX("x")), MPTermTrue())  # \x.x true
        with self.assertRaises(TypeNotMatchingError):
            term.hasType(MPP(), MPGC([]), MPGamma([]), MPTypeBool())
        term2 = MPTermApp(MPTermDecl(MPTermAbs("x", MPTermX("x")), MPTypeArrow(MPTypeBool(), MPTypeBool())), MPTermTrue())
        self.assertTrue(term2.hasType(MPP(), MPGC([]), MPGamma([]), MPTypeBool()))


class ClassDecls(unittest.TestCase):
    def test_same_method(self):
        cls = MPCls([], MPTCA("TC", [MPTypeA("a")]), "m", MPTypeA("a"))
        # declaration with same method name
        gcElemSameM = MPGCElem("m", [], MPTCA("TC1", [MPTypeA("a")]), MPTypeBool())
        with self.assertRaises(AssertionError):
            cls.addToGC(MPGC([gcElemSameM]))

    def test_same_typeclass(self):
        cls = MPCls([], MPTCA("TC", [MPTypeA("a")]), "m", MPTypeA("a"))
        # declaration with same typeclass name
        gcElemSameTC = MPGCElem("m1", [], MPTCA("TC", [MPTypeA("a")]), MPTypeBool())
        with self.assertRaises(AssertionError):
            cls.addToGC(MPGC([gcElemSameTC]))

    def test_ambiguous_sigma(self):
        # declaration with ambiguous sigma
        clsAmbiguous = MPCls([], MPTCA("TC", [MPTypeA("a")]), "m", MPTypeBool())
        with self.assertRaises(AssertionError):
            clsAmbiguous.addToGC(MPGC([]))

    def test_success(self):
        cls = MPCls([], MPTCA("TC", [MPTypeA("a")]), "m", MPTypeA("a"))
        # success case
        gc = MPGC([])
        cls.addToGC(gc)
        expectedElement = MPGCElem("m", [], MPTCA("TC", [MPTypeA("a")]), MPTypeA("a"))
        self.assertTrue(len(gc.elements) == 1)
        resultedElement = gc.elements[0]
        self.assertTrue(expectedElement.equals(resultedElement))


class ClassInsts(unittest.TestCase):
    def test_other_method(self):
        gc = MPGC([MPGCElem("m", [], MPTCA("TC", [MPTypeA("a")]), MPTypeA("a"))])  # context with typeclass declaration
        instOtherMethod = MPInst([], MPTCTau("TC", [MPTypeBool()]), "mOther", MPTermTrue())
        # instantiation with a method name not in context
        with self.assertRaises(NotFoundError):
            instOtherMethod.addToP(MPP(), MPGC([]))
        with self.assertRaises(NotFoundError):
            instOtherMethod.addToP(MPP(), gc)

    def test_other_typeclass(self):
        gc = MPGC([MPGCElem("m", [], MPTCA("TC", [MPTypeA("a")]), MPTypeA("a"))])  # context with typeclass declaration
        # instantiation with the typeclass name not matching
        instOtherTypeclass = MPInst([], MPTCTau("TCOther", [MPTypeBool()]), "m", MPTermTrue())
        with self.assertRaises(AssertionError):
            instOtherTypeclass.addToP(MPP(), gc)

    def test_success(self):
        gc = MPGC([MPGCElem("m", [], MPTCA("TC", [MPTypeA("a")]), MPTypeA("a"))])  # context with typeclass declaration
        # success case
        inst = MPInst([], MPTCTau("TC", [MPTypeBool()]), "m", MPTermTrue())
        p = MPP()
        inst.addToP(p, gc)
        expectedElement = MPPElem(MPC([], [], MPQ(MPTCTau("TC", [MPTypeBool()]))), "m", MPGamma([]), MPTermTrue())
        self.assertTrue(len(p.elements) == 1)
        resultingElement = p.elements[0]
        self.assertTrue(expectedElement.equals(resultingElement))


class Programs(unittest.TestCase):

    def test_pgm(self):
        cls = MPCls([], MPTCA("TC", [MPTypeA("a")]), "m", MPTypeA("a"))
        inst = MPInst([], MPTCTau("TC", [MPTypeBool()]), "m", MPTermTrue())
        e = MPTermDecl(MPTermM("m"), MPTypeSubst([], [], MPTypeSubst([MPTypeBool()], [MPTypeA("a")], MPTypeA("a"))))
        pgm = MPPgmCls(cls, MPPgmInst(inst, MPPgmE(e)))
        result = pgm.getType(MPP(), MPGC([]))
        self.assertTrue(MPTypeBool().equals(result))


if __name__ == '__main__':
    unittest.main()
