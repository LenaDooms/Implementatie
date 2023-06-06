from copy import deepcopy

from SourceLanguage.Environment.Element import GammaX
from SourceLanguage.Environment.environment import Gamma
from SourceLanguage.Types.Tau import TypeBool

x1 = GammaX("x1", TypeBool())
x2 = GammaX("x2", TypeBool())
x3 = GammaX("x3", TypeBool())
gamma = Gamma([])
gamma.addElements([x1, x2, x3])
x4 = GammaX("x1", TypeBool())
print(x4 in gamma.elements)
print(gamma.contains(x4))
gamma.show()
print()
gammaNew = Gamma(deepcopy(gamma.elements[0:2]))
gammaNew.show()

