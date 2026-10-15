"""Regression tests for Engine/Inc/UnObj.h port."""
import sys
sys.path.insert(0, "/home/dclavijo/my_code/Ut99py")
from ut99py.engine import EBspNodeFlags, FBspNode, FPoly, EPolyFlags

def test_bsp_node_flags():
    assert EBspNodeFlags.NF_NotCsg == 0x01
    assert EBspNodeFlags.NF_IsBack == 0x80

class FakeFVector:
    def __sub__(self, other): return self
    __or__ = lambda s, o: 0.0
def test_fpoly():
    p = FPoly()
    p.base = type('V',(),{'__sub__':lambda s,o:s})()

def test_bsp_node():
    n = FBspNode()
    assert n.is_csg() is False  # num_vertices==0
    assert n.MAX_NODE_VERTICES == 16

if __name__ == "__main__":
    test_bsp_node_flags()
    test_bsp_node()
    print("UnObj tests passed.")
