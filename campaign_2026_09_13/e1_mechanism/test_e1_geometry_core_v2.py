import unittest
import numpy as np
import e1_geometry_core_v2 as e1


class GeometryV2Tests(unittest.TestCase):
    def test_redundant_high_variance_block_has_positive_gaps(self):
        rng=np.random.default_rng(1)
        n=1000
        z=rng.normal(size=(n,4))
        C=np.zeros((n,96),dtype=np.float64)
        for j in range(32):
            C[:,j]=4.0*z[:,j%4]+0.05*rng.normal(size=n)
        C[:,32:64]=rng.normal(scale=1.5,size=(n,32))
        C[:,64:96]=rng.normal(scale=0.5,size=(n,32))
        g=e1.archive_geometry_v2(C)
        self.assertGreater(g['PHI_GAP'],0.0)
        self.assertGreater(g['EFFDIM_GAP'],0.0)

    def test_shapes_and_query_zero_case(self):
        with self.assertRaises(ValueError):
            e1.archive_geometry_v2(np.zeros((10,95)))
        q=e1.query_geometry(np.zeros(96))
        self.assertIsNone(q['Q_ABS_CV'])
        self.assertIsNone(q['Q_EFF'])


if __name__=='__main__':
    unittest.main()
