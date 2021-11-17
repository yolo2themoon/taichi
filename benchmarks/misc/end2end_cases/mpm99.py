import numpy as np

import taichi as ti

# copy from examples/simulation/mpm99.py

def e2e_mpm99(test_arch):
    ti.init(kernel_profiler=True, arch=test_arch)

    quality = 1  # Use a larger value for higher-res simulations
    n_particles, n_grid = 9000 * quality**2, 128 * quality
    dx, inv_dx = 1 / n_grid, float(n_grid)
    dt = 1e-4 / quality
    p_vol, p_rho = (dx * 0.5)**2, 1
    p_mass = p_vol * p_rho
    E, nu = 0.1e4, 0.2  # Young's modulus and Poisson's ratio
    mu_0, lambda_0 = E / (2 * (1 + nu)), E * nu / (
        (1 + nu) * (1 - 2 * nu))  # Lame parameters
    x = ti.Vector.field(2, dtype=float, shape=n_particles)  # position
    v = ti.Vector.field(2, dtype=float, shape=n_particles)  # velocity
    C = ti.Matrix.field(2, 2, dtype=float,
                        shape=n_particles)  # affine velocity field
    F = ti.Matrix.field(2, 2, dtype=float,
                        shape=n_particles)  # deformation gradient
    material = ti.field(dtype=int, shape=n_particles)  # material id
    Jp = ti.field(dtype=float, shape=n_particles)  # plastic deformation
    grid_v = ti.Vector.field(2, dtype=float,
                            shape=(n_grid, n_grid))  # grid node momentum/velocity
    grid_m = ti.field(dtype=float, shape=(n_grid, n_grid))  # grid node mass


    @ti.kernel
    def substep():
        for i, j in grid_m:
            grid_v[i, j] = [0, 0]
            grid_m[i, j] = 0
        for p in x:  # Particle state update and scatter to grid (P2G)
            base = (x[p] * inv_dx - 0.5).cast(int)
            fx = x[p] * inv_dx - base.cast(float)
            # Quadratic kernels  [http://mpm.graphics   Eqn. 123, with x=fx, fx-1,fx-2]
            w = [0.5 * (1.5 - fx)**2, 0.75 - (fx - 1)**2, 0.5 * (fx - 0.5)**2]
            F[p] = (ti.Matrix.identity(float, 2) +
                    dt * C[p]) @ F[p]  # deformation gradient update
            h = ti.exp(
                10 *
                (1.0 -
                Jp[p]))  # Hardening coefficient: snow gets harder when compressed
            if material[p] == 1:  # jelly, make it softer
                h = 0.3
            mu, la = mu_0 * h, lambda_0 * h
            if material[p] == 0:  # liquid
                mu = 0.0
            U, sig, V = ti.svd(F[p])
            J = 1.0
            for d in ti.static(range(2)):
                new_sig = sig[d, d]
                if material[p] == 2:  # Snow
                    new_sig = min(max(sig[d, d], 1 - 2.5e-2),
                                1 + 4.5e-3)  # Plasticity
                Jp[p] *= sig[d, d] / new_sig
                sig[d, d] = new_sig
                J *= new_sig
            if material[
                    p] == 0:  # Reset deformation gradient to avoid numerical instability
                F[p] = ti.Matrix.identity(float, 2) * ti.sqrt(J)
            elif material[p] == 2:
                F[p] = U @ sig @ V.transpose(
                )  # Reconstruct elastic deformation gradient after plasticity
            stress = 2 * mu * (F[p] - U @ V.transpose()) @ F[p].transpose(
            ) + ti.Matrix.identity(float, 2) * la * J * (J - 1)
            stress = (-dt * p_vol * 4 * inv_dx * inv_dx) * stress
            affine = stress + p_mass * C[p]
            for i, j in ti.static(ti.ndrange(
                    3, 3)):  # Loop over 3x3 grid node neighborhood
                offset = ti.Vector([i, j])
                dpos = (offset.cast(float) - fx) * dx
                weight = w[i][0] * w[j][1]
                grid_v[base + offset] += weight * (p_mass * v[p] + affine @ dpos)
                grid_m[base + offset] += weight * p_mass
        for i, j in grid_m:
            if grid_m[i, j] > 0:  # No need for epsilon here
                grid_v[i,
                    j] = (1 / grid_m[i, j]) * grid_v[i,
                                                        j]  # Momentum to velocity
                grid_v[i, j][1] -= dt * 50  # gravity
                if i < 3 and grid_v[i, j][0] < 0:
                    grid_v[i, j][0] = 0  # Boundary conditions
                if i > n_grid - 3 and grid_v[i, j][0] > 0: grid_v[i, j][0] = 0
                if j < 3 and grid_v[i, j][1] < 0: grid_v[i, j][1] = 0
                if j > n_grid - 3 and grid_v[i, j][1] > 0: grid_v[i, j][1] = 0
        for p in x:  # grid to particle (G2P)
            base = (x[p] * inv_dx - 0.5).cast(int)
            fx = x[p] * inv_dx - base.cast(float)
            w = [0.5 * (1.5 - fx)**2, 0.75 - (fx - 1.0)**2, 0.5 * (fx - 0.5)**2]
            new_v = ti.Vector.zero(float, 2)
            new_C = ti.Matrix.zero(float, 2, 2)
            for i, j in ti.static(ti.ndrange(
                    3, 3)):  # loop over 3x3 grid node neighborhood
                dpos = ti.Vector([i, j]).cast(float) - fx
                g_v = grid_v[base + ti.Vector([i, j])]
                weight = w[i][0] * w[j][1]
                new_v += weight * g_v
                new_C += 4 * inv_dx * weight * g_v.outer_product(dpos)
            v[p], C[p] = new_v, new_C
            x[p] += dt * v[p]  # advection


    group_size = n_particles // 3


    @ti.kernel
    def initialize():
        for i in range(n_particles):
            x[i] = [
                ti.random() * 0.2 + 0.3 + 0.10 * (i // group_size),
                ti.random() * 0.2 + 0.05 + 0.32 * (i // group_size)
            ]
            material[i] = i // group_size  # 0: fluid 1: jelly 2: snow
            v[i] = ti.Matrix([0, 0])
            F[i] = ti.Matrix([[1, 0], [0, 1]])
            Jp[i] = 1

    print('    initializing ...')
    innner_iter = int(2e-3 // dt)
    outter_iter = 320
    initialize()
    for j in range(innner_iter):
        substep()

    print('    profiling begin ...')
    time_in_s = 0.0
    initialize()
    ti.clear_kernel_profile_info()
    for j in range(outter_iter):
        for s in range(innner_iter):
            substep()
    time_in_s += ti.kernel_profiler_total_time()
    print(f'    time = {time_in_s}')
    ti.reset()
    return time_in_s

if __name__ == '__main__':
    e2e_mpm99(ti.cuda)

# =========================================================================
# Kernel Profiler(count) @ X64 
# =========================================================================
# [      %     total   count |      min       avg       max   ] Kernel name
# -------------------------------------------------------------------------
# [ 84.27%   2.785 s   6080x |    0.423     0.458     5.278 ms] substep_c38_0_kernel_5_range_for
# [  7.35%   0.243 s   6080x |    0.033     0.040     3.666 ms] substep_c38_0_kernel_7_range_for
# [  4.22%   0.140 s   6080x |    0.017     0.023     0.526 ms] substep_c38_0_kernel_6_range_for
# [  4.16%   0.138 s   6080x |    0.015     0.023     2.545 ms] substep_c38_0_kernel_4_range_for
# -------------------------------------------------------------------------
# [100.00%] Total execution time:   3.305 s   number of results: 4
# =========================================================================
# time = 3.3049161434173584
# benchmarkbot@LEGION-REN7000K-26IOB:~/taichi/benchmarks/misc$ python end2end_cases/mpm99.py 
# [Taichi] version 0.8.6, llvm 10.0.0, commit 6ea3e8c3, linux, python 3.8.10
# [Taichi] Starting on arch=cuda
# initialization ...
# profiling begin ...
# =========================================================================
# Kernel Profiler(count) @ CUDA on NVIDIA GeForce RTX 2060
# =========================================================================
# [      %     total   count |      min       avg       max   ] Kernel name
# -------------------------------------------------------------------------
# [ 71.01%   0.101 s   6080x |    0.000     0.017     0.028 ms] substep_c38_0_kernel_5_range_for
# [ 18.08%   0.026 s   6080x |    0.000     0.004     0.008 ms] substep_c38_0_kernel_7_range_for
# [  5.92%   0.008 s   6080x |    0.000     0.001     0.013 ms] substep_c38_0_kernel_6_range_for
# [  4.99%   0.007 s   6080x |    0.000     0.001     0.013 ms] substep_c38_0_kernel_4_range_for
# -------------------------------------------------------------------------
# [100.00%] Total execution time:   0.143 s   number of results: 4
# =========================================================================