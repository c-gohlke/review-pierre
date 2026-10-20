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
    load = 0.3 + 1.0 * np.exp(-((hours - 8) ** 2) / 3) + 1.8 * np.exp(-((hours - 20) ** 2) / 5)
    load = np.maximum(load + rng.normal(0, 0.1, HORIZON), 0)

    # Bell-shaped PV production between 6h and 20h
    pv = PV_PEAK * np.maximum(np.sin(np.pi * (hours - 7) / 12), 0)
    pv = np.maximum(pv * rng.uniform(0.6, 1.0, HORIZON), 0)

    return Data(load=load, pv=pv, prices=prices)


def fill_missing(measurements: pd.DataFrame, freq: pd.Timedelta, max_gap: pd.Timedelta) -> pd.DataFrame:
    """Linearly interpolate gaps of at most `max_gap`, leave longer gaps as NaN.

    Longer gaps usually mean the meter was offline, and interpolating over them would invent data.
    """
    regular = measurements.asfreq(freq)
    return regular.interpolate(method="time", limit=max_gap // freq, limit_area="inside")


def load_measurements(path: str, day: date | str) -> pd.DataFrame:
    measurements = pd.read_csv(path, index_col="timestamp", parse_dates=["timestamp"])
    measurements.index = measurements.index.tz_convert("Europe/Brussels").tz_localize(None)

    # Make sure there are no negative values
    clipped_pv = []
    for _, row in measurements.iterrows():
        clipped_pv.append(max(row["pv_kw"], 0))
    for timestamp in measurements.index:
        negative = measurements[measurements["pv_kw"] < 0]
        if timestamp in negative.index:
            row = measurements.loc[timestamp]
            row["pv_kw"] = 0

    measurements = measurements[measurements.index.date == day]
    return measurements.resample("1h").mean()


def load_data(path: str, day: date | str, prices: npt.NDArray[np.float64]) -> Data:
    measurements = load_measurements(path, day)
    if len(measurements) != HORIZON:
        raise ValueError(f"Expected {HORIZON} hourly values for {day}, got {len(measurements)}")
    return Data(load=measurements["load_kw"].to_numpy(), pv=measurements["pv_kw"].to_numpy(), prices=prices)


def load_prices(path: str, day: date) -> npt.NDArray[np.float64]:
    """Hourly prices of the UTC `day`."""
    prices = pd.read_csv(path, index_col="timestamp", parse_dates=["timestamp"])["price_eur_per_kwh"]
    if str(prices.index.tz) != "UTC":
        raise ValueError(f"Expected UTC timestamps in {path}, got {prices.index.tz}")
    day_prices = prices[prices.index.date == day]
    if len(day_prices) != HORIZON:
        raise ValueError(f"Expected {HORIZON} hourly prices for {day}, got {len(day_prices)}")
    return day_prices.to_numpy()
