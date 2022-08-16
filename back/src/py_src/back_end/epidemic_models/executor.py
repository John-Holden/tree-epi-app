import os
import ctypes
from time import sleep
from typing import List
import numpy as np
import datetime as dt
from multiprocessing import Process
from py_src.back_end.plotting.frame_plot import SIR_frame
from py_src.back_end.epidemic_models.compartments import SIR
from py_src.back_end.epidemic_models.utils.dynamics_helpers import set_SIR, R0_finder, set_I_lt
from py_src.back_end.epidemic_models.utils.common_helpers import (get_tree_density, get_model_name, logger, write_simulation_params,
                                                                  write_SIR_fields, get_env_var)

from py_src.params_and_config import (PATH_TO_CPP_EXECUTABLE, GenericSimulationConfig, Infection_dynamics, RuntimeSettings, SaveOptions, 
                                      set_dispersal, set_domain_config, set_runtime, set_infectious_lt, set_initial_conditions, 
                                      set_infection_dynamics, set_R0_trace, set_epidemic_parameters)
    



def find_beta_max(density, dispersal_value, dispersal_norm_factor, inf_lt) -> float:
    """
        Calculate an upper bound for R0 based on input epidemic parameters
    """

    for beta_factor_max in np.arange(1, 100000, 2):
        R0_est = R0_finder(beta_factor_max, density, dispersal_value, dispersal_norm_factor, inf_lt)
        if R0_est > 20:
            print(f'Beta factor {beta_factor_max} | R0 est {R0_est}')
            return beta_factor_max

    raise Exception('Did not find max beta value')
    



def get_updates(epi_params: dict) -> float:
    """
        Calculate an estimate for R0 based on input epidemic parameters
    """
    host_number = int(epi_params['host_number']) if epi_params['host_number'] != '' else 0 
    domain_size = tuple(map(int, epi_params['domain_size']))

    if host_number < 100:
        return

    if not domain_size[0] * domain_size[1]:
        return

    density = get_tree_density(host_number, domain_size)
    beta_factor = int(epi_params['infectivity'])
    
    if not beta_factor:
        return

    inf_lt = int(epi_params['infectious_lifetime'])

    if not inf_lt:
        return
            
    dispersal_type, dispersal_param = epi_params['dispersal_type'], epi_params['dispersal_param']
    dispersal_param = int(dispersal_param) if dispersal_type == 'gaussian' \
                                                           else tuple(map(float, dispersal_param))

    if type(dispersal_param) == int and not dispersal_param:
        return

    dispersal = set_dispersal(dispersal_type, dispersal_param)
    R0_est = R0_finder(beta_factor, density, dispersal.value, dispersal.norm_factor, inf_lt)
    beta_max = find_beta_max(density, dispersal.value, dispersal.norm_factor, inf_lt)

    return round(R0_est, 2), round(density, 3), round(beta_max)


def get_simulation_config(sim_params: dict) -> GenericSimulationConfig:
    """
        Validate and return the simulation configuaration 
    """

    # Set domain & host number
    host_number = int(sim_params['host_number'])
    domain_size = tuple(map(int, sim_params['domain_size']))
    
    domain = set_domain_config(domain_type='simple_square',
                               scale_constant=1,
                               patch_size=domain_size,
                               tree_density=get_tree_density(host_number, domain_size))

    # Set dispersal
    dispersal_type, dispersal_param = sim_params['dispersal_type'], sim_params['dispersal_param']
    dispersal_param = int(dispersal_param) if dispersal_type == 'gaussian' \
                                                          else tuple(map(float, dispersal_param))
    dispersal = set_dispersal(dispersal_type, dispersal_param)
    # Set runtime & infection dynamics
    runtime = set_runtime(int(sim_params['simulation_runtime']))
    infectious_lt = set_infectious_lt('exp', int(sim_params['infectious_lifetime']))
    beta_factor = float(sim_params['infectivity'])
    infection_dynamics = set_infection_dynamics('SIR', beta_factor, pr_approx=False)
    initial_conditions = set_initial_conditions(sim_params['initially_infected_dist'],
                                                int(sim_params['initially_infected_hosts']))
    
    if get_env_var('FLASK_ENV') == 'development':
        logger(f'[i] host number: {host_number}')
        logger(f'[i] Domain size: {domain_size}')
        logger(f'[i] Dispersal: {dispersal}')
        logger(f'[i] Infectin dynamics: {infection_dynamics}')
        logger(f'[i] Inital conditions: {initial_conditions}')

    return GenericSimulationConfig({'runtime': runtime,
                                    'dispersal': dispersal,
                                    'infection_dynamics': infection_dynamics,
                                    'infectious_lt': infectious_lt,
                                    'initial_conditions': initial_conditions,
                                    'domain_config': domain,
                                    'R0_trace': set_R0_trace(active=False),
                                    'sim_name': get_model_name(infection_dynamics.compartments, dispersal.model_type)})




def pre_sim_checks(sim_context: GenericSimulationConfig, save_options: SaveOptions):
    logger(' generic_SIR - perfoming pre-sim checks')
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


def generic_SIR(sim_context: GenericSimulationConfig, save_options: SaveOptions, runtime_settings: RuntimeSettings) -> dict:
    """
    Run a single SIR/SEIR model simulation
    :param save_options:
    :param runtime_settings:
    :param sim_context:
    """

    try:
        pre_sim_checks(sim_context, save_options)
        logger(f'[i] Succesful pre-sim checks')
    except Exception as e:
        logger(f'Failed pre-sim checks')
        raise e
    
    
    epidemic_parameters = set_epidemic_parameters(sim_context.domain_config.tree_density,
                                                  sim_context.infection_dynamics.beta_factor,
                                                  sim_context.dispersal,
                                                  sim_context.sporulation)

    start = dt.datetime.now()
    sim_result = SIR.run_SIR(sim_context, save_options, runtime_settings, epidemic_parameters)
    elapsed = dt.datetime.now() - start
    logger(f"[i] Termination condition: {sim_result['termination']}...\n"
           f"[i] Sim steps elapsed: {sim_result['end']}...\n"
           f"[i] Sim time elapsed: {elapsed} (s)...")
    
    return sim_result['SIR_fields']



def combine_SIR_fields(S, I, R, inf_lt):
    # populate SIR feild of the form: x1, y1, inf_t1, status \
    #                                 xN, y1N inf_tN, status. where status /in [1, 2, 3] 1: S 2: I 3:R
    # i.e. assuming no R infections...
    
    SIR_fields = np.zeros(shape=(len(S[0]) + len(I[0]) + len(R[0]), 4 )).astype(int)
    num_S = len(S[0])
    num_I = len(I[0])
    assert not len(R[0])

    SIR_fields[:,0][:num_S] = S[0]
    SIR_fields[:,1][:num_S] = S[1]
    SIR_fields[:,3][:num_S] = np.ones(num_S)

    SIR_fields[:,0][num_S:] = I[0]
    SIR_fields[:,1][num_S:] = I[1]
    SIR_fields[:,3][num_S:] = 2 * np.ones(num_I)
    
    # Pre-populate all positions with infectious lifetimes - saves recaculating per step
    SIR_fields[:, 2] = set_I_lt(inf_lt, num_S + num_I, t=0) 

    return SIR_fields
    
    
# Horrible function to reverse-engineer SIR fields compatible with frame_plot
def split_SIR_fields(pos_x: np.ndarray, pos_y: np.ndarray, state: np.ndarray):

    S = [[], []]
    I = [[], []]
    R = [[], []]
    
    for i in range(len(pos_x)):
        tree = state[i]
        if tree == 1:
            S[0].append(pos_x[i])
            S[1].append(pos_y[i])
        elif tree == 2:
            I[0].append(pos_x[i])
            I[1].append(pos_y[i])
        elif tree == 3:
            R[0].append(pos_x[i])
            R[1].append(pos_y[i])
    
    S[0] = np.array(S[0])
    S[1] = np.array(S[1])   
    I[0] = np.array(I[0])
    I[1] = np.array(I[1])
    R[0] = np.array(R[0])
    R[1] = np.array(R[1])
    return S, I , R



def execute_cpp_SIR(sim_context: GenericSimulationConfig, save_options: SaveOptions, runtime_settings: RuntimeSettings):
    """C-bindigns that call pre-compiled simulation code"""
    from ctypes import cdll

    logger('[i] execute_cpp_SIR - loading library and running compiled simulation')

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
        
        epidemic_parameters = set_epidemic_parameters(sim_context.domain_config.tree_density,
                                                  sim_context.infection_dynamics.beta_factor,
                                                  sim_context.dispersal,
                                                  sim_context.sporulation)
        
        sim_context.epidemic_params = epidemic_parameters
        
        sim_name = write_simulation_params(sim_context, save_options, runtime_settings)
        S, I, R = set_SIR(sim_context.domain_config, sim_context.initial_conditions, sim_context.infectious_lt)        
        SIR_fields = combine_SIR_fields(S, I, R, sim_context.infectious_lt)
        write_SIR_fields(sim_name, SIR_fields)

        p1 = Process(target=sim_handler.Execute, args=(sim_name,))
        p1.start()
        p2 = Process(target=parallel_anim, args=([sim_name, sim_context],))
        p2.start()
        p1.join()
        p2.join()
    
        elapsed = dt.datetime.now() - start
    except Exception as e:
        elapsed = dt.datetime.now() - start
        logger(f'execute_cpp_SIR - ERROR! Exiting after {elapsed} (s)', extra={"Reason": e})
        raise e

    logger(f'execute_cpp_SIR - finished in {elapsed} (s)')



def parallel_anim(anim_args: List) -> None:
    # Parallellise animations while b/e computes code
    sim_location: str = anim_args[0]
    sim_context: GenericSimulationConfig = anim_args[1]

    print("[i] Animating in parallell")
    pos_x = np.loadtxt(open(f"{sim_location}/pos_x.csv", "rb"), delimiter=",").astype(int)
    pos_y = np.loadtxt(open(f"{sim_location}/pos_y.csv", "rb"), delimiter=",").astype(int)
    while True:
        files_ = os.listdir(sim_location)
        files = [file for file in files_ if "stat_" in file]
        times = [file.split('_')[1].replace(".csv", "") for file in files]

        for time, file in zip(times, files):
            try:
                state = np.genfromtxt(open(f"{sim_location}/{file}", "r")).astype(int)
            except Exception as e:
                print("Error on:")
                print(f"{sim_location}/{file}")
                raise e

            S, I, R = split_SIR_fields(pos_x, pos_y, state)
            SIR_frame(S, I, R, int(time), sim_context, save_frame=True)
            os.remove(f"{sim_location}/{file}")

        # Terminte if end file in directory & there is no more sims to animate
        if "end" in files_ and not len(files):
            print("end in files, exiting...")
            print('FILES LEFT...====', files)
            break

    return