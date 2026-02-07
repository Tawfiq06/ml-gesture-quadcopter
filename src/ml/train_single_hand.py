import pandas as pd
from sklearn.ensemble import RandomForestClassifier #this is the ml model im using
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

DATA_FILE = "gesture_data.csv"
MODEL_OUT = "models/gesture_model.pkl"

def main():
    # Load dataset
    df = pd.read_csv(DATA_FILE)
    
    # Remove incomplete rows
    df = df.dropna()

    # Split features and labels
    X = df.drop(columns=["label"])  # feature matrix
    y = df["label"]                 # labels

    # Train / test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2, #20% test size
        random_state=42,
        stratify=y
    )

    # Create model
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        random_state=42
    )

    # Train
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred))

    # Save model
    joblib.dump(model, MODEL_OUT)
    print(f"Model saved to {MODEL_OUT}")

if __name__ == "__main__":
    main()
