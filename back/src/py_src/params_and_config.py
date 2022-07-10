"""
Define classes for dispersal_model parameters, settings and metrics.
    - dispersal values from https://doi.org/10.1093/femsec/fiy049 are:
    - density values from Fex dataset https://doi.org/10.1002/ece3.2661
"""
import os
import json
import types
import datetime
import numpy as np
from warnings import warn
from numbers import Number
from schematics import Model
from dataclasses import dataclass
from collections import namedtuple
from typing import Optional, Union, Tuple
from schematics.types import BaseType, StringType
from py_src.back_end.epidemic_models.exceptions import InvalidDispersalException, InvalidDispersalParamsException

LAMBDA_TIMEOUT = 300
PATH_TO_TEMP_STORE = f'{os.getcwd()}/temp_data/'
PATH_TO_DATA_STORE = f'{os.getcwd()}/py_src/back_end/anim_data/'
PATH_TO_CPP_EXECUTABLE = f'{os.getcwd()}/cpp_src'
PATH_TO_TEMP = '/tmp/anim_data'

# --------------Parameters and constants -------------- #
ELL_ADB_GA = 195
ELL_ADB_PL = (205, 3.3)
AVG_ASH_DENSITY = 0.017
L_QTL_ASH_DENSITY = 0.0065
MEDIAN_ASH_DENSITY = 0.011
U_QTL_ASH_DENSITY = 0.019
Compartmentalised_models = ['SIR', 'SEIR']
Infectious_life_time_distributions = ['exp', 'step']
Initial_infected_distributions = ['centralised', 'random']
Domain_types = ['simple_square', 'multi_square', 'urban', 'forest']
Sporulation_models = types.SimpleNamespace(**{'step': 'phi1', 'peaked': 'phi2'})
Ash_density_stats = types.SimpleNamespace(**{'l_qtl': L_QTL_ASH_DENSITY, 'median': MEDIAN_ASH_DENSITY,
                                             'avg': AVG_ASH_DENSITY, 'u_qtl': U_QTL_ASH_DENSITY})

# --------------Fixed simulation config definitions-------------- #
I_lt = namedtuple('I_lt', ['distribution', 'steps'])
Generic_runtime = namedtuple('RUNTIME', ['steps', 'unit'])
ADB_I_lt = namedtuple('I_lt', ['distribution', 'years', 'steps'])
ADB_E_lt = namedtuple('E_lt', ['exposed_lt_day', 'exposed_lt_month', 'exposed_lt_sd'])
Epidemic_parameters = namedtuple('Epidemic_parameters', ['rho', 'beta_pr', 'ell'])
Infection_dynamics = namedtuple('Infection_dynamics', ['compartments', 'beta_factor', 'pr_approx'])
Initial_conditions = namedtuple('Initial_conditions', ['distribution', 'initially_infected'])
Other_boundary_conditions = namedtuple('Boundary_conditions', ['percolation', 'max_infected_generation'])
Dispersal = namedtuple('Dispersal', ['model_type', 'value', 'norm_factor', 'function', 'normed'])
R0_tracker = namedtuple('R0_trace', ['active', 'get_distance', 'first_gen_only', 'transition_times', 'get_network'])
Domain = namedtuple('Domain_config', ['domain_type', 'patch_size', 'alpha', 'tree_density', 'total_hosts'])
ADB_model_runtime = namedtuple('model_runtime', ['years', 'steps', 'start_year', 'start_month', 'start_day',
                                                 'start_date', 'end_year', 'end_month', 'end_day'])
SporulationADB = namedtuple('SporulationADB', ['model', 'peak_months', 'peak_months_str', 'ga_sd', 'normed',
                                               'norm_factor'])


# --------------Mutable simulation config definitions------------- #
@dataclass
class SaveOptions:
    """
    Define which metrics are recorded over the simulation
    """
    frame_save: bool = False
    save_max_d: bool = False
    save_end_time: bool = False
    save_mortality: bool = False
    save_st_fields: bool = False  # st: "spatio-temporal"
    save_percolation: bool = False
    save_field_time_series: bool = False  # e.g. S(t), I(t), R(t)
    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)


@dataclass
class RuntimeSettings:
    """
    Simulation setup
    """
    frame_plot: bool = False
    frame_show: bool = False
    frame_animate: bool = False
    frame_freq: int = 10
    frame_ext = '.png'
    fields_at_freq: bool = False
    verbosity = 2  # verbosity
    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

    @staticmethod
    def ensemble_config(self):
        raise NotImplemented('Refactor for HPC useage')
        # self.verbosity = 0
        # self.hours_elapsed = 0
        # self.time_since_save = None
        # # ----------------HPC time-out/save settings--------------- #
        # self.begin_simulation = datetime.datetime.now()
        # self.hpc_end_save_freq = 600  # (s)
        # self.hpc_end_save_cutoff = 3600  # (s)
        # self.hpc_time_out = int(
        #     os.environ['HPC_TIME_OUT']) * 3600 if 'HPC_TIME_OUT' in os.environ else 7200


@dataclass
class DomainConfig:
    domain_type: str
    scale_constant: int
    tree_density: Union[float, None]
    patch_size: Union[list, tuple]
    ADB_mode: bool = False


# --------------Custom datatypes-------------- #
class ADBSporulationType(BaseType):
    def validate(self, value, context=None):
        assert isinstance(value, SporulationADB)


class InfectionType(BaseType):
    def validate(self, value, context=None):
        assert isinstance(value, Infection_dynamics)


class InfectionLtType(BaseType):
    def validate(self, value, context=None):
        assert isinstance(value, I_lt)


class ADBInfectionLtType(BaseType):
    def validate(self, value, context=None):
        assert isinstance(value, ADB_I_lt)


class ADBExposedLtType(BaseType):
    def validate(self, value, context=None):
        assert isinstance(value, ADB_E_lt)


class DispersalType(BaseType):
    def validate(self, value, context=None):
        assert isinstance(value, Dispersal)


class R0ConfigType(BaseType):
    def validate(self, value, context=None):
        assert isinstance(value, R0_tracker)


class RunTimeType(BaseType):
    def validate(self, value, context=None):
        assert isinstance(value, Generic_runtime) or isinstance(value, ADB_model_runtime)


class ADBrunTimeType(BaseType):
    def validate(self, value, context=None):
        assert isinstance(value, ADB_model_runtime)


class InitCondType(BaseType):
    def validate(self, value, context=None):
        assert isinstance(value, Initial_conditions)


class DomainConfType(BaseType):
    def validate(self, value, context=None):
        assert isinstance(value, DomainConfig)


class BCDconfType(BaseType):
    def validate(self, value, context=None):
        assert isinstance(value, Other_boundary_conditions)


# --------------Dispersal functions-------------- #
def ga_dispersal_func(dist: Union[np.ndarray, float], ell: float):
    """
    Gaussian dispersal model
    :param dist: distance of S-trees
    :param ell: dispersal scale parameter
    :return:
    """
    return np.exp(-(dist/ell) ** 2)


def pl_dispersal_func(dist: Union[np.ndarray, float], ell: tuple):
    """
    Inverse power law dispersal model
    :param dist: distance of S-trees
    :param ell: dispersal scale and shape parameters
    :return:
    """
    a, b = ell
    return (1 + dist/a)**(-b)


def mkdir_tmp_store():
    if os.path.exists(PATH_TO_TEMP):
        return None

    os.mkdir(PATH_TO_TEMP)
    return True


# --------------Setter functions-------------- #
def set_dispersal(model: str, ADB_mode: Optional[bool] = False, dispersal_param = None,
                  normed: Optional[bool] = True) -> Dispersal:
    """
    Set the form/config of dispersal
    :param normed: \beta^* i.e. using the auxiliary infectivity
    :param model: compartments used
    :param ADB_mode: ash dieback model
    :param dispersal_param: dispersal parameterization
    :return:
    """

    model_name = None
    dispersal_function = None
    assert model
    try:
        if model in ['gaussian', 'Gaussian', 'ga']:
            model_name = 'gaussian'
            dispersal_function = ga_dispersal_func
        elif 'power' in model and 'law' in model or 'pl' in model:
            model_name = 'power_law'
            dispersal_function = pl_dispersal_func
    except Exception:
        raise InvalidDispersalException(f'dispersal model is incorrectly defined: {model}')

    if model_name is None or dispersal_function is None:
        raise NotImplementedError

    if ADB_mode:
        # default ash dieback parameters
        if dispersal_param is not None:
            warn(message=f'Using default dispersal params for ADB: ga = {ELL_ADB_GA}, pl = {ELL_ADB_PL}')
        dispersal_param = (ELL_ADB_GA if model_name == 'gaussian' else ELL_ADB_PL)
    else:
        # generic SIR/SEIR compartmental model
        if dispersal_param is None:
            raise InvalidDispersalParamsException(f'Error! Required dispersal parameter for type {model_name}.')

        # validate dispersal parameter inputs
        if model_name == 'gaussian':
            try:
                assert type(dispersal_param) in [int, float, np.int64]
                assert 0 < dispersal_param < np.infty
            except Exception:
                raise InvalidDispersalParamsException(model_name)

        if model_name == 'power_law':
            try:
                assert type(dispersal_param) == tuple
                assert len(dispersal_param) == 2
                assert type(dispersal_param[0]) in [int, float, np.int64]
                assert type(dispersal_param[1]) in [int, float, np.int64]
                assert 0 < dispersal_param[1] < 10  # pl kernel shape param
                assert 0 < dispersal_param[0] < np.infty  # pl length-scale param

            except Exception:
                raise InvalidDispersalParamsException(model_name)

    # find normalisation factor
    if normed and model_name == 'gaussian':
        norm_factor = 1 / (2 * np.pi * (dispersal_param ** 2))
    elif normed and model_name == 'power_law':
        norm_factor = ((dispersal_param[1] - 1) * (dispersal_param[1] - 2)) / (2 * np.pi * dispersal_param[0] ** 2)
    else:
        norm_factor = 1

    return Dispersal(model_name, dispersal_param, norm_factor, dispersal_function, normed)


def set_infection_dynamics(compartments: str, beta_factor: float, ADB_mode: Optional[bool] = False,
                           pr_approx: Optional[bool] = True) -> Infection_dynamics:
    """
    Set the compartmentalised model
    :param ADB_mode: ash dieback implementation
    :param compartments: Compartments used in simulation. SIR and SEIR are configured
    :param beta_factor: infection pressure - a probability in [0, 1], with the dispersal constant factored out
    :param pr_approx: the numerical implementation used to combined statistically independent
                      transition probabilities in the model. If false, we will use the full Poisson construct.
                      **Nb. having full construct will prevent R0 contact-tracing **
    :return:
    """
    try:
        assert compartments in Compartmentalised_models
        if ADB_mode and compartments != 'SEIR':
            raise Exception('Expected type SEIR for ash dieback model')
        if not ADB_mode and compartments == 'SEIR':
            raise NotImplementedError('Not yet implemented type SEIR outside of ADB model')
    except Exception as e:
        raise e

    return Infection_dynamics(compartments, beta_factor, pr_approx)


def set_ADB_sporulation(sporulation_model: str) -> SporulationADB:
    """
    Set the sporulation model for the ash dieback model
    :param sporulation_model: type of sporulation model, i.e. constant, step, peaked
    :return:
    """
    try:
        assert sporulation_model in Sporulation_models.__dict__.keys()
    except Exception:
        raise NotImplementedError(f'Expected sporulation model in '
                                  f'{Sporulation_models.__dict__.keys()}, found {sporulation_model}')
    if sporulation_model == 'step':
        return SporulationADB('step', (6, 10), ('June', 'September'), ga_sd=None, normed=True, norm_factor=None)
    elif sporulation_model == 'peaked':
        return SporulationADB('peaked', (6, 10), ('June', 'September'), ga_sd=20, normed=True, norm_factor=None)


def set_ADB_runtime(years: int) -> ADB_model_runtime:
    """
    Set ADB SEIR runtime
    :param years:
    :return:
    """
    try:
        assert 0 < years < 30
    except Exception:
        raise Exception('Invalid ADB model runtime')

    start_date = datetime.datetime(years, 1, 1)

    return ADB_model_runtime(years, steps=years*365, start_year=2020, start_day=1, start_month=1,
                             end_day=1, end_month=1, end_year=2020+years, start_date=start_date)


def set_runtime(steps: int) -> Generic_runtime:
    """
    Set generic SIR/SEIR runtime
    :param steps:
    :return:
    """
    assert steps
    return Generic_runtime(steps, unit=1)


def set_initial_conditions(distribution: str, number_infected: int) -> Initial_conditions:
    """
    Simulation config at time t=0
    :param distribution: spatial distribution of infected trees
    :param number_infected: number of initially infected trees
    :return:
    """
    if distribution not in Initial_infected_distributions:
        raise Exception("Incorrect distribution! Choose between 'centralised' and 'random'")

    if not isinstance(number_infected, Number):
        raise Exception("Wrong number of infected")

    return Initial_conditions(distribution, number_infected)


def set_infectious_lt(distribution: str, life_time_parameter: int) -> I_lt:
    """
    Set the infectious life-time dynamics and parameters

    :param distribution:
    :param life_time_parameter:
    :return:
    """

    try:
        assert distribution in Infectious_life_time_distributions
    except Exception:
        raise NotImplementedError(f'Expected infectious lf in {Infectious_life_time_distributions}')

    return I_lt(distribution, life_time_parameter)


def get_ADB_lifetimes() -> Tuple[ADB_E_lt, ADB_I_lt]:
    exposed_lt = ADB_E_lt(exposed_lt_month=11, exposed_lt_day=1, exposed_lt_sd=14)
    infected_lt = ADB_I_lt(distribution='exp', years=5, steps=5 * 365)
    return exposed_lt, infected_lt


def set_R0_trace(active: bool = False, first_gen_only: bool = True, get_distances: Optional[bool] = False,
                 transition_times: Optional[bool] = False,  get_network: Optional[bool] = False) -> R0_tracker:
    """
    Config for contact-traced secondary-infections
    :param transition_times:
    :param get_network: plot a directed network graph
    :param active: if true, simulations will record R0
    :param first_gen_only: process only the first generation of infected ash
    :param get_distances: record the distances of induced secondary infections
    :return:
    """
    return R0_tracker(active, get_distances, first_gen_only, transition_times, get_network)


def set_domain_config(domain_type: str, scale_constant: int, tree_density: float, patch_size: Tuple[int],
                      ADB_mode: Optional[bool] = False) -> DomainConfig:

    if 10 <= scale_constant < 100:
        warn(message=f'Host units are currently set to one tree. '
                     f'A scale constant of {scale_constant} '
                     f'(m) is becoming unrealistic for single tree canopy cover')

    try:
        assert 0 < scale_constant < 100
    except Exception:
        raise Exception(f'Expected positive scale constant < 100m, found {scale_constant}')
    try:
        assert 0 <= tree_density <= 1.0
    except Exception:
        raise Exception(f'tree density should be float in [0.0, 1.0], found {tree_density}')
    try:
        assert domain_type in Domain_types
    except Exception:
        raise NotImplementedError(f'Expected domain in {Domain_types}, found {domain_type}')
    try:
        if ADB_mode:
            assert scale_constant == 5
    except Exception:
        raise Exception(f'ash dieback simulations configured for 5m only, found alpha = {scale_constant}')
    try:
        if domain_type == 'simple_square':
            assert patch_size[0] <= 2000 and patch_size[1] <= 2000
    except Exception:
        raise Exception(f'domain is too large, max size f{2000, 2000}')

    return DomainConfig(domain_type, scale_constant, tree_density, patch_size, ADB_mode)


def set_epidemic_parameters(rho: float, beta_factor: Union[float, int], dispersal: Dispersal,
                            sporulation: Optional[SporulationADB] = None) -> Epidemic_parameters:
    """

    :param rho:
    :param beta_factor:
    :param dispersal:
    :param sporulation:
    :return:
    """
    beta_pr = beta_factor * dispersal.norm_factor
    # todo refactor sporulation norm factor
    beta_pr = beta_pr * sporulation.norm_factor if sporulation else beta_pr
    return Epidemic_parameters(rho, beta_pr, dispersal.value)


# --------------Simulation Models-------------- #
class GenericSimulationConfig(Model):
    # For generic infection model
    sim_name: str = StringType(required=True)
    dispersal: Dispersal = DispersalType(required=True)
    infectious_lt: I_lt = InfectionLtType(required=True)
    runtime: Generic_runtime = RunTimeType(required=True)
    domain_config: DomainConfig = DomainConfType(required=True)
    initial_conditions: Initial_conditions = InitCondType(required=True)
    infection_dynamics: Infection_dynamics = InfectionType(required=True)
    R0_trace: Union[None, R0_tracker] = R0ConfigType(required=False, default=None)
    other_boundary_conditions: Other_boundary_conditions = BCDconfType(required=False,
                                                                       default=Other_boundary_conditions(False, False))
    exposed_lt = None
    sporulation = None


class ADBSimulationConfig(Model):
    # For parameterised ash dieback infection model
    dispersal: Dispersal = DispersalType(required=True)
    runtime: ADB_model_runtime = ADBrunTimeType(required=True)
    exposed_lt: ADB_E_lt = ADBExposedLtType(required=True)
    infectious_lt: ADB_I_lt = ADBInfectionLtType(required=True)
    sporulation: SporulationADB = ADBSporulationType(required=True)
    infection_dynamics: Infection_dynamics = InfectionType(required=True)
    domain_config: DomainConfig = DomainConfType(required=True)
    initial_conditions: Initial_conditions = InitCondType(required=True)
    R0_trace: Union[None, R0_tracker] = R0ConfigType(required=False, default=None)
    Other_boundary_conditions: Union[None, Other_boundary_conditions] = BCDconfType(required=False, default=None)


