import csv #used to read and write CSV files
import os 

RAW_DATA_FILE = "raw_landmarks.csv"
FEATURE_DATA_FILE = "gesture_data.csv"

#save the coords of each point of the hand
def save_raw_landmarks(hand_landmarks, label):
    if hand_landmarks is None or label is None:
        return
    
    row = []
    for lm in hand_landmarks:
        row += [lm.x, lm.y, lm.z] #add the coords
    row.append(label) #add the label at the end

    file_exists = os.path.isfile(RAW_DATA_FILE)

    with open(RAW_DATA_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            header = []
            for i in range(21):
                header += [f"x{i}", f"y{i}", f"z{i}"]
            header.append("label")
            writer.writerow(header)
        writer.writerow(row)

#save the angle/normed valued
def save_features(features, label):
    if features is None or label is None:
        return

    file_exists = os.path.isfile(FEATURE_DATA_FILE)

    with open(FEATURE_DATA_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([f"f{i}" for i in range(len(features))] + ["label"])
        writer.writerow(features + [label])
