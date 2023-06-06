import unittest

from SourceLanguage.Constraint.TC import TcA, TcTau
from SourceLanguage.Constraint.constraint import C, Q
from SourceLanguage.Environment.Element import GammaX, PElem, GCElem, GammaA
from SourceLanguage.Environment.environment import P, GC, Gamma
from SourceLanguage.Programs.program import Inst, Cls, PgmE, PgmInst, PgmCls
from SourceLanguage.Terms.Term import TermTrue, TermFalse, TermX, TermM, TermAbs, TermDecl, TermApp, TermLet
from SourceLanguage.Types.Rho import RhoConstr
from SourceLanguage.Types.Sigma import SigmaForall
from SourceLanguage.Types.Tau import TypeBool, TypeA, TypeSubst, TypeArrow
from exceptions import NotFoundError, TypeNotMatchingError


class general(unittest.TestCase):

    def test_fv(self):
        a = TypeA("a")
        b = TypeA("b")
        sigma = SigmaForall([a], TypeArrow(a, b))
        self.assertTrue(len(sigma.getFreeVars()) == 1)
        self.assertTrue(b.equals(sigma.getFreeVars()[0]))


class Types(unittest.TestCase):

    def test_true(self):
        true = TermTrue()
        boolean = TypeBool()
        a = TypeA("a")
        self.assertTrue(true.hasType(P(), GC([]), Gamma([]), boolean))
        self.assertFalse(true.hasType(P(), GC([]), Gamma([]), a))
        self.assertTrue(true.getType(P(), GC([]), Gamma([])).equals(boolean))
        self.assertFalse(true.getType(P(), GC([]), Gamma([])).equals(a))

    def test_false(self):
        false = TermFalse()
        boolean = TypeBool()
        a = TypeA("a")
        self.assertTrue(false.hasType(P(), GC([]), Gamma([]), boolean))
        self.assertFalse(false.hasType(P(), GC([]), Gamma([]), a))
        self.assertTrue(false.getType(P(), GC([]), Gamma([])).equals(boolean))
        self.assertFalse(false.getType(P(), GC([]), Gamma([])).equals(a))

    def test_substitute(self):
        tau = TypeA("a")
        with self.assertRaises(AssertionError):
            TypeSubst([TypeBool(), TypeBool()], [TypeA("a")], tau)
        tauSubst = TypeSubst([TypeBool()], [TypeA("a")], tau)
        evaluated = tauSubst.evaluate()
        self.assertTrue(evaluated.equals(TypeBool()))

    def test_var(self):
        x = TermX("x")
        tau = TypeA("a")
        tauSubst1 = TypeSubst([TypeBool()], [TypeA("a")], tau)
        sigma1 = SigmaForall([TypeA("a")], RhoConstr([], tau))
        tauSubst2 = TypeSubst([TypeBool()], [TypeA("b")], tau)
        with self.assertRaises(NotFoundError):
            x.hasType(P(), GC([]), Gamma([]), tauSubst1)
        self.assertTrue(x.hasType(P(), GC([]), Gamma([GammaX("x", sigma1)]), tauSubst1))
        self.assertFalse(x.hasType(P(), GC([]), Gamma([GammaX("x", sigma1)]), tauSubst2))

    def test_let(self):
        term = TermLet("x", TypeBool(), TermTrue(), TermX("x"))
        self.assertFalse(term.hasType(P(), GC([]), Gamma([]), TypeA("a")))
        self.assertTrue(term.hasType(P(), GC([]), Gamma([]), TypeBool()))

    def test_method_fail_type(self):
        m = TermM("m")
        tauFail = TypeArrow(TypeA("a"), TypeA("b"))  # a -> b
        tauSubFail = TypeSubst([TypeBool(), TypeA("c")], [TypeA("a"), TypeA("b")], tauFail)
        tauSubSubFail = TypeSubst([TypeBool()], [TypeA("c")], tauSubFail)
        tau = TypeA("a")  # a
        sigma = SigmaForall([], RhoConstr([], tau))
        gcElem = GCElem("m", [], TcA("TC", TypeA("a")), sigma)
        c = C([], [], Q(TcTau("TC", TypeBool())))
        pElem = PElem(c, "m", Gamma([]), TermTrue())
        p = P()
        p.addElement(pElem)
        self.assertFalse(m.hasType(p, GC([gcElem]), Gamma([]), tauSubSubFail))

    def test_method_empty_context(self):
        m = TermM("m")
        tau = TypeA("a")  # a
        tauSub = TypeSubst([TypeBool()], [TypeA("a")], tau)
        tauSubSub = TypeSubst([], [], tauSub)
        with self.assertRaises(NotFoundError):
            m.hasType(P(), GC([]), Gamma([]), tauSubSub)

    def test_method(self):
        m = TermM("m")
        tau = TypeA("a")  # a
        tauSub = TypeSubst([TypeBool()], [TypeA("a")], tau)
        tauSubSub = TypeSubst([], [], tauSub)
        sigma = SigmaForall([], RhoConstr([], tau))
        gcElem = GCElem("m", [], TcA("TC", TypeA("a")), sigma)
        c = C([], [], Q(TcTau("TC", TypeBool())))
        pElem = PElem(c, "m", Gamma([]), TermTrue())
        p = P()
        p.addElement(pElem)
        self.assertTrue(m.hasType(p, GC([gcElem]), Gamma([]), tauSubSub))

    def test_abstraction(self):
        term = TermAbs("x", TermX("x"))
        type1 = TypeArrow(TypeBool(), TypeBool())  # bool -> bool
        self.assertTrue(term.hasType(P(), GC([]), Gamma([]), type1))
        a = TypeA("a")
        type2 = TypeArrow(a, a)  # a -> a
        self.assertTrue(term.hasType(P(), GC([]), Gamma([GammaA(a)]), type2))
        type3 = TypeArrow(a, TypeA("b"))  # a -> b
        self.assertFalse(term.hasType(P(), GC([]), Gamma([GammaA(a), GammaA(TypeA("b"))]), type3))
        type4 = TypeArrow(a, TypeBool())  # a -> bool
        self.assertFalse(term.hasType(P(), GC([]), Gamma([GammaA(a)]), type4))

    def test_declaration(self):
        term = TermDecl(TermTrue(), TypeBool())
        self.assertTrue(term.hasType(P(), GC([]), Gamma([]), TypeBool()))
        self.assertFalse(term.hasType(P(), GC([]), Gamma([]), TypeArrow(TypeBool(), TypeBool())))

    def test_application(self):
        term = TermApp(TermAbs("x", TermX("x")), TermTrue())  # \x.x true
        with self.assertRaises(TypeNotMatchingError):
            term.hasType(P(), GC([]), Gamma([]), TypeBool())
        term2 = TermApp(TermDecl(TermAbs("x", TermX("x")), TypeArrow(TypeBool(), TypeBool())), TermTrue())
        self.assertTrue(term2.hasType(P(), GC([]), Gamma([]), TypeBool()))


class ClassDecls(unittest.TestCase):
    def test_same_method(self):
        cls = Cls([], TcA("TC", TypeA("a")), "m", TypeA("a"))
        # declaration with same method name
        gcElemSameM = GCElem("m", [], TcA("TC1", TypeA("a")), TypeBool())
        with self.assertRaises(AssertionError):
            cls.addToGC(GC([gcElemSameM]))

    def test_same_typeclass(self):
        cls = Cls([], TcA("TC", TypeA("a")), "m", TypeA("a"))
        # declaration with same typeclass name
        gcElemSameTC = GCElem("m1", [], TcA("TC", TypeA("a")), TypeBool())
        with self.assertRaises(AssertionError):
            cls.addToGC(GC([gcElemSameTC]))

    def test_ambiguous_sigma(self):
        # declaration with ambiguous sigma
        clsAmbiguous = Cls([], TcA("TC", TypeA("a")), "m", TypeBool())
        with self.assertRaises(AssertionError):
            clsAmbiguous.addToGC(GC([]))

    def test_success(self):
        cls = Cls([], TcA("TC", TypeA("a")), "m", TypeA("a"))
        # success case
        gc = GC([])
        cls.addToGC(gc)
        expectedElement = GCElem("m", [], TcA("TC", TypeA("a")), TypeA("a"))
        self.assertTrue(len(gc.elements) == 1)
        resultedElement = gc.elements[0]
        self.assertTrue(expectedElement.equals(resultedElement))


class ClassInsts(unittest.TestCase):
    def test_other_method(self):
        gc = GC([GCElem("m", [], TcA("TC", TypeA("a")), TypeA("a"))])  # context with typeclass declaration
        instOtherMethod = Inst([], TcTau("TC", TypeBool()), "mOther", TermTrue())
        # instantiation with a method name not in context
        with self.assertRaises(NotFoundError):
            instOtherMethod.addToP(P(), GC([]))
        with self.assertRaises(NotFoundError):
            instOtherMethod.addToP(P(), gc)

    def test_other_typeclass(self):
        gc = GC([GCElem("m", [], TcA("TC", TypeA("a")), TypeA("a"))])  # context with typeclass declaration
        # instantiation with the typeclass name not matching
        instOtherTypeclass = Inst([], TcTau("TCOther", TypeBool()), "m", TermTrue())
        with self.assertRaises(AssertionError):
            instOtherTypeclass.addToP(P(), gc)

    def test_success(self):
        gc = GC([GCElem("m", [], TcA("TC", TypeA("a")), TypeA("a"))])  # context with typeclass declaration
        # success case
        inst = Inst([], TcTau("TC", TypeBool()), "m", TermTrue())
        p = P()
        inst.addToP(p, gc)
        expectedElement = PElem(C([], [], Q(TcTau("TC", TypeBool()))), "m", Gamma([]), TermTrue())
        self.assertTrue(len(p.elements) == 1)
        resultingElement = p.elements[0]
        self.assertTrue(expectedElement.equals(resultingElement))


class Programs(unittest.TestCase):

    def test_pgm(self):
        cls = Cls([], TcA("TC", TypeA("a")), "m", TypeA("a"))
        inst = Inst([], TcTau("TC", TypeBool()), "m", TermTrue())
        e = TermDecl(TermM("m"), TypeSubst([], [], TypeSubst([TypeBool()], [TypeA("a")], TypeA("a"))))
        pgm = PgmCls(cls, PgmInst(inst, PgmE(e)))
        result = pgm.getType(P(), GC([]))
        self.assertTrue(TypeBool().equals(result))


if __name__ == '__main__':
    unittest.main()
