from dataclasses import dataclass
from datetime import date

import numpy as np
import numpy.typing as npt
import pandas as pd

from coding_review_test.config import HORIZON, PV_PEAK


@dataclass
class Data:
    load: npt.NDArray[np.float64]  # kW
    pv: npt.NDArray[np.float64]  # kW
    prices: npt.NDArray[np.float64]  # €/kWh


def generate_data(seed: int, prices: npt.NDArray[np.float64]) -> Data:
    rng = np.random.default_rng(seed)
    hours = np.arange(HORIZON)

    # Base load with a morning and an evening peak
    load = 0.4 + 0.8 * np.exp(-((hours - 7) ** 2) / 4) + 1.5 * np.exp(-((hours - 19) ** 2) / 6)
    load = np.maximum(load + rng.normal(0, 0.1, HORIZON), 0)

    # Bell-shaped PV production between 6h and 20h
    pv = PV_PEAK * np.maximum(np.sin(np.pi * (hours - 6) / 14), 0)
    pv = np.maximum(pv * rng.uniform(0.6, 1.0, HORIZON), 0)

    return Data(load=load, pv=pv, prices=prices)


def load_prices(path: str, day: date) -> npt.NDArray[np.float64]:
    """Hourly prices of the UTC `day`."""
    prices = pd.read_csv(path, index_col="timestamp", parse_dates=["timestamp"])["price_eur_per_kwh"]
    if str(prices.index.tz) != "UTC":
        raise ValueError(f"Expected UTC timestamps in {path}, got {prices.index.tz}")
    day_prices = prices[prices.index.date == day]
    if len(day_prices) != HORIZON:
        raise ValueError(f"Expected {HORIZON} hourly prices for {day}, got {len(day_prices)}")
    return day_prices.to_numpy()
