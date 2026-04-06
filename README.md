# Health Insurance Quoting System

Steps 1–5 (Data Generation, BMI Calculation, Model Training, Evaluation and Business Rule Engine) are documented and demonstrated end-to-end in `notebooks/submission.ipynb`. Steps 6 onwards cover operationalization and are documented here.

## Operationalization Plan
The operationalization of this health insurance quoting system encompasses five core components: data generation pipeline for synthetic applicant data, polynomial regression model for BMI prediction, rule engine that derives insurance quotes from BMI and age, FastAPI inference layer for real-time serving and Streamlit frontend for user interaction. Supporting infrastructure includes unit testing, structured logging, Docker containerization, MLflow experiment tracking and a GitHub Actions CI/CD pipeline.

---

## Project Structure

```
insurance-quoter/
├── src/
│   ├── data_generator.py       # Generates applicants.csv
│   ├── bmi_calculator.py       # Adds BMI column to applicants.csv
│   ├── train.py                # Trains model → saves models/bmi_model.pkl, logs to mlruns/
│   ├── rule_engine.py          # Business rule engine and quoting logic
│   └── monitoring.py           # Prediction logging
├── api/
│   └── app.py                  # FastAPI: loads bmi_model.pkl → predicts BMI → rule engine → quote
├── frontend/
│   └── streamlit_app.py
├── tests/
│   └── test_app.py
│   └── test_mock.py
├── notebooks/
│   └── submission.ipynb
├── mlruns/
├── models/
│   ├── bmi_model.pkl
│   └── ohe_encoder.pkl
├── data/
│   └── applicants.csv
├── logs/
│   └── predictions.csv         # Real-time prediction store
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Architecture

### Training

data_generator.py → bmi_calculator.py → train.py → models/bmi_model.pkl
                                                  → models/ohe_encoder.pkl
                                                  → mlruns/ (MLflow tracking)
                                                
### Inference

User input: { gender, age, height, weight }
        ↓
app.py — loads models/bmi_model.pkl → predicts BMI
        ↓
rule_engine.py — applies business rules (age + predicted BMI + gender)
        ↓
Response: { bmi, quote, reason }
        ↓
logs/pipeline.log — logs every pipeline event and prediction

### System overview

[Applicant] → [Streamlit UI] → [FastAPI /predict] → [bmi_model.pkl] → [rule_engine] → [Quote]
                                       |
                               [logs/pipeline.log]
                                       |
                            [monitoring.py]

Commentary: In production, training and inference pipelines would be fully decoupled with training running on an event-driven basis via AWS SageMaker Pipelines and inference served independently behind a load balancer. This project is a simplified approximation to demonstrate the end-to-end flow within a single codebase.

---

## Setup

```
pip install -r requirements.txt
```

---

## Part 1: Data Generation
 
Generates a synthetic dataset of 2,000 applicants with realistic height/weight distributions split by gender, grounded in CSO 2024 and gov.ie data. The data gets saved in data/applicants.csv. In production, strict data versioning will be put in place where sub folders are created in S3 and saved on each run.

```
python src/data_generator.py
```
 
---

## Part 2: BMI Calculation

Calculates BMI for each applicant using the standard formula: weight_kg / (height_m)² and appends it to data/applicants.csv as a historical label for model training.

```
python src/BMI_calculator.py
```

---
 
## Part 3: Model Training
 
Trains a Polynomial Regression model (degree=2) with 5-fold cross-validation. Model saved to models/bmi_model.pkl, OHE encoder saved to models/ohe_encoder.pkl — reused at inference time to ensure gender encoding remains consistent. All runs tracked via MLflow.
 
```
python src/train.py
```
 
To view MLflow experiments:

```
mlflow ui --host 0.0.0.0 --port 5000
```
 
If running from SageMaker Studio, open:

```
https://<your-studio-domain>.studio.us-east-1.sagemaker.aws/jupyterlab/default/proxy/5000/
```

Commentary: In production, versioned subfolders would be created in S3 on each training run (e.g. s3://insurance-quote/bmi_model/v1/, v2/) with the latest stable version promoted via MLflow Model Registry. The inference layer would always load from a designated production alias in the registry, allowing rollback to any previous version without redeployment.

---
 
## Part 4: Business Rule Engine

Implements quoting logic based on age and BMI thresholds with a 10% discount applied for female applicants. Accepts predicted BMI from the model at inference time via app.py.

```
python src/rule_engine.py
```

---

## Part 5: API

FastAPI app exposing a `/predict` endpoint with Pydantic input validation, request logging middleware, and a `/health` check. Loads `models/bmi_model.pkl` and `models/ohe_encoder.pkl` at startup — predicts BMI from inputs, feeds predicted BMI into the rule engine and returns the quote.

```
uvicorn api.app:app --reload --host 0.0.0.0 --port 8000
```

The command can be tested in terminal with following POST request:
 
```
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"gender": "Female", "age": 30, "height": 165, "weight": 70}'
```

Commentary: In production, Amazon ElastiCache (Redis) would be used to cache predictions for common input combinations — this completely bypasses our current method where inference is called each time allowing us to cut down costs while scaling.

---
 
## Part 6: Frontend
 
Streamlit app styled to match Insurance firm's product UI. Requires FastAPI server to be running.

```
streamlit run frontend/streamlit_app.py
```

If running from SageMaker Studio, open:
 
```
https://<your-studio-domain>.studio.us-east-1.sagemaker.aws/jupyterlab/default/proxy/8501/
```

---
 
## Part 7: Observability & Monitoring
 
Every prediction is logged to logs/predictions.csv with timestamp, inputs, predicted BMI and quote.
 
Commentary 1: In production, this would be replaced with AWS SageMaker Model Monitor, which continuously monitors the deployed endpoint for data drift and model quality degradation. CloudWatch would handle alerting via SNS notifications if drift exceeds configured thresholds, with logs and metrics stored in S3.

Commentary 2: In production, as part of Responsible AI deployment; fairness audits would be performed periodically by grouping predictions across demographic subgroups and comparing average quotes to detect unintended disparate impact. SageMaker Clarify would automate this with scheduled bias reports and CloudWatch alerts if disparity metrics exceed configured thresholds.

---

## Part 8: Testing
 
Unit tests cover all business rule combinations — all age/BMI tiers, boundary conditions and the female discount. Mock tests cover the API endpoints with the model and OHE encoder mocked so tests run without needing the pkl files.

```
pytest tests/test_app.py -v
```

Commentary: In production, integration tests would be added additionally to test the full end-to-end flow against a live API with real model artifacts.

---

## Part 9: Containerisation
 
Packages the API and frontend into isolated containers. The API container loads models from the mounted models/ directory, logs predictions to logs/ and serves on port 8000. The Streamlit frontend connects to the API via the internal Docker network.

To run the API only:
 
```
docker build -t insurance-quoter .
docker run -p 8000:8000 insurance-quoter
```

Commentary: In production, the image would be pushed to Amazon ECR and deployed to AWS ECS Fargate behind an Application Load Balancer. API and frontend will be running as seperate ECS services and auto scaling configured depending on the request volume.

---

## Part 10: CI/CD

GitHub Actions pipeline runs on every push to main and dev branches. The flow of CI is as follows -> Python setup, install dependencies, generate data, train model, lint checking with flake8, run unit tests with pytest and build Docker image.

---
## References:
I have used official AWS Sagemaker documents as a reference document to write the operationalization plan along with domain knowledge from prior work experience:
https://github.com/aws/amazon-sagemaker-examples
