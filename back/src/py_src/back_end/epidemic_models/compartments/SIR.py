from operator import le
import os
import time
import numpy as np
from typing import Tuple, List
from py_src.back_end.plotting.frame_plot import SIR_frame
from py_src.back_end.epidemic_models.utils.common_helpers import logger
from py_src.back_end.epidemic_models.exceptions import IncorrectHostNumber
from py_src.back_end.epidemic_models.utils.common_helpers import get_total_host_number
from py_src.back_end.epidemic_models.utils.dynamics_helpers import (set_SIR, set_R0_trace_struct, new_infections)
from py_src.params_and_config import (Epidemic_parameters, GenericSimulationConfig, SaveOptions, RuntimeSettings, set_epidemic_parameters,
                                      LAMBDA_TIMEOUT)


def evolve_time_step(S_t1, I_t1, R_t1, t, epidemic_parameters, domain_config, dispersal, infectious_lt,
                     pr_approx) -> Tuple[List[np.ndarray], List[np.ndarray], List[np.ndarray]]:
    # Find new infections
    new_I, del_S = new_infections(epidemic_parameters, domain_config, dispersal,
                                  S_t1, I_t1, t, infectious_lt, pr_approx)
    # S_tree -> I_tree
    if new_I[0]:
        I_t2_row = np.hstack((I_t1[0], new_I[0]))  # infected rows
        I_t2_col = np.hstack((I_t1[1], new_I[1]))  # infected col
        I_t2_lt = np.hstack((I_t1[2], new_I[2]))  # infected lt
        S_t2_row = np.delete(S_t1[0], del_S)
        S_t2_col = np.delete(S_t1[1], del_S)  # remove new I from S
    else:
        S_t2_row = S_t1[0]
        S_t2_col = S_t1[1]
        I_t2_row = I_t1[0]
        I_t2_col = I_t1[1]
        I_t2_lt = I_t1[2]

    # I_tree -> R_tree
    new_R = np.where(I_t2_lt < t)
    if new_R[0].shape[0]:
        # Add newly removed trees to the removed class
        R_t2_row = np.hstack((R_t1[0], I_t2_row[new_R]))
        R_t2_col = np.hstack((R_t1[1], I_t2_col[new_R]))
        # Remove newly removed trees from the infected class
        I_t2_row = np.delete(I_t2_row, new_R)
        I_t2_col = np.delete(I_t2_col, new_R)
        I_t2_lt = np.delete(I_t2_lt, new_R)
    else:
        R_t2_row = R_t1[0]
        R_t2_col = R_t1[1]

    return [S_t2_row, S_t2_col], [I_t2_row, I_t2_col, I_t2_lt], [R_t2_row, R_t2_col]


def run_SIR(sim_context: GenericSimulationConfig, save_options: SaveOptions, rt_settings: RuntimeSettings,
            epidemic_parameters: Epidemic_parameters):
    """
    Simulate ash dieback over
    """

    # initialise structures
    logger(f'[i] Beginning simulation...')
    
    steps = range(sim_context.runtime.steps)
    S, I, R = set_SIR(sim_context.domain_config,
                      sim_context.initial_conditions,
                      sim_context.infectious_lt)

    break_condition = None
    max_d_ts = np.zeros(sim_context.runtime.steps) if save_options.save_max_d else None
    st_frames = {} if save_options.save_st_fields and rt_settings.frame_plot and rt_settings.frame_freq else None
    host_number = get_total_host_number(S, I, R, sim_context.domain_config)
    host_number_at_t = None
    S_ts = [host_number] * sim_context.runtime.steps if save_options.save_field_time_series else None
    I_ts = [sim_context.initial_conditions.initially_infected] * sim_context.runtime.steps if save_options.save_field_time_series else None
    R_ts = [0] * sim_context.runtime.steps if save_options.save_field_time_series else None
    
    R0_struct = set_R0_trace_struct(sim_context.R0_trace, sim_context.infection_dynamics, I) \
        if sim_context.R0_trace.active else None

    print(R0_struct)

    if 'HPC_MODE' not in os.environ and rt_settings.verbosity == 3:
        from tqdm import tqdm
        steps = tqdm(steps)

    start = time.time()
    t = 0
    try:
        for t in steps:
            # output simulation progress
            if rt_settings.verbosity:
                print(f't = {t}')
            if time.time() - start > LAMBDA_TIMEOUT - 10:
                logger(f' run_SIR - imminent lambda timout t = {time.time() - start} (s) of {LAMBDA_TIMEOUT}')

            # evolve time-step by one unit
            S, I, R = evolve_time_step(S, I, R, t,
                                       epidemic_parameters,
                                       sim_context.domain_config,
                                       sim_context.dispersal,
                                       sim_context.infectious_lt,
                                       sim_context.infection_dynamics.pr_approx)
            
            # perform post-step checks
            try:
                host_number_at_t = len(S[0]) + len(I[0]) + len(R[0])
                assert host_number_at_t == host_number
            except Exception:
                raise IncorrectHostNumber(expected=host_number, actual=host_number_at_t)
            
            # handle metrics & output
            if save_options.save_field_time_series:
                S_ts[t] = len(S[0])
                I_ts[t] = len(I[0])
                R_ts[t] = len(R[0])

            if R0_struct:
                a = None

            # if save_options.save_max_d:
                # max_d_ts[t] = get_max_d(I)

            if not len(I[0]):
                break_condition = 'infected tree extinction'
                break

            if save_options.save_st_fields and t % rt_settings.frame_freq == 0:
                st_frames[f't_{t}'] = np.array([I[0], I[1]])  # 'spatio temporal' frames

            if rt_settings.frame_plot and t % rt_settings.frame_freq == 0:
                SIR_frame(S, I, R, t, sim_context, save_options.frame_save, rt_settings.frame_show)

            if t == sim_context.runtime.steps - 1:
                break_condition = 'simulation time-steps exceeded'
                
    except Exception as e:
        logger(f'[e] Failed simulation: ', 
                extra={'Error': e, 
                       'simulation time steps elapsed': f'{t}',
                       'time elapsed': f'{time.time() - start} (s)'})
        raise e

    # construct post-simulation output
    sim_result = {"end": t,
                  "termination": break_condition,
                  'runtime': time.time() - start}

    if R0_struct:
        sim_result['R0_hist'] = R0_struct

    if max_d_ts:
        sim_result['max_d'] = max_d_ts

    if save_options.save_field_time_series:
        S_ts, I_ts, R_ts = S_ts[:t], I_ts[:t], R_ts[:t]
        sim_result['SIR_fields'] = {'S': S_ts, 'I': I_ts, 'R': R_ts}

    if st_frames:
        sim_result['data_fields'] = st_frames

    if save_options.save_mortality:
        sim_result['tree-mortality'] = len(R[0])
        sim_result['tree-mortality-ratio'] = len(R[0]) / host_number

    return sim_result