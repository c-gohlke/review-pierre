# coding-review-test

Minimal example: generate dummy household load + PV data, optimise a battery schedule with a linear program
(minimise the cost of the power exchanged with the grid) using hourly prices from a CSV file, and plot the result.

```bash
uv run python -m coding_review_test.main --seed 0 --day 2024-03-27
```

- `config.py` — battery and tariff parameters
- `data.py` — dummy load and PV profiles, prices loaded from a CSV file
- `data/prices.csv` — hourly prices (UTC timestamps)
- `optimisation.py` — LP formulation solved with `cvxpy`
- `solutions.py` — baseline solutions to compare the optimisation against
- `plot.py` — power and state-of-energy schedule

## Code review exercise

The exercise has two parts: first get to know the code base, then review a pull request on it.

### Part 1: check out the repo and read it

You need `git` and [`uv`](https://docs.astral.sh/uv/getting-started/installation/).

```bash
git clone <repository-url>
cd <repository>
uv sync
uv run python -m coding_review_test.main --seed 0 --day 2024-03-27
```

The schedules open in your browser. Then read through the code (see the file overview above) and walk us through it:

- What data goes in, and where does it come from?
- What problem does the optimisation solve, and what does the resulting schedule look like?

### Part 2: review the pull request

Check out the open pull request *Load consumption/PV data from the csv file*:

```bash
git checkout add-measured-data
uv run python -m coding_review_test.main --data data/measurements.csv --day 2024-03-27
```

Go through the changes with `git diff main...HEAD` or in the GitHub *Files changed* tab, and review them as if a
colleague had asked you for feedback. Feel free to run the code, add print statements or try other inputs. You don't
need to fix anything.

Comment on anything you would raise in a real review, for example:

- Does the code do what the pull request says it does? Are there inputs for which it is wrong?
- Is it easy to read and maintain?
- Does every change belong in this pull request?
- Is there anything you would ask the author about?

For each comment, say how important you think it is: must fix before merging, should fix, or minor/optional.
