import unittest

from IntermediateLanguage.Dictionaries.Dictionary import DictionarySigma
from IntermediateLanguage.Terms.Term import ITermTrue, ITermFalse, ITermX, ITermESigma, ITermLet, ITermM, ITermAbs, \
    ITermApp
from IntermediateLanguage.Types.Sigma import ITypeA, ITypeBool
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


class Terms(unittest.TestCase):

    def test_true(self):
        true = TermTrue()
        expectedTerm = ITermTrue()
        self.assertTrue(expectedTerm.equals(true.elaborate(P(), GC([]), Gamma([]))))
        self.assertFalse(ITermFalse().equals(true.elaborate(P(), GC([]), Gamma([]))))

    def test_false(self):
        false = TermFalse()
        expectedTerm = ITermFalse()
        self.assertTrue(expectedTerm.equals(false.elaborate(P(), GC([]), Gamma([]))))
        self.assertFalse(ITermTrue().equals(false.elaborate(P(), GC([]), Gamma([]))))

    def test_var(self):
        x = TermX("x")
        tau = TypeA("a")
        tauSubst = TypeSubst([TypeBool()], [TypeA("a")], tau)
        sigma = SigmaForall([TypeA("a")], RhoConstr([], tau))
        expectedTerm = ITermESigma(ITermX("x"), ITypeBool())
        self.assertEqual(x.elaborate(P(), GC([]), Gamma([GammaX("x", sigma)])), None)
        self.assertTrue(x.elaborateWithType(P(), GC([]), Gamma([GammaX("x", sigma)]), tauSubst).equals(expectedTerm))

    def test_let(self):
        term = TermLet("x", TypeBool(), TermTrue(), TermX("x"))
        expectedTerm = ITermLet("x", ITypeBool(), ITermTrue(), ITermX("x"))
        self.assertTrue(term.elaborate(P(), GC([]), Gamma([])).equals(expectedTerm))

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
        self.assertEqual(m.elaborate(p, GC([gcElem]), Gamma([])), None)
        expectedTerm = ITermM(DictionarySigma(0, [], []), "m")
        self.assertTrue(m.elaborateWithType(p, GC([gcElem]), Gamma([]), tauSubSub).equals(expectedTerm))

    def test_abstraction(self):
        term = TermAbs("x", TermX("x"))
        type1 = TypeArrow(TypeBool(), TypeBool())  # bool -> bool
        self.assertEqual(term.elaborate(P(), GC([]), Gamma([])), None)
        expectedTerm = ITermAbs("x", ITypeBool(), ITermX("x"))
        self.assertTrue(term.elaborateWithType(P(), GC([]), Gamma([]), type1).equals(expectedTerm))

        a = TypeA("a")
        type2 = TypeArrow(a, a)  # a -> a
        expectedTerm2 = ITermAbs("x", ITypeA("a"), ITermX("x"))
        self.assertTrue(term.elaborateWithType(P(), GC([]), Gamma([GammaA(a)]), type2).equals(expectedTerm2))

    def test_declaration(self):
        term = TermDecl(TermTrue(), TypeBool())
        expectedTerm = ITermTrue()
        self.assertTrue(term.elaborate(P(), GC([]), Gamma([])).equals(expectedTerm))
        self.assertTrue(term.elaborateWithType(P(), GC([]), Gamma([]), TypeBool()).equals(expectedTerm))
        with self.assertRaises(AssertionError):
            self.assertTrue(term.elaborateWithType(P(), GC([]), Gamma([]), TypeA("a")).equals(expectedTerm))

    def test_application(self):
        term = TermApp(TermDecl(TermAbs("x", TermX("x")), TypeArrow(TypeBool(), TypeBool())), TermTrue())
        expectedTerm = ITermApp(ITermAbs("x", ITypeBool(), ITermX("x")), ITermTrue())
        self.assertTrue(term.elaborate(P(), GC([]), Gamma([])).equals(expectedTerm))


class Programs(unittest.TestCase):

    def test_pgm(self):
        cls = Cls([], TcA("TC", TypeA("a")), "m", TypeA("a"))
        inst = Inst([], TcTau("TC", TypeBool()), "m", TermTrue())
        e = TermDecl(TermM("m"), TypeSubst([], [], TypeSubst([TypeBool()], [TypeA("a")], TypeA("a"))))
        pgm = PgmCls(cls, PgmInst(inst, PgmE(e)))
        expectedTerm = ITermM(DictionarySigma(0, [], []), "m")
        self.assertTrue(pgm.elaborate(P(), GC([])).equals(expectedTerm))


if __name__ == '__main__':
    unittest.main()
