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


def get_quote(applicant):
    # return insurance quote based on age, gender and bmi
    age = applicant["age"]
    bmi = applicant["bmi"]
    gender = applicant["gender"]

    if 18 <= age <= 39 and (bmi < 17 or bmi > 37.5):
        quote = 800
        reason = "Age is between 18 and 39 and BMI is either less than 17 or greater than 37.5"
    elif 40 <= age <= 59 and (bmi < 18 or bmi > 37.5):
        quote = 900
        reason = "Age is between 40 and 59 and BMI is either less than 18 or greater than 37.5"
    elif age >= 60 and (bmi < 18 or bmi > 44.5):
        quote = 18000
        reason = "Age is greater than 60 and BMI is either less than 18 or greater than 44.5"
    else:
        quote = 600
        reason = "BMI is in the right range"

    if gender == "Female":
        quote = quote * 0.9
        reason += " 10% discount added as application gender is female."

    return {"quote": quote, "reason": reason}


if __name__ == "__main__":
    logger.info(get_quote({"age": 25, "bmi": 16, "gender": "Male"}))
    logger.info(get_quote({"age": 45, "bmi": 20, "gender": "Female"}))
    logger.info(get_quote({"age": 65, "bmi": 50, "gender": "Male"}))
    logger.info(get_quote({"age": 30, "bmi": 25, "gender": "Female"}))
