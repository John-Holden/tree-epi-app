import numpy as np
from typing import Tuple, Optional, Union, List
from py_src.back_end.epidemic_models.utils.common_helpers import get_initial_host_number
from py_src.params_and_config import (DomainConfig, Initial_conditions, I_lt,
                               Infectious_life_time_distributions, Initial_infected_distributions,
                               R0_tracker, Epidemic_parameters, Infection_dynamics, Dispersal)


def ij_distance(i: tuple, j: Union[tuple, list]) -> np.ndarray:
    """
    Find the distance between site i : (x, y) and coordinates j : (x1,...xN), (y1,...,yN)
    """
    if len(j[0]) > 0:
        return np.sqrt((i[0] - j[0]) ** 2 + (i[1] - j[1]) ** 2)

    return np.array([0])


def set_I_lt(infect_lt: I_lt, I_num: int, t: int) -> np.ndarray:
    """
    Set the infectious lifetime of a tree, conditioned on a type of distribution and scale parameter
    :param infect_lt: config
    :param I_num: the number of infected trees
    :param t:
    :return:
    """
    try:
        assert infect_lt.distribution in Infectious_life_time_distributions
        if infect_lt.distribution == 'exp':
            return np.random.exponential(scale=infect_lt.steps, size=I_num).astype(int) + t
        elif infect_lt.distribution == 'step':
            return np.ones(I_num).astype(int) + infect_lt.steps + t

    except Exception:
        raise NotImplementedError(f'Unexpected infectious life-time distribution: {infect_lt.distribution}')


def set_I(init_cond: Initial_conditions, patch_size: tuple, infect_lt: I_lt) -> List[np.ndarray]:
    """
    Set the infectious tree locations, I_row, I_col, and infectious lifetimes I_lt
    :param infect_lt:
    :param init_cond: the model initial conditions
    :param patch_size: the domain size
    :return: a tuple of Infected row and column locations, and lifetimes
    """

    init_n_infected = init_cond.initially_infected
    Lx, Ly = patch_size
    I_row, I_col = [], []
    if init_cond.distribution not in Initial_infected_distributions:
        raise Exception(f'Unexpected distribution: {init_cond.distribution}')
    try:
        if init_cond.distribution == 'random':
            # set n initially infected sites throughout the domain
            set_epi_c = 0
            while set_epi_c < init_n_infected:
                row, col = np.random.randint(0, Lx - 1), np.random.randint(0, Ly - 1)
                for i, j in zip(I_row, I_col):
                    if row == i and col == j:
                        break
                else:
                    I_row.append(row)
                    I_col.append(col)
                    set_epi_c += 1

        elif init_cond.distribution == 'centralised':
            # Populate a small square of infected trees in the center of the domain
            xarr, yarr = np.meshgrid(np.arange(0, Ly, 1), np.arange(0, Lx, 1))
            dist_arr = np.sqrt((xarr - Lx / 2) ** 2 + (yarr - Ly / 2) ** 2)
            domain_center = np.where(dist_arr < np.sqrt(init_n_infected) + 20)
            rand = np.random.permutation(np.arange(0, len(domain_center[0]), 1))
            I_row = [i for i in domain_center[0][rand[:init_n_infected]]]
            I_col = [i for i in domain_center[1][rand[:init_n_infected]]]

        assert len(I_row) == len(I_col)
        assert len(I_row) == init_n_infected

        return [np.array(I_row).astype(int), np.array(I_col).astype(int), set_I_lt(infect_lt, len(I_row), t=0)]

    except Exception as e:
        raise e


def set_S(rho: float, patch_size: tuple) -> List[np.ndarray]:
    """
    Set susceptible trees
    """
    S = np.zeros(shape=patch_size)
    S_tree_number = int(rho * patch_size[0] * patch_size[1])
    tree = 0
    try:
        while tree < S_tree_number:  # seed exact number in random locations
            rand_row = np.random.randint(0, patch_size[0])
            rand_col = np.random.randint(0, patch_size[1])

            if not S[rand_row, rand_col]:
                S[rand_row, rand_col] = 1
                tree += 1

        S = np.where(S)
        assert len(S[0]) == S_tree_number

    except Exception as e:
        raise e

    return [S[0].astype(int), S[1].astype(int)]


def set_SIR(domain_config: DomainConfig, initial_conditions: Initial_conditions, infect_lt: I_lt) \
        -> Tuple[List[np.ndarray], List[np.ndarray], List[np.ndarray]]:
    """
    Set the fields, S, I and R
    :param infect_lt:
    :param initial_conditions:
    :param domain_config:
    :return: a tuple of lists containing numpy arrays, e.g. [S_row, S_col] (where S_col, S_row are numpy arrays)
    """

    def remove_I_from_S(S_field: List[np.ndarray], I_field: List[np.ndarray]) -> List[np.ndarray]:
        S_cleaned = ([], [])
        for S_row, S_col in zip(S_field[0], S_field[1]):
            for I_row, I_col in zip(I_field[0], I_field[1]):
                if I_row == S_row and I_col == S_col:
                    break
            else:
                S_cleaned[0].append(S_row)
                S_cleaned[1].append(S_col)

        assert len(S_cleaned[0]) <= len(S_field[0])
        return [np.array(S_cleaned[0]), np.array(S_cleaned[1])]

    init_host_number = get_initial_host_number(domain_config.patch_size, domain_config.tree_density)
    if init_host_number < initial_conditions.initially_infected:
        raise Exception('The number of trees is smaller than the number of infected trees at t.')

    I = set_I(initial_conditions, domain_config.patch_size, infect_lt)
    S = set_S(domain_config.tree_density, domain_config.patch_size)
    S = remove_I_from_S(S, I)
    R = [np.array([]), np.array([])]  # Removed trees, row, col
    return S, I, R


def set_SEIR(domain_config: DomainConfig, initial_conditions: Initial_conditions, infect_lt: I_lt):
    """
    A thin wrapper that initialises the SEIR fields, where E assumes the initially infected
    :param domain_config:
    :param initial_conditions:
    :param infect_lt:
    :return:
    """
    S, E, I = set_SIR(domain_config, initial_conditions, infect_lt)
    R = [[], [], []]  # Removed trees
    return S, E, I, R


def set_R0_trace_struct(R0_config: R0_tracker, infection_dynamics: Infection_dynamics,
                        I: List[np.ndarray]) -> dict:
    """
    A record the secondary infections of the form "site_i_j : {neighbours_infected: N,....}"

    :param infection_dynamics:
    :param R0_config:
    :param I: the initial infectious indices
    :return:
    """
    if not R0_config.active or not infection_dynamics.pr_approx:
        return {}

    R0_hist = {}
    for i in range(len(I[0])):
        site = f'{I[0][i]}.{I[1][i]}'

        R0_hist[site] = {'time_infected': 0, 'num_nn_infected': 0, 'generation_infected': 0}
        if R0_config.get_distance:
            # append and empty list to store infection distances
            R0_hist[site]['distances'] = []
        if R0_config.transition_times:
            R0_hist[site]['transition_times'] = []
        if R0_config.get_network:
            R0_hist[site]['nn_infected'] = []

    return R0_hist


def new_infections(epidemic_parameters: Epidemic_parameters,
                   domain_config: DomainConfig, dispersal: Dispersal,
                   S: List[np.ndarray], I: List[np.ndarray], t: int, inf_lt: I_lt,
                   prob_approx: bool, max_gen_bcd: Optional[float] = None,
                   phi: Optional[float] = 1) -> Tuple[Tuple, List]:
    """
    Return a list of indices of all the newly infected trees, along with the max infectious order AND
    remove index from susceptible
    :param t: current time-step
    :param dispersal:
    :param domain_config:
    :param phi:
    :param max_gen_bcd:
    :param epidemic_parameters:
    :param I: indices of infected trees
    :param S: indices of susceptible trees
    :param prob_approx: implement the transition probability assumption, or use the full Poisson construct, i.e.
    :param inf_lt:
                        combing n statistically independent events according to the exclusion principle
    :return: (new_infected_row, new_infected_col, infect_lt), (new_S_transition_indices)
    """
    if max_gen_bcd is not None:
        raise NotImplementedError('Max generation boundary condition')

    if not (epidemic_parameters.beta_pr and S[0].any()):
        return ([], [], []), []

    if prob_approx:
        # return pr_approx(S, I,  phi, epidemic_parameters)
        raise NotImplementedError

    return pr_full(S, I, t, phi, epidemic_parameters, domain_config, dispersal, inf_lt)


def pr_approx(S, I, R0_struct, phi, epidemic_parameters):
    raise NotImplementedError


def pr_full(S: List[np.ndarray], I: List[np.ndarray],
            t: int, phi: float, epidemic_parameters: Epidemic_parameters, domain_config: DomainConfig,
            dispersal: Dispersal, infectious_life_time: I_lt) -> Tuple[Tuple, List]:
    """
    Compute new transitions through the full Poisson construct
    :param I: infected trees (row, col, life-time
    :param S: susceptible trees (row, col)
    :param t: current time-step
    :param phi: sporulation function at time-step t
    :param epidemic_parameters: struct holding epidemic parameters
    :param domain_config: struct holding domain config info
    :param dispersal: struct holding dispersal info
    :param infectious_life_time: struct holding infectious lifetime info
    :return: new infected tree locations and indices to remove from S
    """

    def S_transition(single_S_tree: Tuple[int, int], I_trees: List[np.ndarray], phi_t: float,
                     epi_parameters: Epidemic_parameters, domain_conf: DomainConfig, disp: Dispersal) -> bool:
        """Get the probability of susceptible tree becoming infected due to n infected trees"""

        distance = ij_distance(single_S_tree, I_trees) * domain_conf.scale_constant  # (m)
        # probability of a susceptible tree transitioning to the infected compartment
        pr_S_to_I = phi_t * epi_parameters.beta_pr * disp.function(distance, epidemic_parameters.ell)
        # probability of susceptible tree remaining susceptible due to n infected trees
        pr_S_to_S = 1 - pr_S_to_I
        # probability of susceptible tree transitioning into an infected due under the influence of n infected trees
        pr_S_to_I = 1 - np.cumprod(pr_S_to_S)[-1]
        # compare pr_S_to_I to randomly drawn samples
        return np.random.uniform(low=0, high=1) < pr_S_to_I

    delete_S_ind = []
    new_I_row, new_I_col = [], []
    for ith_tree in range(len(S[0])):
        # for each exposed/infected site, find secondary infections
        S_tree = (S[0][ith_tree], S[1][ith_tree])  # (x, y)
        if S_transition(S_tree, I, phi, epidemic_parameters, domain_config, dispersal):
            try:
                # append the newly exposed/infected list
                new_I_row.append(S_tree[0])
                new_I_col.append(S_tree[1])
                delete_S_ind.append(ith_tree)  # store list of infected tree to delete later
            except Exception as e:
                raise e

    infected_lt = set_I_lt(infectious_life_time, len(new_I_row), t)
    return (new_I_row, new_I_col, infected_lt), delete_S_ind

