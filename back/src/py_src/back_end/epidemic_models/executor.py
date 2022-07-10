import ctypes
import datetime as dt
from py_src.back_end.epidemic_models.compartments import SIR
from py_src.back_end.epidemic_models.utils.dynamics_helpers import set_SIR
from py_src.back_end.epidemic_models.utils.common_helpers import (get_tree_density, get_model_name, logger, write_simulation_params,
                                                                  write_SIR_fields)

from py_src.params_and_config import (PATH_TO_CPP_EXECUTABLE, GenericSimulationConfig, RuntimeSettings, SaveOptions, 
                                      set_dispersal, set_domain_config, set_runtime, set_infectious_lt, set_initial_conditions, 
                                      set_infection_dynamics, set_R0_trace)
    


def get_simulation_config(sim_params: dict) -> GenericSimulationConfig:
    """Validate and return the simulation configuaration """

    host_number = int(sim_params['host_number'])
    domain_size = tuple(map(int, sim_params['domain_size']))
    dispersal = set_dispersal(sim_params['dispersal_type'], sim_params['dispersal_param'])
    
    domain = set_domain_config(domain_type='simple_square',
                               scale_constant=1,
                               patch_size=domain_size,
                               tree_density=get_tree_density(host_number, domain_size))

    runtime = set_runtime(int(sim_params['simulation_runtime']))
    infectious_lt = set_infectious_lt('exp', int(sim_params['infectious_lifetime']))

    infection_dynamics = set_infection_dynamics('SIR',
                                                int(sim_params['secondary_R0']),
                                                pr_approx=False)

    initial_conditions = set_initial_conditions(sim_params['initially_infected_dist'],
                                                int(sim_params['initially_infected_hosts']))

    return GenericSimulationConfig({'runtime': runtime,
                                    'dispersal': dispersal,
                                    'infection_dynamics': infection_dynamics,
                                    'infectious_lt': infectious_lt,
                                    'initial_conditions': initial_conditions,
                                    'domain_config': domain,
                                    'R0_trace': set_R0_trace(active=False),
                                    'sim_name': get_model_name(infection_dynamics.compartments, dispersal.model_type)})




def pre_sim_checks(sim_context: GenericSimulationConfig, save_options: SaveOptions):
    logger.info(' generic_SIR - perfoming pre-sim checks')
    if sim_context.dispersal.model_type == 'power_law' and save_options.save_max_d:
        raise Exception('Percolation-like boundary conditions is not valid for power-law based dispersal')

    if sim_context.sporulation:
        raise NotImplementedError('Sporulation for generic sim not implemented')

    if not sim_context.runtime.steps:
        raise Exception('Expected non-zero runtime')

    if sim_context.R0_trace.active and not sim_context.infection_dynamics.pr_approx:
        raise Exception('We cannot cannot contact-trace secondary infections when using the full poisson construct')

    if sim_context.other_boundary_conditions.percolation and save_options.save_max_d:
        raise Exception('Enable max distance metric to use the percolation BCD')


def generic_SIR(sim_context: GenericSimulationConfig, save_options: SaveOptions, runtime_settings: RuntimeSettings):
    """
    Run a single SIR/SEIR model simulation
    :param save_options:
    :param runtime_settings:
    :param sim_context:
    """

    try:
        pre_sim_checks(sim_context, save_options)
    except Exception as e:
        logger.info(f'generic_SIR - Failed pre-sim checks')
        raise e

    start = dt.datetime.now()
    sim_result = SIR.run_SIR(sim_context, save_options, runtime_settings)
    elapsed = dt.datetime.now() - start
    logger.info(f"Termination condition: {sim_result['termination']} "
                f"Sim steps elapsed: {sim_result['end']}, "
                f"sim time elapsed: {elapsed} (s)")
    # todo
    #   end_of_sim_plots(sim_context, sim_result, runtime_settings)


def generic_SIR_animation(sim_context: GenericSimulationConfig, save_options: SaveOptions, runtime_settings: RuntimeSettings):
    try:
        pre_sim_checks(sim_context, save_options)
    except Exception as e:
        logger.info(f'generic_SIR - Failed pre-sim checks')
        raise e

    start = dt.datetime.now()
    SIR.SIR_function_animate(sim_context, save_options, runtime_settings)
    elapsed = dt.datetime.now() - start
    print(f"Simulation finished in {elapsed} (s)")
    logger.info(f"Simulation finished in {elapsed} (s)")


def execute_cpp_SIR(sim_context: GenericSimulationConfig, save_options: SaveOptions, runtime_settings: RuntimeSettings):
    """C-bindigns that call pre-compiled simulation code"""
    from ctypes import cdll

    logger('execute_cpp_SIR - loading library and running compiled simulation')
    
    lib = cdll.LoadLibrary(f'{PATH_TO_CPP_EXECUTABLE}/libSIR.so')
    class SimulationExecutor:
        def __init__(self):
            self.obj = lib.newSimOjb()

        def Execute(self, sim_name: str):
            c_string = ctypes.c_char_p(sim_name.encode('UTF-8'))
            return lib.execute(self.obj, c_string)

    try:
        sim_handler = SimulationExecutor()
        start = dt.datetime.now()
        sim_name = write_simulation_params(sim_context, save_options, runtime_settings)
        S, I, R = set_SIR(sim_context.domain_config, sim_context.initial_conditions, sim_context.infectious_lt)
        write_SIR_fields(sim_name, S, I, R)
        out = sim_handler.Execute(sim_name)
        elapsed = dt.datetime.now() - start
    except Exception as e:
        elapsed = dt.datetime.now() - start
        logger(f'execute_cpp_SIR - ERROR! Exiting after {elapsed} (s)', extra={"Reason": e})
        raise e

    logger(f'execute_cpp_SIR - finished in {elapsed} (s)')
