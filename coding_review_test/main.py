import argparse
from datetime import date

from coding_review_test.data import generate_data, load_data, load_prices
from coding_review_test.optimisation import optimise
from coding_review_test.plot import plot
from coding_review_test.solutions import no_battery, self_consumption


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--data", help="CSV with UTC timestamps and load_kw / pv_kw columns. Dummy data if omitted.")
    parser.add_argument("--prices", default="data/prices.csv", help="CSV with UTC timestamps and hourly prices")
    parser.add_argument("--day", type=date.fromisoformat, default=date(2024, 3, 27))
    args = parser.parse_args()

    prices = load_prices(args.prices, args.day)
    data = load_data(args.data, args.day, prices) if args.data else generate_data(args.seed, prices)
    for solution in (no_battery, self_consumption, optimise):
        name = solution.__name__
        schedule = solution(data)
        plot(data, schedule, name)
        print(f"{name:>20}: {schedule.cost:6.2f}€")


if __name__ == "__main__":
    main()
