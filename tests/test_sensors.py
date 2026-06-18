from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "sensors"))

from sensor_humidity import generate_humidity
from sensor_power import generate_power
from sensor_pressure import generate_pressure
from sensor_temperature import generate_temperature
from sensor_vibration import generate_vibration


def test_vibration_normal():
    data = generate_vibration(anomaly=False)
    assert data["sensor_type"] == "vibration"
    assert 0.5 <= data["value"] <= 10.0
    assert data["unit"] == "mm/s"


def test_vibration_anomaly():
    data = generate_vibration(anomaly=True)
    assert data["value"] >= 15.0


def test_temperature_normal():
    data = generate_temperature(anomaly=False)
    assert 40.0 <= data["value"] <= 75.0


def test_pressure_anomaly():
    data = generate_pressure(anomaly=True)
    assert data["value"] < 20.0


def test_humidity_anomaly():
    data = generate_humidity(anomaly=True)
    assert data["value"] >= 80.0


def test_power_normal():
    data = generate_power(anomaly=False)
    assert 20.0 <= data["value"] <= 75.0
