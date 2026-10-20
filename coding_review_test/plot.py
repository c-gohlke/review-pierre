import numpy as np
import numpy.typing as npt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from coding_review_test.config import HORIZON
from coding_review_test.data import Data
from coding_review_test.optimisation import Schedule

# Categorical colours in a fixed order, and a neutral ink for the price, which is alone in its panel
LOAD, PV, BATTERY, GRID = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
INK = "#52514e"


def _hourly_steps(values: npt.NDArray[np.float64]) -> tuple[npt.NDArray[np.int_], npt.NDArray[np.float64]]:
    """Repeat the last hourly value so that the step line also covers the last hour."""
    return np.arange(HORIZON + 1), np.append(values, values[-1])


def plot(data: Data, schedule: Schedule, name: str) -> None:
    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=("Power [kW]", "Price [€/kWh]", "State of energy [kWh]"),
    )
    for label, values, color in [
        ("Load", data.load, LOAD),
        ("PV", data.pv, PV),
        ("Battery (+ charge)", schedule.battery_power, BATTERY),
        ("Grid (+ import)", schedule.grid_power, GRID),
    ]:
        x, y = _hourly_steps(values)
        fig.add_trace(go.Scatter(x=x, y=y, name=label, line={"shape": "hv", "color": color, "width": 2}), row=1, col=1)

    x, y = _hourly_steps(data.prices)
    fig.add_trace(
        go.Scatter(x=x, y=y, name="Price", showlegend=False, line={"shape": "hv", "color": INK, "width": 2}),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=np.arange(HORIZON + 1),
            y=schedule.soe,
            name="State of energy",
            showlegend=False,
            mode="lines+markers",
            line={"color": BATTERY, "width": 2},
            marker={"size": 8},
        ),
        row=3,
        col=1,
    )

    fig.update_xaxes(title_text="Time [h]", row=3, col=1)
    fig.update_layout(
        title=f"{name}: total cost {schedule.cost:.2f}€", template="plotly_white", hovermode="x unified", height=800
    )
    fig.show()
