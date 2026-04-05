import pandas as pd
import logging
import os

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s",
    handlers=[
        logging.FileHandler("logs/pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def calculate_bmi(weight, height):
    #Calculate BMI given weight in kg and height in cm.
    return weight / (height / 100) ** 2

if __name__ == "__main__":
    df = pd.read_csv("data/applicants.csv")
    df["bmi"] = df.apply(lambda row: calculate_bmi(row["weight"], row["height"]), axis=1)
    df["bmi"] = df["bmi"].round(2)
    df.to_csv("data/applicants.csv", index=False)
    logger.info(f"BMI calculated for {len(df)} records")
    logger.info(df[["applicationID", "height", "weight", "bmi"]].head().to_string())