import unittest

from SourceLanguageMP.Constraint.TC import MPTCA, MPTCTau
from SourceLanguageMP.Environment.environment import MPP, MPGC
from SourceLanguageMP.Programs.program import MPInst, MPCls, MPPgmE, MPPgmInst, MPPgmCls
from SourceLanguageMP.Terms.Term import MPTermTrue, MPTermX, MPTermM, MPTermAbs, MPTermDecl, MPTermApp
from SourceLanguageMP.Types.Tau import MPTypeBool, MPTypeA, MPTypeSubst, MPTypeArrow


class Programs(unittest.TestCase):

    def test_pgm(self):
        a = MPTypeA("a")
        b = MPTypeA("b")
        boolean = MPTypeBool()
        m = MPTermAbs("x", MPTermAbs("y", MPTermApp(MPTermX("x"), MPTermX("y"))))
        cls = MPCls([], MPTCA("TC", [a, b]), "m", MPTypeArrow(a, MPTypeArrow(b, b)))
        inst = MPInst([], MPTCTau("TC", [MPTypeArrow(boolean, boolean), boolean]), "m", m)
        #  e = (\x.\y. x y) :: [bool->bool, bool]/[a, b] (a->b->b)
        e = MPTermDecl(MPTermM("m"), MPTypeSubst([], [], MPTypeSubst([MPTypeArrow(boolean, boolean), boolean], [a, b],
                                                                     MPTypeArrow(a, MPTypeArrow(b, b)))))
        pgm = MPPgmCls(cls, MPPgmInst(inst, MPPgmE(e)))
        result = pgm.getType(MPP(), MPGC([]))
        self.assertTrue(MPTypeArrow(MPTypeArrow(boolean, boolean), MPTypeArrow(boolean, boolean)).equals(result))
        #  e2 = ((\x.\y. x y) :: [bool->bool, bool]/[a, b] (a->b->b)) ((\x. x) :: bool->bool)
        e2 = MPTermApp(e, MPTermDecl(MPTermAbs("x", MPTermX("x")), MPTypeArrow(boolean, boolean)))
        pgm2 = MPPgmCls(cls, MPPgmInst(inst, MPPgmE(e2)))
        result2 = pgm2.getType(MPP(), MPGC([]))
        self.assertTrue(MPTypeArrow(boolean, boolean).equals(result2))
        #  e3 = (((\x.\y. x y) :: [bool->bool, bool]/[a, b] (a->b->b)) ((\x. x) :: bool->bool)) true
        e3 = MPTermApp(e2, MPTermTrue())
        pgm3 = MPPgmCls(cls, MPPgmInst(inst, MPPgmE(e3)))
        result3 = pgm3.getType(MPP(), MPGC([]))
        self.assertTrue(boolean.equals(result3))


if __name__ == '__main__':
    unittest.main()
