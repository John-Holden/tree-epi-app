import numpy as np
import pytest
import params_and_config as prm_conf
from py_src.back_end.epidemic_models.utils.common_helpers import get_model_name
from py_src.back_end.epidemic_models.utils.dynamics_helpers import set_SIR
from py_src.back_end.epidemic_models.utils.common_helpers import get_initial_host_number, get_total_host_number


def test_dispersal_setter_fails():
    """
    Test variety of use cases for setting dispersal config
    :return:
    """
    # Test config/param input errors FAIL expected
    with pytest.raises(AssertionError):
        prm_conf.set_dispersal(model=None, dispersal_param=1)
    with pytest.raises(NotImplementedError):
        prm_conf.set_dispersal(model='undefined model', dispersal_param=1)
    with pytest.raises(Exception) as err:
        prm_conf.set_dispersal(model='inverse power law', dispersal_param=1)
    assert 'Pl dispersal params not set correctly, expected numeric types: (ell, a)' == err.value.msg
    with pytest.raises(Exception) as err:
        prm_conf.set_dispersal(model='gaussian', dispersal_param='wrong type')
    assert 'Ga dispersal params not set correctly, expected numeric type: ell' == err.value.msg
    with pytest.warns(UserWarning):
        prm_conf.set_dispersal(model='Gaussian', dispersal_param=1, ADB_mode=True)


def test_dispersal_setter_passes():
    # Test config/param input errors PASS expected
    dispersal_param_out = prm_conf.set_dispersal(model='inverse power law', dispersal_param=(1, 1))
    assert dispersal_param_out.model_type == 'power_law'
    ell_param_out = prm_conf.set_dispersal(model='Gaussian', dispersal_param=1)
    assert ell_param_out.model_type == 'gaussian'
    ell_param_out = prm_conf.set_dispersal(model='Gaussian', ADB_mode=True)
    assert ell_param_out.value == prm_conf.ELL_ADB_GA
    ell_param_out = prm_conf.set_dispersal(model='power law', ADB_mode=True)
    assert ell_param_out.value == prm_conf.ELL_ADB_PL


def test_dispersal_numerics():
    # todo verify norm factors...
    # Gaussian
    ell_param = 1
    dispersal_param_out = prm_conf.set_dispersal(model='ga', dispersal_param=ell_param)
    assert dispersal_param_out.norm_factor == 1/(2 * np.pi * ell_param**2)
    with pytest.raises(Exception):
        prm_conf.set_dispersal(model='ga', dispersal_param=0)
    with pytest.raises(Exception):
        prm_conf.set_dispersal(model='ga', dispersal_param=np.infty)
    # Inverse power law
    ell_param = (1, 1)
    dispersal_param_out = prm_conf.set_dispersal(model='pl', dispersal_param=ell_param)
    assert dispersal_param_out.norm_factor == ((ell_param[1] - 1) * (ell_param[1] - 2)) / (2 * np.pi * ell_param[0] ** 2)
    with pytest.raises(Exception):
        prm_conf.set_dispersal(model='pl', dispersal_param=(100, 0))
    with pytest.raises(Exception):
        prm_conf.set_dispersal(model='pl', dispersal_param=(0, 2))


def test_infection_dynamics_setter():
    out = prm_conf.set_infection_dynamics('SIR', beta_factor=1, ADB_mode=False)
    assert out.compartments == 'SIR'
    with pytest.raises(Exception):
        prm_conf.set_infection_dynamics('bad_model_name', beta_factor=1, ADB_mode=False)
    with pytest.raises(NotImplementedError):
        prm_conf.set_infection_dynamics('SEIR', beta_factor=1, ADB_mode=False)
    with pytest.raises(Exception):
        prm_conf.set_infection_dynamics('SIR', beta_factor=1, ADB_mode=True)


def test_ADB_sporulation_setter():
    with pytest.raises(NotImplementedError):
        prm_conf.set_ADB_sporulation('non-existent-sporulation-model')

    out = prm_conf.set_ADB_sporulation('step')
    assert out.model == 'step'
    out = prm_conf.set_ADB_sporulation('peaked')
    assert out.model == 'peaked'


def test_model_name():
    dispersal_conf = prm_conf.set_dispersal(model='ga', ADB_mode=True)
    model_name = get_model_name(compartments='SIR', dispersal_model=dispersal_conf.model_type)
    assert model_name == 'SIR-phi0-ga'
    dispersal_conf = prm_conf.set_dispersal(model='pl', ADB_mode=True)
    sporulation = prm_conf.set_ADB_sporulation('step')
    model_name = get_model_name(compartments='SEIR', sporulation_model=sporulation.model,
                                dispersal_model=dispersal_conf.model_type)

    assert model_name == 'SEIR-phi1-pl'


def test_domain_conf_setter(sim_context, arbitrary_SIR_fields):
    with pytest.warns(UserWarning):
        prm_conf.set_domain_config('simple_square', scale_constant=10, tree_density=0.10, patch_size=(199, 199))
    with pytest.raises(NotImplementedError):
        prm_conf.set_domain_config('not_valid_type', scale_constant=1, tree_density=0.10, patch_size=(199, 199))
    with pytest.raises(Exception):
        prm_conf.set_domain_config('simple_square', scale_constant=100, tree_density=0.10, patch_size=(199, 199))
    with pytest.raises(Exception):
        prm_conf.set_domain_config('simple_square', scale_constant=1, tree_density=2.0, patch_size=(199, 199))
    with pytest.raises(Exception):
        prm_conf.set_domain_config('simple_square', scale_constant=1, tree_density=-2.0, patch_size=(199, 199))
    with pytest.raises(Exception):
        prm_conf.set_domain_config('simple_square', scale_constant=1, tree_density=0.10, patch_size=(199, 199),
                                   ADB_mode=True)
    with pytest.raises(Exception):
        prm_conf.set_domain_config('simple_square', scale_constant=1, tree_density=0.10, patch_size=(2001, 10),
                                   ADB_mode=True)
    tree_density = 0.01
    patch_size = (100, 100)
    assert get_initial_host_number(patch_size, tree_density) == patch_size[0] * patch_size[1] * tree_density

    S, I, R = arbitrary_SIR_fields
    host_number = get_total_host_number(S, I, R, sim_context.domain_config)
    assert host_number == len(S[0]) + len(I[0]) + len(R[0])

    # Compare different methods of calculating hosts - repeat due to stochasticity
    for repeat in range(10):
        sim_context.domain_config = prm_conf.set_domain_config('simple_square', 1, tree_density=0.5,
                                                               patch_size=(200, 200))
        sim_context.initial_conditions = prm_conf.set_initial_conditions(distribution='centralised', number_infected=0)
        S, I, R = set_SIR(sim_context.domain_config, sim_context.initial_conditions, sim_context.infectious_lt)
        host_number = get_total_host_number(S, I, R, sim_context.domain_config)
        assert host_number == get_initial_host_number(sim_context.domain_config.patch_size,
                                                      sim_context.domain_config.tree_density)










