import pandas as pd
import os
import logging
from datetime import datetime, timezone

LOG_PATH = "logs/observability.csv"
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