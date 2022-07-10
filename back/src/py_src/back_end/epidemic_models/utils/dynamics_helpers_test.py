import numpy as np
import pytest

import py_src.params_and_config as prm_cfg
from py_src.params_and_config import set_initial_conditions, set_infectious_lt

from py_src.back_end.epidemic_models.utils.dynamics_helpers import set_S, set_I, set_SIR


def test_set_S():
    rhos = np.arange(0.0, 1.0, 0.05)
    patch_size = (200, 200)
    for rho in rhos:
        S = set_S(rho, patch_size)
        assert len(S[0]) == int(rho * patch_size[0] * patch_size[1])

    rho = 0.25
    patch_dims = np.arange(0, 1000, 100)
    patch_sizes = (np.random.permutation(patch_dims), np.random.permutation(patch_dims))
    for L_row, L_col in zip(patch_sizes[0], patch_sizes[1]):
        S = set_S(rho, (L_row, L_col))
        assert len(S[0]) == int(rho * L_row * L_col)


def test_set_I():
    """"""
    with pytest.raises(Exception):
        init_dist = prm_cfg.set_initial_conditions(distribution='not-real-disgt', number_infected=10)
        inf_lt = prm_cfg.set_infectious_lt('exp', life_time_parameter=10)
        set_I(init_dist, (10, 10), inf_lt)

    init_dist = prm_cfg.set_initial_conditions(distribution='random', number_infected=10)

    inf_lt = prm_cfg.set_infectious_lt('step', life_time_parameter=10)
    I = set_I(init_dist, (10, 10), inf_lt)
    assert len(I[0]) == init_dist.initially_infected
    assert all(np.equal(I[2], np.array([inf_lt.steps + 1] * init_dist.initially_infected)))


def test_set_SIR():
    # Patch size too small
    with pytest.raises(Exception):
        domain_cfg = prm_cfg.set_domain_config('simple_square', scale_constant=1, tree_density=1,
                                               patch_size=(1, 1))
        init_dist = set_initial_conditions(distribution='random', number_infected=10)
        inf_lt = set_infectious_lt('step', life_time_parameter=10)
        set_SIR(domain_config=domain_cfg, initial_conditions=init_dist, infect_lt=inf_lt)

    with pytest.raises(Exception):
        domain_cfg = prm_cfg.set_domain_config('simple_square', scale_constant=1, tree_density=1,
                                               patch_size=(500, 500))
        init_dist = set_initial_conditions(distribution='random', number_infected=10**6)
        inf_lt = set_infectious_lt('step', life_time_parameter=10)
        set_SIR(domain_config=domain_cfg, initial_conditions=init_dist, infect_lt=inf_lt)

    # Happy path for random IC
    domain_cfg = prm_cfg.set_domain_config('simple_square', scale_constant=1, tree_density=1, patch_size=(100, 100))
    init_dist = set_initial_conditions(distribution='random', number_infected=10)
    inf_lt = set_infectious_lt('step', life_time_parameter=10)
    number_S = domain_cfg.tree_density * domain_cfg.patch_size[0] * domain_cfg.patch_size[1]
    S, I, R = set_SIR(domain_config=domain_cfg, initial_conditions=init_dist, infect_lt=inf_lt)
    assert number_S - init_dist.initially_infected == len(S[0])

    # Happy path for centralised IC
    domain_cfg = prm_cfg.set_domain_config('simple_square', scale_constant=1, tree_density=1, patch_size=(150, 80))
    init_dist = set_initial_conditions(distribution='centralised', number_infected=55)
    inf_lt = set_infectious_lt('exp', life_time_parameter=101)
    number_S = domain_cfg.tree_density * domain_cfg.patch_size[0] * domain_cfg.patch_size[1]
    S, I, R = set_SIR(domain_config=domain_cfg, initial_conditions=init_dist, infect_lt=inf_lt)
    assert number_S - init_dist.initially_infected == len(S[0])

    # Happy path when rho < 1.0
    for i in range(25):
        domain_cfg = prm_cfg.set_domain_config('simple_square', scale_constant=1, tree_density=0.01, patch_size=(500, 500))
        init_dist = set_initial_conditions(distribution='random', number_infected=25)
        inf_lt = set_infectious_lt('step', life_time_parameter=10)
        number_S = domain_cfg.tree_density * domain_cfg.patch_size[0] * domain_cfg.patch_size[1]
        S, I, R = set_SIR(domain_config=domain_cfg, initial_conditions=init_dist, infect_lt=inf_lt)
        for S_row, S_col in zip(S[0], S[1]):
            for I_row, I_col in zip(I[0], I[1]):
                assert not (S_row == I_row and S_col == I_col)
        assert len(S[0]) <= number_S
        assert number_S - len(S[0]) <= init_dist.initially_infected


