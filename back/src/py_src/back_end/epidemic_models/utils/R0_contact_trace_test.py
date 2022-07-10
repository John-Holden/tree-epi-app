from py_src.params_and_config import set_R0_trace, set_initial_conditions, set_infectious_lt, set_infection_dynamics
from py_src.back_end.epidemic_models.utils.dynamics_helpers import set_R0_trace_struct, set_I


def test_init_R0_struct():
    init_dist = set_initial_conditions(distribution='random', number_infected=10)
    inf_lt = set_infectious_lt('exp', life_time_parameter=10)
    R0_config = set_R0_trace(active=False, transition_times=[0])

    I = set_I(init_dist, (10, 10), inf_lt)
    infection_dynamics = set_infection_dynamics('SIR', beta_factor=1, ADB_mode=False)
    R0_struct = set_R0_trace_struct(R0_config, infection_dynamics, I)
    assert not R0_struct

    init_dist = set_initial_conditions(distribution='random', number_infected=10)
    inf_lt = set_infectious_lt('exp', life_time_parameter=10)
    R0_config = set_R0_trace(active=True, transition_times=[0])

    I = set_I(init_dist, (10, 10), inf_lt)
    infection_dynamics = set_infection_dynamics('SIR', beta_factor=1, ADB_mode=False)
    R0_struct = set_R0_trace_struct(R0_config, infection_dynamics, I)
    assert len(R0_struct.keys()) == init_dist.initially_infected






