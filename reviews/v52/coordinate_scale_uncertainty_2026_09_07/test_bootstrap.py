"""Pure synthetic tests; never load real rows or invoke main."""
import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('boot',Path(__file__).with_name('bootstrap.py'))
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
np=b.np

class Tests(unittest.TestCase):
    def means(self):
        return np.tile(np.array([1.,1.,.5,.75,.75,.875]),(1,10,1))

    def test_point(self):
        st,_,_=b.statistics(self.means())
        np.testing.assert_allclose(st,[[.5,.5,0,.5,.5,0]])

    def test_one_zero_seed(self):
        x=self.means();x[0,0,2]=1
        st,_,_=b.statistics(x)
        self.assertTrue(np.isnan(st[0,0]) and np.isnan(st[0,2]))
        self.assertTrue(np.isfinite(st[0,3]))

    def test_zero_aggregate(self):
        x=self.means();x[0,:5,2]=.5;x[0,5:,2]=1.5
        st,_,_=b.statistics(x)
        self.assertTrue(np.isfinite(st[0,0]) and np.isnan(st[0,3]) and np.isnan(st[0,5]))

    def test_no_clipping(self):
        x=self.means();x[:,:,2]=1.5;x[:,:,3]=.5
        st,den,_=b.statistics(x)
        self.assertEqual(st[0,0],2)
        self.assertTrue((den[:,:,0]<0).all())

    def test_noncommutation(self):
        x=self.means();x[0,:5,2]=.9;x[0,:5,3]=1
        st,_,_=b.statistics(x)
        self.assertNotAlmostEqual(st[0,0],st[0,3])

    def test_weights_and_cluster_concatenation(self):
        x=np.arange(4*60,dtype=float).reshape(4,60)/240
        w=np.array([2,0,1,1])
        np.testing.assert_allclose(w@x/w.sum(),x[[0,0,2,3]].mean(axis=0))
        np.testing.assert_allclose((3*w)@x/(3*w).sum(),w@x/w.sum())
        # cluster0 has one row, cluster1 has three; draw cluster1 twice.
        sums=np.array([x[0],x[1:].sum(axis=0)])
        counts=np.array([0,2]);sizes=np.array([1,3])
        np.testing.assert_allclose(counts@sums/(counts@sizes),x[[1,2,3,1,2,3]].mean(axis=0))

    def test_rng_repeat_pairing(self):
        old=b.B;b.B=16
        try:
            x=np.tile(self.means(),(4,1,1))
            a=b.resample(x,None,7);c=b.resample(x,None,7)
            for i in range(3): np.testing.assert_array_equal(a[i],c[i])
            np.testing.assert_allclose(a[0][:,[0,1,3,4]],.5)
            cluster=b.resample(x,np.array([0,1,1,1]),7)
            np.testing.assert_allclose(cluster[0][:,[0,1,3,4]],.5)
        finally:
            b.B=old

    def test_finite_accounting(self):
        x=self.means();x[0,0,2]=1
        st,d,ad=b.statistics(x);out=b.summaries(st,d,ad)
        for ent in out['statistics'].values():
            self.assertEqual(ent['finite']+ent['undefined'],1)
        self.assertEqual(out['statistics']['A_I']['undefined'],1)

    def test_production_cluster_weighting_nonconstant(self):
        old=b.B;b.B=16
        try:
            x=np.tile(self.means(),(4,1,1))
            x[:, :, 3]+=np.arange(4)[:,None]*.025
            labels=np.array([0,1,1,1])
            actual=b.resample(x,labels,91)[0]
            counts=np.random.Generator(np.random.PCG64(91)).multinomial(2,[.5,.5],size=16)
            expected=[]
            for row in counts:
                selected=[0]*int(row[0])+[1,2,3]*int(row[1])
                expected.append(b.statistics(x[selected].mean(axis=0)[None,:,:])[0][0])
            np.testing.assert_allclose(actual,np.array(expected),atol=1e-12)
        finally:
            b.B=old

if __name__=='__main__':unittest.main()
