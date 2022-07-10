from back_end.epidemic_models.utils.common_helpers import get_model_name
from params_and_config import (set_ADB_runtime, set_dispersal, set_infection_dynamics, set_initial_conditions,
                               set_domain_config, set_R0_trace, get_ADB_lifetimes, set_ADB_sporulation,
                               ADBSimulationConfig, SaveOptions, RuntimeSettings)


def run_SIR():
    runtime = set_ADB_runtime(years=10)
    dispersal = set_dispersal(model='pl', ADB_mode=True)
    infection_dynamics = set_infection_dynamics(compartments='SEIR', ADB_mode=True)
    sporulation = set_ADB_sporulation('step')
    exposed_lt, infectious_lt = get_ADB_lifetimes()
    initial_conditions = set_initial_conditions(distribution='centralised', number_infected=10)
    domain_config = set_domain_config('simple_square', scale_constant=5, tree_density=0.01, patch_size=(500, 500),
                                      ADB_mode=True)

    R0_trace = set_R0_trace(active=True, get_distances=True)
    adb_sim = ADBSimulationConfig({'runtime': runtime,
                                   'dispersal': dispersal,
                                   'sporulation': sporulation,
                                   'exposed_lt': exposed_lt,
                                   'infectious_lt': infectious_lt,
                                   'infection_dynamics': infection_dynamics,
                                   'initial_conditions': initial_conditions,
                                   'domain_config': domain_config,
                                   'R0_trace': R0_trace})
    adb_sim.validate()
    adb_sim.model_name = get_model_name(infection_dynamics.compartments, dispersal.model_type)
    SaveOptions(save_Frame=True)
    RuntimeSettings()


if __name__ == '__main__':
    run_SIR()
