from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "fog_node"))

from processor import process_reading, reading_history


def setup_function(function):
    reading_history.clear()


def test_vibration_anomaly_detected():
    data = {"sensor_id": "VIB_001", "sensor_type": "vibration", "value": 20.0, "unit": "mm/s"}
    result = process_reading(data)
    assert result["anomaly"] is True
    assert result["alert"] is not None


def test_normal_reading_no_anomaly():
    data = {"sensor_id": "TEMP_001", "sensor_type": "temperature", "value": 55.0, "unit": "celsius"}
    result = process_reading(data)
    assert result["anomaly"] is False


def test_processed_by_fog():
    data = {"sensor_id": "HUM_001", "sensor_type": "humidity", "value": 40.0, "unit": "percent"}
    result = process_reading(data)
    assert result["processed_by"] == "fog_node"


def test_rising_trend_warning():
    readings = [
        {"sensor_id": "PWR_001", "sensor_type": "power", "value": 70.0, "unit": "kW"},
        {"sensor_id": "PWR_001", "sensor_type": "power", "value": 75.0, "unit": "kW"},
        {"sensor_id": "PWR_001", "sensor_type": "power", "value": 80.0, "unit": "kW"},
    ]

    results = [process_reading(item) for item in readings]
    assert results[-1].get("trend") == "RISING"
    assert results[-1].get("alert") is not None
