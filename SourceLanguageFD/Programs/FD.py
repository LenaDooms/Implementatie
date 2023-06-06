from typing import List
from SourceLanguageFD.Types.Tau import FDTypeA


class FD:
    aList1 = []
    aList2 = []

    def __init__(self, aList1: List[FDTypeA], aList2: List[FDTypeA]):
        #  check that no variables are on both left and right side
        assert all(not any(a1.equals(a2) for a2 in aList2) for a1 in aList1)
        #  no functional dependencies with one empty side
        assert (len(aList1) == 0 and len(aList2) == 0) or (len(aList1) != 0 and len(aList2) != 0)
        self.aList1 = aList1
        self.aList2 = aList2

    def equals(self, fd):
        return (isinstance(fd, FD)
                and len(self.aList1) == len(fd.aList1)
                and len(self.aList2) == len(fd.aList2)
                and all(any(a1.equals(a2) for a2 in fd.aList1) for a1 in self.aList1)
                and all(any(a1.equals(a2) for a2 in fd.aList2) for a1 in self.aList2))
