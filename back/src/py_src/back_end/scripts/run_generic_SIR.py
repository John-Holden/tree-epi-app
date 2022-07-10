from typing import Tuple
from back_end.epidemic_models import executor
from back_end.epidemic_models.utils.common_helpers import get_model_name
from params_and_config import (set_runtime, set_dispersal, set_infection_dynamics, set_infectious_lt,
                               set_initial_conditions, set_domain_config, set_R0_trace,
                               GenericSimulationConfig, SaveOptions, RuntimeSettings, mkdir_tmp_store)


def set_params() -> Tuple[GenericSimulationConfig, RuntimeSettings, SaveOptions]:
    runtime = set_runtime(steps=1)
    dispersal = set_dispersal(model='ga', dispersal_param=50)
    infection_dynamics = set_infection_dynamics(compartments='SIR', beta_factor=10, pr_approx=False)
    infectious_lt = set_infectious_lt(distribution='step', life_time_parameter=100)
    initial_conditions = set_initial_conditions(distribution='centralised', number_infected=10)
    domain_config = set_domain_config('simple_square', scale_constant=1, tree_density=0.01, patch_size=(500, 500))
    R0_trace = set_R0_trace(active=False, transition_times=True, get_network=True)
    generic_sim = GenericSimulationConfig({'runtime': runtime,
                                           'dispersal': dispersal,
                                           'infection_dynamics': infection_dynamics,
                                           'infectious_lt': infectious_lt,
                                           'initial_conditions': initial_conditions,
                                           'domain_config': domain_config,
                                           'R0_trace': R0_trace,
                                           'sim_name': get_model_name(infection_dynamics.compartments,
                                                                      dispersal.model_type)})
    rt_settings = RuntimeSettings()
    rt_settings.verbosity = 3
    rt_settings.frame_plot = True
    rt_settings.frame_show = False
    rt_settings.frame_freq = 1
    save_options = SaveOptions()
    save_options.frame_save = True
    mkdir_tmp_store()
    return generic_sim, rt_settings, save_options


def run_SIR():
    generic_sim, save_options, rt_settings = set_params()
    executor.generic_SIR(generic_sim, rt_settings, save_options)


def run_SIR_anim():
    generic_sim, save_options, rt_settings = set_params()
    executor.generic_SIR_animation(generic_sim, rt_settings, save_options)


if __name__ == '__main__':
    run_SIR_anim()
