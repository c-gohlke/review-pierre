import argparse
from datetime import date

from coding_review_test.data import generate_data, load_prices
from coding_review_test.optimisation import optimise
from coding_review_test.plot import plot
from coding_review_test.solutions import no_battery, self_consumption


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--prices", default="data/prices.csv", help="CSV with UTC timestamps and hourly prices")
    parser.add_argument("--day", type=date.fromisoformat, default=date(2024, 3, 27))
    args = parser.parse_args()

    data = generate_data(args.seed, load_prices(args.prices, args.day))
    for solution in (no_battery, self_consumption, optimise):
        name = solution.__name__
        schedule = solution(data)
        plot(data, schedule, name)
        print(f"{name:>20}: {schedule.cost:6.2f}€")


if __name__ == "__main__":
    main()
