import numpy as np
import numpy.typing as npt

from coding_review_test.config import BATTERY_CAPACITY, EFFICIENCY, INIT_SOE, MAX_POWER, TIMESTEP_SIZE
from coding_review_test.data import Data
from coding_review_test.optimisation import Schedule


def schedule_from_battery_power(
    data: Data, battery_power: npt.NDArray[np.float64], soe: npt.NDArray[np.float64]
) -> Schedule:
    grid_power = data.load - data.pv + battery_power
    cost = float(np.sum(data.prices * grid_power * TIMESTEP_SIZE))
    return Schedule(battery_power, grid_power, soe, cost)


def no_battery(data: Data) -> Schedule:
    return schedule_from_battery_power(data, np.zeros_like(data.load), np.full(len(data.load) + 1, INIT_SOE))


def self_consumption(data: Data) -> Schedule:
    """Charge the battery with PV surplus, discharge it to cover the remaining load."""
    soe = [INIT_SOE]
    battery_power = []
    for surplus in data.pv - data.load:
        if surplus > 0:
            max_charge = (BATTERY_CAPACITY - soe[-1]) / EFFICIENCY / TIMESTEP_SIZE
            power = min(surplus, MAX_POWER, max_charge)
            soe.append(soe[-1] + power * EFFICIENCY * TIMESTEP_SIZE)
        else:
            max_discharge = soe[-1] * EFFICIENCY / TIMESTEP_SIZE
            power = max(surplus, -MAX_POWER, -max_discharge)
            soe.append(soe[-1] + power / EFFICIENCY * TIMESTEP_SIZE)
        battery_power.append(power)
    return schedule_from_battery_power(data, np.array(battery_power), np.array(soe))
