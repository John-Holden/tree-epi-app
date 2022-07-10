import numpy as np
import pytest
from unittest.mock import patch

from py_src.back_end.epidemic_models.compartments.SIR import evolve_time_step, run_SIR
from py_src.back_end.epidemic_models.utils.dynamics_helpers import new_infections, set_SIR
from py_src.back_end.epidemic_models.exceptions import IncorrectHostNumber
from py_src.params_and_config import (set_epidemic_parameters, set_domain_config, set_dispersal, set_infectious_lt,
                                      set_initial_conditions, Epidemic_parameters, set_runtime)


class Config:
    dispersal = set_dispersal(model='ga', dispersal_param=100)
    infection_lt = set_infectious_lt(distribution='step', life_time_parameter=10)
    initial_conditions = set_initial_conditions(distribution='centralised', number_infected=10)
    domain_config = set_domain_config('simple_square', scale_constant=1, tree_density=0.5, patch_size=(100, 100))


@pytest.fixture()
def SIR_fields(config):
    return gen_new_SIR(config)


def gen_new_SIR(config: Config):
    return set_SIR(config.domain_config, config.initial_conditions, config.infection_lt)


@pytest.fixture()
def config():
    return Config


@pytest.fixture()
def high_epidemic_params() -> Epidemic_parameters:
    return set_epidemic_parameters(rho=0.01, beta_factor=10000, dispersal=Config.dispersal, sporulation=None)


@pytest.fixture()
def low_epidemic_params() -> Epidemic_parameters:
    return set_epidemic_parameters(rho=0.01, beta_factor=10, dispersal=Config.dispersal, sporulation=None)


def test_new_infections_pr_full(config, high_epidemic_params):
    """
    Test infection dynamics when pr_approx = false, i.e. using the full Poisson construct
    :return:
    """
    # Executes successfully
    S_1, I_1, _ = gen_new_SIR(config)
    new_I, S_trans_I = new_infections(high_epidemic_params, config.domain_config, config.dispersal,
                                      S=S_1, I=I_1, t=1, inf_lt=config.infection_lt, prob_approx=False)

    # Verify the list of S trees to remove describe S_xy, where xy are the row & col of the infected tree I_xy
    for S_index, (new_I_row, new_I_col) in zip(S_trans_I, zip(new_I[0], new_I[1])):
        assert S_1[0][S_index] == new_I_row
        assert S_1[1][S_index] == new_I_col

    S_2, I_2, _ = gen_new_SIR(config)
    # Errors raise when numbers don't match up, i.e. expected S_(x, y) -> I_(x, y), but x,y isn't listed in S
    with pytest.raises(AssertionError):
        new_I, S_trans_I = new_infections(high_epidemic_params, config.domain_config, config.dispersal,
                                          S=S_2, I=I_1, t=1, inf_lt=config.infection_lt, prob_approx=False)

        for S_index, (new_I_row, new_I_col) in zip(S_trans_I, zip(new_I[0], new_I[1])):
            assert S_1[0][S_index] == new_I_row
            assert S_1[1][S_index] == new_I_col

    with pytest.raises(AssertionError):
        new_I, S_trans_I = new_infections(high_epidemic_params,  config.domain_config, config.dispersal,
                                          S=S_1, I=I_2, t=1, inf_lt=config.infection_lt, prob_approx=False)

        for S_index, (new_I_row, new_I_col) in zip(S_trans_I, zip(new_I[0], new_I[1])):
            assert S_2[0][S_index] == new_I_row
            assert S_2[1][S_index] == new_I_col


def test_evolve_time_step(config, SIR_fields, high_epidemic_params):
    t = 1
    S_t1, I_t1, R_t1 = SIR_fields
    for repeat in range(25):
        S_t2, I_t2, R_t2 = evolve_time_step(S_t1, I_t1, R_t1, t,
                                            high_epidemic_params,
                                            config.domain_config,
                                            config.dispersal,
                                            config.infection_lt,
                                            pr_approx=False)

        assert len(S_t1[0]) + len(I_t1[0]) == len(S_t2[0]) + len(I_t2[1])
        assert len(S_t2[0]) == len(S_t2[1])
        assert len(I_t2[0]) == len(I_t2[1])
        assert len(I_t2[1]) == len(I_t2[2])


@patch('epidemic_models.compartments.SIR.new_infections')
def test_SIR_evolve_time_step_new_infect(new_infection_fnc, sim_context, save_options, runtime_settings, SIR_fields):
    """
    Test the correct S,I,R fields are initialised after a new infection.
    """
    S, I, R = SIR_fields
    epidemic_params = set_epidemic_parameters(sim_context.domain_config.tree_density,
                                              sim_context.infection_dynamics.beta_factor,
                                              sim_context.dispersal,
                                              sim_context.sporulation)

    mocked_new_infections = ([S[0][1]], [S[1][1]], [1])
    mocked_infectious_lt = [1]
    new_infection_fnc.return_value = mocked_new_infections, mocked_infectious_lt

    S_out, I_out, R_out = evolve_time_step(S, I, R, 1, epidemic_params, sim_context.domain_config,
                                           sim_context.dispersal, sim_context.infectious_lt, pr_approx=False)

    assert len(R_out[0]) == len(R[0])
    assert len(S_out[0]) + len(mocked_new_infections[0]) == len(S[0])
    assert len(I_out[0]) == len(I[0]) + len(mocked_new_infections[0])
    assert len(S_out[0]) + len(I_out[0]) + len(R_out[0]) == len(S[0]) + len(I[0]) + len(R[0])


@patch('epidemic_models.compartments.SIR.new_infections')
def test_SIR_evolve_time_step_new_removed(new_infection_fnc, sim_context, save_options, runtime_settings, SIR_fields):
    """
    Test the correct S,I,R fields are initialised after a new infection.
    """
    S, I, R = SIR_fields
    epidemic_params = set_epidemic_parameters(sim_context.domain_config.tree_density,
                                              sim_context.infection_dynamics.beta_factor,
                                              sim_context.dispersal,
                                              sim_context.sporulation)

    mocked_new_infections = (np.array([]), np.array([]), np.array([]))
    mocked_infectious_lt = []
    new_infection_fnc.return_value = mocked_new_infections, mocked_infectious_lt

    t = 12  # i.e. a time-step greater than the initially infected life-time
    S_out, I_out, R_out = evolve_time_step(S, I, R, t, epidemic_params, sim_context.domain_config,
                                           sim_context.dispersal, sim_context.infectious_lt, pr_approx=False)

    assert len(I_out[0]) == 0
    assert len(R_out[0]) == len(I[0])
    assert len(S_out[0]) == len(S[0])
    assert len(S_out[0]) + len(I_out[0]) + len(R_out[0]) == len(S[0]) + len(I[0]) + len(R[0])


@patch('epidemic_models.compartments.SIR.new_infections')
def test_SIR_evolve_time_step_no_infected(new_infection_fnc, sim_context, save_options, runtime_settings, SIR_fields):
    """
    Test the correct S,I,R fields are initialised after a new infection.
    """
    S, I, R = SIR_fields
    epidemic_params = set_epidemic_parameters(sim_context.domain_config.tree_density,
                                              sim_context.infection_dynamics.beta_factor,
                                              sim_context.dispersal,
                                              sim_context.sporulation)

    mocked_new_infections = (np.array([]), np.array([]), np.array([]))
    mocked_infectious_lt = []
    new_infection_fnc.return_value = mocked_new_infections, mocked_infectious_lt

    S_out, I_out, R_out = evolve_time_step(S, I, R, 1, epidemic_params, sim_context.domain_config,
                                           sim_context.dispersal, sim_context.infectious_lt, pr_approx=False)

    assert np.equal(S_out, S).all()
    assert np.equal(I_out, I).all()
    assert np.equal(R_out, R).all()


def test_correct_SIR_number_no_exceptions(sim_context, save_options, runtime_settings, capsys):
    sim_context.domain_config.tree_density = 0.01
    sim_context.runtime = set_runtime(100)
    runtime_settings.verbosity = 3
    run_SIR(sim_context, save_options, runtime_settings)
    captured = capsys.readouterr()
    assert '/100' in captured.err


@patch('epidemic_models.compartments.SIR.evolve_time_step')
def test_incorrect_SIR_number_fails(evol_time_step, sim_context, save_options, runtime_settings, SIR_fields):
    S, I, R = SIR_fields
    evol_time_step.return_value = S, I, R
    # init a sim with sufficiently different domain with incorrect SIR_fields
    sim_context.domain_config.tree_density = 0.005
    with pytest.raises(IncorrectHostNumber):
        run_SIR(sim_context, save_options, runtime_settings)




