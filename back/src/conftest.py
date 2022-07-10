import pytest

from py_src.back_end.epidemic_models.utils.dynamics_helpers import set_SIR
from py_src.back_end.epidemic_models.utils.common_helpers import get_model_name
from py_src.params_and_config import (set_domain_config, set_dispersal, set_infectious_lt,
                                      set_initial_conditions, set_runtime, set_infection_dynamics,
                                      set_R0_trace, GenericSimulationConfig, RuntimeSettings, SaveOptions)


def gen_sim_config():
    runtime = set_runtime(steps=100)
    dispersal = set_dispersal(model='ga', dispersal_param=100)
    initial_conditions = set_initial_conditions(distribution='centralised', number_infected=10)
    domain_config = set_domain_config('simple_square', scale_constant=1, tree_density=0.01, patch_size=(100, 100))
    infection_dynamics = set_infection_dynamics(compartments='SIR', beta_factor=1, pr_approx=False)
    infection_lt = set_infectious_lt(distribution='step', life_time_parameter=10)
    R0_trace = set_R0_trace(active=False, transition_times=True, get_network=True)
    generic_sim = GenericSimulationConfig({'runtime': runtime,
                                           'dispersal': dispersal,
                                           'infection_dynamics': infection_dynamics,
                                           'infectious_lt': infection_lt,
                                           'initial_conditions': initial_conditions,
                                           'domain_config': domain_config,
                                           'R0_trace': R0_trace,
                                           'sim_name': get_model_name(infection_dynamics.compartments,
                                                                      dispersal.model_type)})
    return generic_sim


@pytest.fixture
def sim_context() -> GenericSimulationConfig:
    return gen_sim_config()


@pytest.fixture
def runtime_settings() -> RuntimeSettings:
    return RuntimeSettings()


@pytest.fixture
def save_options() -> SaveOptions:
    return SaveOptions()


@pytest.fixture()
def arbitrary_SIR_fields():
    gen_sim = gen_sim_config()
    return set_SIR(gen_sim.domain_config, gen_sim.initial_conditions, gen_sim.infectious_lt)
