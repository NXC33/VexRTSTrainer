import csv
import os
import matplotlib.pyplot as plt

RESULTS_FILE = "reaction_results.csv"
ROLLING_WINDOW = 10  # last N attempts for rolling average


def load_times():
    times = []

    if not os.path.exists(RESULTS_FILE):
        print("No reaction_results.csv found.")
        return times

    with open(RESULTS_FILE, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                times.append(float(row["reaction_time"]))
            except (KeyError, ValueError):
                continue

    return times


def rolling_average(data, window):
    averages = []
    for i in range(len(data)):
        start = max(0, i - window + 1)
        window_data = data[start:i + 1]
        averages.append(sum(window_data) / len(window_data))
    return averages


def plot_times(times):
    attempts = list(range(1, len(times) + 1))
    rolling = rolling_average(times, ROLLING_WINDOW)

    plt.figure(figsize=(10, 5))

    plt.plot(attempts, times, label="Reaction Time", alpha=0.6)
    plt.plot(attempts, rolling, label=f"Rolling Avg ({ROLLING_WINDOW})", linewidth=2)

    plt.xlabel("Attempt")
    plt.ylabel("Reaction Time (seconds)")
    plt.title("VEX Score Recognition Reaction Time")
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()


def plot_histogram(times):
    plt.figure(figsize=(8, 4))
    plt.hist(times, bins=20)
    plt.xlabel("Reaction Time (seconds)")
    plt.ylabel("Frequency")
    plt.title("Reaction Time Distribution")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def summary(times):
    print("Attempts:", len(times))
    print("Best time:", f"{min(times):.3f}s")
    print("Average time:", f"{sum(times) / len(times):.3f}s")


if __name__ == "__main__":
    times = load_times()

    if not times:
        print("No data to visualize.")
    else:
        summary(times)
        plot_times(times)
        plot_histogram(times)
