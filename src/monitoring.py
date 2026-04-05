import pandas as pd
import os
import logging
from datetime import datetime, timezone

LOG_PATH = "logs/predictions.csv"

# Training baseline stats for drift detection
TRAINING_BMI_MEAN = 25.5
TRAINING_BMI_STD = 4.5
DRIFT_THRESHOLD = 2.0

# Expected input ranges based on training data distribution
INPUT_RANGES = {
    "age": (18, 75),
    "height": (140, 210),
    "weight": (45, 200),
}

logger = logging.getLogger("uvicorn")


def log_prediction(gender, age, height, weight, bmi, quote):
    os.makedirs("logs", exist_ok=True)
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "gender": gender,
        "age": age,
        "height": height,
        "weight": weight,
        "bmi": bmi,
        "quote": quote
    }
    df = pd.DataFrame([record])
    df.to_csv(
        LOG_PATH,
        mode="a",
        header=not os.path.exists(LOG_PATH),
        index=False)
    _check_input_ranges(age, height, weight)
    _check_drift()


def _check_input_ranges(age, height, weight):
    # Warn if incoming inputs are outside training distribution
    for feature, (low, high) in INPUT_RANGES.items():
        value = {"age": age, "height": height, "weight": weight}[feature]
        if not (low <= value <= high):
            logger.warning(f"Input out of expected range: {
                           feature}={value} (expected {low}-{high})")


def _check_drift():
    # Compare recent prediction BMI mean against training baseline
    # In production this would be replaced with Evidently AI for automated drift reports
    # and Grafana/Prometheus for real-time dashboards
    logs = get_prediction_logs()
    if len(logs) < 50:
        return
    recent_mean = logs["bmi"].tail(50).mean()
    drift = abs(recent_mean - TRAINING_BMI_MEAN)
    if drift > DRIFT_THRESHOLD:
        logger.warning(
            f"BMI drift detected: recent mean={
                recent_mean:.2f}, training mean={TRAINING_BMI_MEAN}, drift={
                drift:.2f}")


def get_prediction_logs():
    if not os.path.exists(LOG_PATH):
        return pd.DataFrame()
    return pd.read_csv(LOG_PATH)
