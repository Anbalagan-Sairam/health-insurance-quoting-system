import numpy as np
import pandas as pd
import os
import logging

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

logger.info("Data generation pipeline starting...")

np.random.seed(42)
N = 2000

genders = np.random.choice(["Male", "Female"], N)
ages = np.random.randint(18, 75, N)

heights = np.where(
    genders == "Male",
    np.random.normal(175.6, 7, N),
    np.random.normal(162.2, 6, N)
)
heights = np.clip(heights, 140, 210).round(1)

weights = np.where(
    genders == "Male",
    np.random.normal(81, 13, N),
    np.random.normal(66.8, 11, N)
)
height_effect = (heights - heights.mean()) * 0.10
weights = np.clip(weights + height_effect, 45, 200).round(1)

df = pd.DataFrame({
    "applicationID": range(1, N + 1),
    "gender": genders,
    "age": ages,
    "height": heights,
    "weight": weights
})

os.makedirs("data", exist_ok=True)
df.to_csv("data/applicants.csv", index=False)

logger.info("Saved to data/applicants.csv")
