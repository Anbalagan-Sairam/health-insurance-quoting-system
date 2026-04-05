# Health Insurance Quoting System
 
## Goal
The goal of this assignment is to build an end-to-end health insurance quoting system — from synthetic data generation to a production-ready ML pipeline with a REST API, frontend, observability, testing, containerisation, and CI/CD.

---
 
## Project Structure
 
```
sunlife-assignment/
├── src/
│   ├── data_generator.py       # Generates synthetic applicant dataset
│   ├── BMI_calculator.py       # BMI calculation function + applies to dataset
│   ├── train.py                # Model training, evaluation, and model saving
│   └── rule_engine.py          # Business rule engine and quoting logic
├── api/
│   └── app.py                  # FastAPI serving layer
├── frontend/
│   └── streamlit_app.py        # Streamlit frontend
├── tests/
│   └── test_app.py             # Unit tests for business rules
├── notebooks/
│   └── submission.ipynb        # Full end-to-end notebook walkthrough
├── models/                     # Saved model artifacts
├── data/                       # Generated dataset
├── logs/                       # Prediction and pipeline logs
├── Dockerfile                  # Container definition
├── docker-compose.yml          # Multi-service orchestration
├── requirements.txt
└── README.md
```
 
---
 
## Setup
 
```
pip install -r requirements.txt
```
 
---
 
## Part 1: Data Generation
 
Generates a synthetic dataset of 2,000 applicants with realistic height/weight distributions split by gender, grounded in CSO 2024 and Healthy Ireland 2024 data.
 
```
python src/data_generator.py
```
 
---
 
## Part 2: BMI Calculation
 
Calculates BMI for each applicant using the standard formula: weight_kg / (height_m)²
 
```
python src/BMI_calculator.py
```
 
---
 
## Part 3: Model Training
 
Trains and evaluates four models (Linear Regression, Polynomial Regression, Random Forest, Gradient Boosting) with 5-fold cross-validation. Champion model saved to models/bmi_model.pkl.
 
```
python src/train.py
```
 
Why Polynomial Regression? BMI is a near-deterministic function of height and weight. Polynomial Regression captures the mathematical structure exactly, achieving R² of 0.9999 with consistent cross-validation scores. In a regulated insurance environment, model decisions must be explainable to auditors and regulators — Polynomial Regression provides interpretability while matching the underlying formula structure.
 
---
 
## Part 4: Business Rule Engine
 
Implements quoting logic based on age and BMI thresholds with a female discount applied where applicable.
 
```python
from src.rule_engine import get_quote
 
get_quote({"age": 30, "bmi": 25, "gender": "Female"})
# {'quote': 540.0, 'reason': 'BMI is in the right range 10% discount added as application gender is female.'}
```
 
---
 
## Part 5: API
 
FastAPI app exposing a /predict endpoint with Pydantic input validation, request logging middleware, and a /health check.
 
```
uvicorn api.app:app --reload --host 0.0.0.0 --port 8000
```
 
Example request:
 
```
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"gender": "Female", "age": 30, "height": 165, "weight": 70}'
```
 
Response:
 
```json
{
  "bmi": 25.71,
  "quote": 540.0,
  "reason": "BMI is in the right range 10% discount added as application gender is female."
}
```
 
---
 
## Part 6: Frontend
 
Streamlit app styled to match Sun Life's product UI. Requires FastAPI server to be running.
 
```
streamlit run frontend/streamlit_app.py
```
 
---
 
## Part 7: Testing
 
Unit tests cover all business rule combinations — all age/BMI tiers, boundary conditions, and the female discount.
 
```
pytest tests/test_app.py -v
```
 
Output: 14 passed
 
---
 
## Part 8: Observability & Monitoring
 
Every prediction is logged with timestamp, inputs, predicted BMI, and quote to logs/pipeline.log. Request-level observability (latency, status codes) is handled via FastAPI middleware and logged to stdout.
 
---
 
## Part 9: Containerisation
 
```
docker build -t sunlife .
docker run -p 8000:8000 sunlife
```
 
Or run both API and frontend together:
 
```
docker-compose up
```
 
---
 
## Part 10: CI/CD
 
GitHub Actions pipeline runs on every push to main. Steps: checkout, Python setup, install dependencies, lint with flake8, run unit tests with pytest.
 
---
 
## Operationalization Plan
 
### Architecture
 
```
[Applicant] -> [Streamlit UI] -> [FastAPI] -> [ML Model] -> [Business Rules] -> [Quote]
                                     |
                               [Prediction Log]
                                     |
                          [Drift Monitoring Pipeline]
```
 
### Steps to Operationalize
 
1. Model Versioning
All experiments tracked via MLflow. Final model versioned and registered in MLflow Model Registry. Artifacts stored in S3.
 
2. Serving Layer
FastAPI containerised and deployed to AWS ECS Fargate behind an Application Load Balancer. Auto-scaling configured based on request volume.
 
3. CI/CD Pipeline
GitHub Actions runs tests and linting on every push. On merge to main, triggers automated deployment to ECS via AWS CodePipeline.
 
4. Monitoring
- Request-level: latency and error rates via CloudWatch
- Prediction-level: all inputs/outputs logged to S3
- Drift detection: weekly Evidently reports comparing incoming feature distributions against training baseline
- Alerts: SNS notifications if BMI prediction drift exceeds threshold
 
5. Feedback Loop
New applicant data accumulated monthly. Automated retraining pipeline triggered via SageMaker Pipelines. Model promoted to production only if new model outperforms baseline on held-out evaluation set.
 
6. Security
- API authentication via AWS API Gateway + IAM
- PII data encrypted at rest (S3 SSE) and in transit (HTTPS)
- GDPR Article 22 compliance — Polynomial Regression chosen specifically for explainability of automated decisions