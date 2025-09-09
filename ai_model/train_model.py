import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import pickle
import os

# Define the path for the output model
MODEL_DIR = "/app/model"
MODEL_PATH = os.path.join(MODEL_DIR, "species_classifier.pkl")

# Ensure the model directory exists
os.makedirs(MODEL_DIR, exist_ok=True)

print("--- Starting Model Training ---")

# 1. Load the dataset
try:
    data = pd.read_csv("/app/data/sample_training_data.csv")
    print("Successfully loaded training data.")
    print("Data Head:\n", data.head())
except FileNotFoundError:
    print("Error: sample_training_data.csv not found. Make sure it's in the correct directory.")
    exit()

# 2. Define features (X) and target (y)
features = ['area_px', 'perimeter_px', 'width_px', 'height_px', 'aspect_ratio']
target = 'species'
X = data[features]
y = data[target]

# 3. Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"Data split: {len(X_train)} training samples, {len(X_test)} testing samples.")

# 4. Initialize and train the classifier
# RandomForest is a good general-purpose classifier
classifier = RandomForestClassifier(n_estimators=100, random_state=42)
print("Training RandomForestClassifier...")
classifier.fit(X_train, y_train)
print("Training complete.")

# 5. Evaluate the model
y_pred = classifier.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy on test data: {accuracy:.2f}")

# 6. Save the trained model to a file using pickle
with open(MODEL_PATH, 'wb') as f:
    pickle.dump(classifier, f)
print(f"Model successfully saved to {MODEL_PATH}")
print("--- Model Training Finished ---")


# some changes here 