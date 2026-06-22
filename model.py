import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib

data = pd.read_csv("student_data.csv")

X = data[["Hours", "Attendance", "Difficulty"]]
y = data["Score"]

model = LinearRegression()
model.fit(X, y)

joblib.dump(model, "student_model.pkl")

print("Model trained successfully!")