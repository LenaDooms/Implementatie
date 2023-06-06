import unittest

from IntermediateLanguage.Constraint.TC import ITCA, ITCTau
from IntermediateLanguage.Constraint.constraint import IC, IQ
from IntermediateLanguage.Dictionaries.Dictionary import DictionarySigma
from IntermediateLanguage.Environment.Element import IGCElem, IPElem
from IntermediateLanguage.Terms.Term import ITermApp, ITermTrue, ITermM, ITermAbs, ITermX, ITermFalse, ITermESigma, \
    ITermLet
from IntermediateLanguage.Types.Sigma import ITypeBool, ITypeA, ITypeArrow
from SourceLanguageMP.Constraint.TC import MPTCA, MPTCTau
from SourceLanguageMP.Constraint.constraint import MPC, MPQ
from SourceLanguageMP.Environment.Element import MPGammaX, MPPElem, MPGCElem, MPGammaA
from SourceLanguageMP.Environment.environment import MPP, MPGC, MPGamma
from SourceLanguageMP.Programs.program import MPInst, MPCls, MPPgmE, MPPgmInst, MPPgmCls
from SourceLanguageMP.Terms.Term import MPTermTrue, MPTermFalse, MPTermX, MPTermM, MPTermAbs, MPTermDecl, MPTermApp, \
    MPTermLet
from SourceLanguageMP.Types.Rho import MPRhoConstr
from SourceLanguageMP.Types.Sigma import MPSigmaForall
from SourceLanguageMP.Types.Tau import MPTypeBool, MPTypeA, MPTypeSubst, MPTypeArrow


class Terms(unittest.TestCase):

    def test_true(self):
        true = MPTermTrue()
        expectedTerm = ITermTrue()
        self.assertTrue(true.elaborate(MPP(), MPGC([]), MPGamma([])).equals(expectedTerm))

    def test_false(self):
        false = MPTermFalse()
        expectedTerm = ITermFalse()
        self.assertTrue(false.elaborate(MPP(), MPGC([]), MPGamma([])).equals(expectedTerm))

    def test_var(self):
        x = MPTermX("x")
        tau = MPTypeA("a")
        tauSubst = MPTypeSubst([MPTypeBool()], [MPTypeA("a")], tau)
        sigma = MPSigmaForall([MPTypeA("a")], MPRhoConstr([], tau))
        expectedTerm = ITermESigma(ITermX("x"), ITypeBool())
        self.assertEqual(x.elaborate(MPP(), MPGC([]), MPGamma([MPGammaX("x", sigma)])), None)
        self.assertTrue(x.elaborateWithType(MPP(), MPGC([]), MPGamma([MPGammaX("x", sigma)]), tauSubst).equals(expectedTerm))

    def test_let(self):
        term = MPTermLet("x", MPTypeBool(), MPTermTrue(), MPTermX("x"))
        expectedTerm = ITermLet("x", ITypeBool(), ITermTrue(), ITermX("x"))
        self.assertTrue(term.elaborate(MPP(), MPGC([]), MPGamma([])).equals(expectedTerm))

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
        self.assertEqual(m.elaborate(p, MPGC([gcElem]), MPGamma([])), None)
        expectedTerm = ITermM(DictionarySigma(0, [], []), "m")
        self.assertTrue(m.elaborateWithType(p, MPGC([gcElem]), MPGamma([]), tauSubSub).equals(expectedTerm))

    def test_abstraction(self):
        term = MPTermAbs("x", MPTermX("x"))
        type1 = MPTypeArrow(MPTypeBool(), MPTypeBool())  # bool -> bool
        self.assertEqual(term.elaborate(MPP(), MPGC([]), MPGamma([])), None)
        expectedTerm = ITermAbs("x", ITypeBool(), ITermX("x"))
        self.assertTrue(term.elaborateWithType(MPP(), MPGC([]), MPGamma([]), type1).equals(expectedTerm))

        a = MPTypeA("a")
        type2 = MPTypeArrow(a, a)  # a -> a
        expectedTerm2 = ITermAbs("x", ITypeA("a"), ITermX("x"))
        self.assertTrue(term.elaborateWithType(MPP(), MPGC([]), MPGamma([MPGammaA(a)]), type2).equals(expectedTerm2))

    def test_declaration(self):
        term = MPTermDecl(MPTermTrue(), MPTypeBool())
        expectedTerm = ITermTrue()
        self.assertTrue(term.elaborate(MPP(), MPGC([]), MPGamma([])).equals(expectedTerm))
        self.assertTrue(term.elaborateWithType(MPP(), MPGC([]), MPGamma([]), MPTypeBool()).equals(expectedTerm))
        with self.assertRaises(AssertionError):
            self.assertTrue(term.elaborateWithType(MPP(), MPGC([]), MPGamma([]), MPTypeA("a")).equals(expectedTerm))

    def test_application(self):
        term = MPTermApp(MPTermDecl(MPTermAbs("x", MPTermX("x")), MPTypeArrow(MPTypeBool(), MPTypeBool())), MPTermTrue())
        expectedTerm = ITermApp(ITermAbs("x", ITypeBool(), ITermX("x")), ITermTrue())
        self.assertTrue(term.elaborate(MPP(), MPGC([]), MPGamma([])).equals(expectedTerm))


class Context(unittest.TestCase):

    def test_gc(self):
        a = MPTypeA("a")
        b = MPTypeA("b")
        gc = MPGC([MPGCElem("m", [], MPTCA("TC", [a, b]), MPTypeArrow(a, b))])  # context with typeclass declaration
        igc = gc.elaborate()
        self.assertTrue(len(igc.elements) == 1)
        expectedElement = IGCElem("m", ITCA("TC", ITypeA("a")), ITypeA("a"))
        self.assertTrue(expectedElement.equals(igc.elements[0]))

    def test_p(self):
        a = MPTypeA("a")
        b = MPTypeA("b")
        boolean = MPTypeBool()
        m = MPTermAbs("x", MPTermAbs("y", MPTermApp(MPTermX("x"), MPTermX("y"))))
        cls = MPCls([], MPTCA("TC", [a, b]), "m", MPTypeArrow(a, MPTypeArrow(b, b)))
        gc = MPGC([])
        cls.addToGC(gc)
        inst = MPInst([], MPTCTau("TC", [MPTypeArrow(boolean, boolean), boolean]), "m", m)
        p = MPP()
        inst.addToP(p, gc)
        pNew = p.elaborate(gc)
        self.assertTrue(len(pNew.elements) == 1)
        mNew = ITermAbs("x", ITypeArrow(ITypeBool(), ITypeBool()), ITermAbs("y", ITypeBool(), ITermApp(ITermX("x"), ITermX("y"))))
        newTau = ITypeArrow(ITypeArrow(ITypeBool(), ITypeBool()), ITypeArrow(ITypeBool(), ITypeBool()))
        expectedElement = IPElem(IC([], [], IQ(ITCTau("TC", newTau))), "m", mNew)
        self.assertTrue(expectedElement.equals(pNew.elements[0]))


class Elaborate(unittest.TestCase):

    def test_elaborate(self):
        a = MPTypeA("a")
        b = MPTypeA("b")
        boolean = MPTypeBool()
        m = MPTermAbs("x", MPTermAbs("y", MPTermApp(MPTermX("x"), MPTermX("y"))))
        cls = MPCls([], MPTCA("TC", [a, b]), "m", MPTypeArrow(a, MPTypeArrow(b, b)))
        inst = MPInst([], MPTCTau("TC", [MPTypeArrow(boolean, boolean), boolean]), "m", m)
        #  e = (\x.\y. x y) :: [bool->bool, bool]/[a, b] (a->b->b)
        e = MPTermDecl(MPTermM("m"), MPTypeSubst([], [], MPTypeSubst([MPTypeArrow(boolean, boolean), boolean], [a, b],
                                                                     MPTypeArrow(a, MPTypeArrow(b, b)))))
        #  e2 = ((\x.\y. x y) :: [bool->bool, bool]/[a, b] (a->b->b)) ((\x. x) :: bool->bool)
        e2 = MPTermApp(e, MPTermDecl(MPTermAbs("x", MPTermX("x")), MPTypeArrow(boolean, boolean)))
        #  e3 = (((\x.\y. x y) :: [bool->bool, bool]/[a, b] (a->b->b)) ((\x. x) :: bool->bool)) true
        e3 = MPTermApp(e2, MPTermTrue())
        pgm = MPPgmCls(cls, MPPgmInst(inst, MPPgmE(e3)))
        result = pgm.elaborate(MPP(), MPGC([]))
        im = ITermM(DictionarySigma(0, [], []), "m")
        abstraction = ITermAbs("x", ITypeBool(), ITermX("x"))
        expectedTerm = ITermApp(ITermApp(im, abstraction), ITermTrue())
        self.assertTrue(result.equals(expectedTerm))

    def test_pgm(self):
        a = MPTypeA("a")
        b = MPTypeA("b")
        boolean = MPTypeBool()
        m1 = MPTermAbs("x", MPTermX("x"))
        cls1 = MPCls([], MPTCA("Convert", [a, b]), "convert", MPTypeArrow(a, b))
        inst1 = MPInst([], MPTCTau("Convert", [boolean, boolean]), "convert", m1)
        m2 = MPTermAbs("x", MPTermAbs("y", MPTermX("y")))
        sigma = MPSigmaForall([a], MPRhoConstr([MPQ(MPTCA("Convert", [a, b]))], MPTypeArrow(a, MPTypeArrow(b, b))))
        typeSub = MPTypeSubst([boolean], [a], MPTypeSubst([boolean], [b], MPTypeArrow(a, MPTypeArrow(b, b))))
        cls2 = MPCls([], MPTCA("Add", [b]), "add", sigma)
        inst2 = MPInst([], MPTCTau("Add", [boolean]), "add", m2)
        pgmE = MPPgmE(MPTermApp(MPTermApp(MPTermDecl(MPTermM("add"), typeSub), MPTermTrue()), MPTermFalse()))
        pgm = MPPgmCls(cls1, MPPgmCls(cls2, MPPgmInst(inst1, MPPgmInst(inst2, pgmE))))
        result = pgm.getType(MPP(), MPGC([]))
        self.assertTrue(result.equals(boolean))
        elaboration = pgm.elaborate(MPP(), MPGC([]))
        elaboration.show()




if __name__ == '__main__':
    unittest.main()
