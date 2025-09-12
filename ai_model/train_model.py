import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib
import os

print("--- Starting Model Training ---")

# Define the path for the output model
output_model_path = 'species_classifier.pkl'
data_path = 'sample_training_data.csv'

# Check if data file exists
if not os.path.exists(data_path):
    print(f"Error: {data_path} not found. Make sure it's in the correct directory.")
    exit()

# Load the dataset
df = pd.read_csv(data_path)

# Prepare the data
X = df[['area', 'perimeter', 'width', 'height', 'aspect_ratio']]
y = df['species']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize and train the classifier
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Evaluate the model
y_pred = clf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model trained with accuracy: {accuracy:.2f}")

# Save the trained model using joblib
joblib.dump(clf, output_model_path)
print(f"Model saved to {output_model_path}")
print("--- Model Training Script Finished ---")


