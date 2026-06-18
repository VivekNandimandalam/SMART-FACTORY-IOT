import argparse
import threading
from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parent))

from sensor_humidity import run as run_humidity
from sensor_power import run as run_power
from sensor_pressure import run as run_pressure
from sensor_temperature import run as run_temperature
from sensor_vibration import run as run_vibration


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rate", type=float, default=5)
    parser.add_argument("--anomaly-chance", type=float, default=0.05)
    arguments = parser.parse_args()

    sensor_threads = [
        threading.Thread(target=run_vibration, args=(arguments.rate, arguments.anomaly_chance), daemon=True),
        threading.Thread(target=run_temperature, args=(arguments.rate, arguments.anomaly_chance), daemon=True),
        threading.Thread(target=run_pressure, args=(arguments.rate, arguments.anomaly_chance), daemon=True),
        threading.Thread(target=run_humidity, args=(arguments.rate, arguments.anomaly_chance), daemon=True),
        threading.Thread(target=run_power, args=(arguments.rate, arguments.anomaly_chance), daemon=True),
    ]

    for thread in sensor_threads:
        thread.start()

    print("All 5 sensors running. Press Ctrl+C to stop.")
    stop_event = threading.Event()
    try:
        stop_event.wait()
    except KeyboardInterrupt:
        print("Sensors stopped.")


if __name__ == "__main__":
    main()
