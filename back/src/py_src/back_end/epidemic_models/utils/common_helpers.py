from cmath import log
import os
import math
import json
from jinja2 import UndefinedError
import numpy as np
import datetime as dt
from typing import Optional, List
from py_src.params_and_config import (DomainConfig, Compartmentalised_models, GenericSimulationConfig, SaveOptions, 
                                      RuntimeSettings, PATH_TO_TEMP_CPP_STORE)


def time_print(time_seconds: int, msg: Optional[str] = 'Simulation done in: ', display: Optional[bool] = True) -> str:
    """
    Pretty formatter to display time
    """
    seconds = math.floor(time_seconds)
    hrs = math.floor(seconds / 3600)
    mns = math.floor(seconds / 60)
    secs = seconds % 60

    if seconds < 60:
        if display:
            print(f'{msg} {seconds} (s)')
    elif 60 <= seconds < 3600:
        if display:
            print(f'{msg} {mns} (mins): {secs} (s)')
    elif seconds >= 3600:
        if display:
            print(f'{msg} {hrs} (Hrs): {mns%60} (mins): {secs} (s)')

    return f'{msg} {hrs} (Hrs): {mns%60} (mins): {secs} (s)'


def get_initial_host_number(patch_size: tuple, tree_density: float) -> float:
    """
    Calculate number of susceptible hosts in a simple flat domain of size [Lx, Ly]
    """
    return patch_size[0] * patch_size[1] * tree_density


def simple_square_host_num(S: List[np.ndarray], I: List[np.ndarray], R: List[np.ndarray]) -> int:
    """
    From list of SIR fields, return the total number of hosts in the system
    """
    return len(S[0]) + len(I[0]) + len(R[0])


def get_total_host_number(S: List[np.ndarray], I: List[np.ndarray], R: List[np.ndarray],
                          domain_config: DomainConfig) -> int:
    # Find and return the total number of trees in the domain based on SIR
    if domain_config.domain_type == 'simple_square':
        return simple_square_host_num(S, I, R)

    raise NotImplementedError(f'domain type: {domain_config.domain_type}')


def get_tree_density(host_number: int, patch_size: tuple):
    # Find tree density based on host number and domain config
    return host_number / (patch_size[0] * patch_size[1])


def get_model_name(compartments: str, dispersal_model: str, sporulation_model: Optional[str] = None) -> str:
    """
    Get the model-name, based on sporulation and dispersal type
    :param compartments:
    :param dispersal_model:
    :param sporulation_model:

    :return:
    """

    if compartments not in Compartmentalised_models:
        raise NotImplementedError(f'Expected models {Compartmentalised_models}, found type {compartments}')

    name = False
    if sporulation_model is None:
        name = 'phi0'
    elif sporulation_model == 'step':
        name = 'phi1'
    elif sporulation_model == 'peaked':
        name = 'phi2'
    elif not compartments:
        raise Exception('Incorrectly defined sporulation')

    if 'power' in dispersal_model and 'law' in dispersal_model:
        return f'{compartments}-{name}-pl'
    elif dispersal_model in ['Gaussian', 'gaussian', 'ga']:
        return f'{compartments}-{name}-ga'


def logger(msg: str, extra: Optional[dict] = None):
    """
    Simple pretty logger
    """
    
    if extra:
        list_objects = []
        for key_value in extra.items():
            key, value = key_value
            fmt_extra = f'\n\t{key} - {value}'
            list_objects.append(fmt_extra)

        print(f'{msg}: {"".join(list_objects)}')
        return
    
    print(msg)


def write_simulation_params(sim_context: GenericSimulationConfig, save_options: SaveOptions, rt_settings: RuntimeSettings) -> str:
    """
    Write simulation parameters to json file & return save location - loaded in by c++ executable
    """
    
    sim_write_loc = f'{PATH_TO_TEMP_CPP_STORE}{dt.datetime.now().strftime("%d%m%Y%H%M%S")}'
    logger('[i] Writing sim parameters & config to: {PATH_TO_TEMP_CPP_STORE}')

    if os.path.exists(sim_write_loc):
        raise Exception(f'Path {sim_write_loc} already exists!')
    else:
        os.mkdir(sim_write_loc)

    sim_params = {}

    for obj in sim_context.items():
        # Iterate through each config element
        config_element_name, config_element_value = obj

        if config_element_name == 'sim_name':
            sim_params["sim_name"] = sim_context.sim_name
        
        elif config_element_name == 'domain_config':
            sim_params["domain"] = {"type": sim_context.domain_config.domain_type, "scale_const": sim_context.domain_config.scale_constant,
                                    "tree_density": sim_context.domain_config.tree_density, "patch_size": sim_context.domain_config.patch_size}      
        
        elif config_element_name == "dispersal":
            sim_params["dispersal"] = {"model": sim_context.dispersal.model_type, "value": sim_context.dispersal.value, "norm": sim_context.dispersal.norm_factor}
        
        else:
            config_element_dict = config_element_value._asdict()
            sim_params[config_element_name] = config_element_dict


    sim_params['save_options'] = json.loads(save_options.to_json())
    sim_params['rt_settings'] = json.loads(rt_settings.to_json())

    with open(f'{sim_write_loc}/parameters.json', 'w') as f:
        json.dump(sim_params, f, indent=4)

    return sim_write_loc


def write_SIR_fields(sim_save_loc: str, SIR_fields) -> None:
    """
    Write SI fields to csv (should be no R fields at t=0)
    """
    np.savetxt(f'{sim_save_loc}/SIR.csv', SIR_fields, fmt='%i', delimiter=',')

        
def get_env_var(var: str):
    if os.environ.get(var) is None:
        logger(f'[e] Environment variable {var} not defined!')
        return None
    
    return os.environ.get(var)
        

