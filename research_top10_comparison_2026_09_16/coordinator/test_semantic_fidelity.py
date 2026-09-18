"""Coordinator regression tests: exact native FP32 + partial resume."""
import sys, pathlib, tempfile, unittest
import numpy as np
import torch
SEM=pathlib.Path(__file__).resolve().parent.parent/'semantic'
sys.path.insert(0,str(SEM))
import pplx_scorer as s
class Fidelity(unittest.TestCase):
    def test_pool_is_official_fp32_reduction(self):
        h=np.array([[[1e8],[1.0],[-1e8]]],dtype=np.float32);m=np.ones((1,3),dtype=np.int64)
        ht=torch.from_numpy(h);mask=torch.from_numpy(m).unsqueeze(-1).expand(ht.size()).to(ht.dtype)
        expected=((ht*mask).sum(1)/mask.sum(1).clamp(min=1e-9)).numpy()
        np.testing.assert_array_equal(s.masked_mean_pool(h,m),expected)
    def test_int8_matches_official_torch_fp32_boundaries(self):
        t=np.arange(-126,126,dtype=np.float64)+.5
        x=np.arctanh(t/127).astype(np.float32)
        x=np.concatenate([x,np.nextafter(x,np.float32(np.inf)),np.nextafter(x,np.float32(-np.inf))])
        expected=torch.clamp(torch.round(torch.tanh(torch.from_numpy(x))*127),-128,127).numpy().astype(np.int8)
        np.testing.assert_array_equal(s.official_int8(x),expected)
    def test_partial_resume_does_not_mark_missing_rows_done(self):
        h=['a','b','c']; pooled=np.arange(12,dtype=np.float32).reshape(3,4)
        with tempfile.TemporaryDirectory() as t:
            p=pathlib.Path(t)/'partial.npz'
            np.savez(p,hashes=np.array(h),pooled_f32=pooled,complete=np.array([1,0,1],dtype=bool))
            x,have=s.load_checkpoint(p,h,4)
            np.testing.assert_array_equal(have,[True,False,True]);np.testing.assert_array_equal(x,pooled)
            _,have2=s.load_checkpoint(p,['a','changed','c'],4)
            self.assertFalse(have2.any())
    def test_missing_complete_mask_is_not_complete(self):
        with tempfile.TemporaryDirectory() as t:
            p=pathlib.Path(t)/'partial.npz'
            np.savez(p,hashes=np.array(['a']),pooled_f32=np.ones((1,4),np.float32))
            _,have=s.load_checkpoint(p,['a'],4);self.assertFalse(have.any())
if __name__=='__main__':unittest.main(verbosity=2)
