from dataclasses import dataclass

import cvxpy as cp
import numpy as np
import numpy.typing as npt

from coding_review_test.config import (
    BATTERY_CAPACITY,
    EFFICIENCY,
    HORIZON,
    INIT_SOE,
    MAX_POWER,
    TIMESTEP_SIZE,
)
from coding_review_test.data import Data


@dataclass
class Schedule:
    battery_power: npt.NDArray[np.float64]  # kW, positive = charging
    grid_power: npt.NDArray[np.float64]  # kW, positive = import
    soe: npt.NDArray[np.float64]  # kWh, HORIZON + 1 values
    cost: float  # €


def optimise(data: Data) -> Schedule:
    """Minimise the electricity bill of a household with load, PV and a battery."""
    charge = cp.Variable(HORIZON, nonneg=True)
    discharge = cp.Variable(HORIZON, nonneg=True)
    soe = cp.Variable(HORIZON + 1)
    grid_power = data.load - data.pv + charge - discharge

    constraints = {
        "initial_soe": soe[0] == INIT_SOE,
        "transition_function": soe[1:] == soe[:-1] + (charge - discharge) * EFFICIENCY * TIMESTEP_SIZE,
        "min_soe": soe >= 0,
        "max_soe": soe <= BATTERY_CAPACITY,
        "max_charge": charge <= MAX_POWER,
        "max_discharge": discharge <= MAX_POWER,
    }
    cost = data.prices @ grid_power * TIMESTEP_SIZE
    problem = cp.Problem(cp.Minimize(cost), list(constraints.values()))
    problem.solve()
    if problem.status != cp.OPTIMAL:
        raise RuntimeError(f"Optimisation failed: {problem.status}")

    return Schedule(
        battery_power=charge.value - discharge.value,
        grid_power=grid_power.value,
        soe=soe.value,
        cost=float(problem.value),
    )
