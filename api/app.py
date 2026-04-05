import joblib
import numpy as np
import time
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel, Field
from src.rule_engine import get_quote
from src.monitoring import log_prediction
import logging

logger = logging.getLogger("uvicorn")

app = FastAPI(title="Sun Life Insurance Quoting System")

model = joblib.load("models/bmi_model.pkl")
ohe = joblib.load("models/ohe_encoder.pkl")


class Applicant(BaseModel):
    gender: str = Field(..., pattern="^(Male|Female)$")
    age: int = Field(..., ge=18, le=120)
    height: float = Field(..., gt=0)
    weight: float = Field(..., gt=0)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    logger.info(f"{request.method} {
                request.url.path} - {response.status_code} - {round(time.time() - start, 4)}s")
    return response


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(applicant: Applicant):
    try:
        gender_encoded = ohe.transform([[applicant.gender]])[0][0]
        features = np.array(
            [[applicant.age, applicant.height, applicant.weight, gender_encoded]])
        bmi = round(float(model.predict(features)[0]), 2)
        result = get_quote({
            "age": applicant.age,
            "bmi": bmi,
            "gender": applicant.gender
        })
        log_prediction(
            gender=applicant.gender,
            age=applicant.age,
            height=applicant.height,
            weight=applicant.weight,
            bmi=bmi,
            quote=result["quote"]
        )
        logger.info(
            f"Prediction - age: {
                applicant.age}, height: {
                applicant.height}, weight: {
                applicant.weight}, gender: {
                    applicant.gender}, bmi: {bmi}, quote: {
                        result['quote']}")
        return {
            "bmi": bmi,
            "quote": result["quote"],
            "reason": result["reason"]
        }
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail="Prediction failed")
