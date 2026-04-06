import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, PolynomialFeatures, OneHotEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import os
import logging
import mlflow
import mlflow.sklearn

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

df = pd.read_csv("data/applicants.csv")

# One-hot encoding gender to avoid implying ordinal relationship between
# categories
ohe = OneHotEncoder(drop="first", sparse_output=False)
df["gender_encoded"] = ohe.fit_transform(df[["gender"]]).astype(int)

X = df[["age", "height", "weight", "gender_encoded"]]
y = df["bmi"]

# Holding out 20% test data set for model evaluation
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)

mlflow.set_experiment("bmi_prediction")

with mlflow.start_run(run_name="polynomial_regression_champion"):

    champion = Pipeline([
        ("poly", PolynomialFeatures(degree=2)),
        ("scaler", StandardScaler()),
        ("model", LinearRegression())
    ])

    champion.fit(X_train, y_train)
    y_pred = champion.predict(X_test)

    mae = round(mean_absolute_error(y_test, y_pred), 4)
    rmse = round(np.sqrt(mean_squared_error(y_test, y_pred)), 4)
    r2 = round(r2_score(y_test, y_pred), 4)
    cv_scores = cross_val_score(champion, X, y, cv=5, scoring="r2")

    # Log params
    mlflow.log_param("model", "Polynomial Regression")
    mlflow.log_param("degree", 2)
    mlflow.log_param("test_size", 0.2)
    mlflow.log_param("random_state", 42)
    mlflow.log_param("cv_folds", 5)

    # Log metrics
    mlflow.log_metric("MAE", mae)
    mlflow.log_metric("RMSE", rmse)
    mlflow.log_metric("R2", r2)
    mlflow.log_metric("CV_R2_mean", round(cv_scores.mean(), 4))
    mlflow.log_metric("CV_R2_std", round(cv_scores.std(), 4))

    # Log model artifact
    mlflow.sklearn.log_model(champion, "bmi_model",
                             input_example=X_train.iloc[:1])

    logger.info(f"MAE: {mae}, RMSE: {rmse}, R2: {r2}")
    logger.info(
        f"CV R2: {
            cv_scores.round(4)}, Mean: {
            cv_scores.mean().round(4)}, Std: {
                cv_scores.std().round(4)}")

os.makedirs("models", exist_ok=True)

logger.info("Saving OHE encoder to models/ohe_encoder.pkl")
joblib.dump(ohe, "models/ohe_encoder.pkl")

logger.info("Saving model to models/bmi_model.pkl")
joblib.dump(champion, "models/bmi_model.pkl")