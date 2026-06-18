from copy import deepcopy


THRESHOLDS = {
    "vibration": {"max": 15.0, "unit": "mm/s", "alert": "Bearing failure risk"},
    "temperature": {"max": 85.0, "unit": "celsius", "alert": "Motor overheating"},
    "pressure": {"min": 20.0, "unit": "bar", "alert": "Hydraulic leak detected"},
    "humidity": {"max": 80.0, "unit": "percent", "alert": "Corrosion risk"},
    "power": {"max": 90.0, "unit": "kW", "alert": "Power spike - possible fault"},
}


reading_history = {}


def process_reading(data):
    """Process a single sensor reading and add anomaly metadata."""
    result = deepcopy(data)
    result["anomaly"] = False
    result["alert"] = None
    result["processed_by"] = "fog_node"

    sensor_type = data.get("sensor_type")
    value = data.get("value")
    sensor_id = data.get("sensor_id")

    if sensor_type not in THRESHOLDS or value is None:
        return result

    threshold = THRESHOLDS[sensor_type]

    if "max" in threshold and value > threshold["max"]:
        result["anomaly"] = True
        result["alert"] = threshold["alert"]
        result["severity"] = "HIGH"

    if "min" in threshold and value < threshold["min"]:
        result["anomaly"] = True
        result["alert"] = threshold["alert"]
        result["severity"] = "HIGH"

    if sensor_id not in reading_history:
        reading_history[sensor_id] = []

    reading_history[sensor_id].append(value)
    reading_history[sensor_id] = reading_history[sensor_id][-5:]

    history = reading_history[sensor_id]
    if len(history) >= 3 and history[-1] > history[-2] > history[-3]:
        if "max" in threshold and value > threshold["max"] * 0.85:
            result["trend"] = "RISING"
            if not result["anomaly"]:
                result["alert"] = f"Warning: {sensor_type} trending toward threshold"
                result["severity"] = "MEDIUM"

    return result
