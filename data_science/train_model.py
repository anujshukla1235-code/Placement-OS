# offline training script
import os
import pathlib

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
import joblib
from sklearn.linear_model import LogisticRegression

from jobs.models import Application

from .feature_engineering import dataframe_from_applications


def train():
    apps = Application.objects.select_related("student", "job").all()
    if apps.count() < 20:
        print("Not enough data (<20). Using rule-based fallback.")
        return
    df = dataframe_from_applications(apps)
    X = df.drop(columns=["outcome"])
    y = df["outcome"]
    model = LogisticRegression()
    model.fit(X, y)
    out_dir = pathlib.Path(__file__).parent / "model_artifacts"
    out_dir.mkdir(exist_ok=True)
    joblib.dump(model, out_dir / "logreg_v1.pkl")
    print("Model saved")


if __name__ == "__main__":
    train()
