import taichi as ti
import numpy as np

ti.init(arch=ti.cuda)


def test_thread_idx():
    x = ti.field(ti.i32, shape=(256))

    @ti.kernel
    def func():
        for i in range(32):
            for j in range(8):
                t = ti.global_thread_idx()
                x[t] += 1

    func()
    assert x.to_numpy().sum() == 256

# @ti.test(arch=ti.cuda)
def test_global_thread_idx():
    n = 2048 # Make sure that threads are located in multiple blocks (CUDA: Maximum number of threads per block = 1024)
             # `n` should not be too large that exceeds the maximum number of global threads configured by Taichi
    x = ti.field(ti.i32, shape=(n))

    @ti.kernel
    def func():
        for i in range(n):
            tid = ti.global_thread_idx()
            x[tid] = tid
    
    func()
    assert np.arange(n).sum() == x.to_numpy().sum()

    for i in range(n):
        print(x[i])

test_global_thread_idx()
test_thread_idx()
