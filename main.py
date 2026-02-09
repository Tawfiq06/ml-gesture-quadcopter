import cv2
import yaml
from src.video.webcam import Webcam
from src.gestures.recognizer import GestureRecognizer
from src.gestures.features import extract_features
from src.gestures.dataset import save_features, save_raw_landmarks

#Configure
RECORD_FRAMES = 120
COUNTDOWN_SECONDS = 3

CONFIG_PATH = "config/gestures.yaml"
MODEL_PATH = "models/hand_landmarker.task"
ML_MODEL_PATH = "models/gesture_model.pkl"
#current modes: IDLE, COUNTDOWN, RECORDING

try:
    with open("config/gestures.yaml") as f:
        gesture_config = yaml.safe_load(f) or {}
except FileNotFoundError:
    gesture_config = {}

def main():
    print("Program started")

    cam = Webcam()
    recognizer = GestureRecognizer(
        model_path=MODEL_PATH,
        ml_model_path=ML_MODEL_PATH
    )

    timestamp_ms = 0
    
    mode = "IDLE"
    current_label = None
    last_label = None

    recording_frames_left = 0
    countdown_start_time = 0
    
    print("Keys:")
    print(" L = new label")
    print(" R = reuse last label")
    print(" q = quit")
    print(" 1 = UP")
    print(" 2 = DOWN")

    while True:
        frame = cam.read()
        frame = cv2.flip(frame, 1) #mirror the image
        
        gesture, hand_landmarks = recognizer.recognize(frame, timestamp_ms)
        timestamp_ms += int(1000/30)

        if gesture:
           cv2.putText(frame, gesture, (50,50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)

        if mode == "COUNTDOWN":
            elapsed = (timestamp_ms - countdown_start_time) / 1000.0 #determine how many seconds have passed
            remaining = int(COUNTDOWN_SECONDS - elapsed) #to show a whole number

            if remaining > 0: #not 0 yet
                cv2.putText(
                    frame, 
                    f"Get ready: {remaining}",
                    (50,100),
                    cv2.FONT_HERSHEY_COMPLEX,
                    2,
                    (0,255,255),
                    3
                )
            else: #count down is done
                mode = "RECORDING"
                recording_frames_left = RECORD_FRAMES

        if mode == "RECORDING":
            cv2.putText(
                frame,
                f"RECORDING: {current_label}",
                (50, 140),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2
            )

            if hand_landmarks is None:
                print("Hand lost, stopping early")
                mode = "IDLE"
                recording_frames_left = 0
            else:
                cfg = gesture_config.get(current_label, {})
                rotation_invariant = cfg.get("rotation_invariant", False)

                #save raw landmarks
                save_raw_landmarks(hand_landmarks, current_label)

                # extract features then save
                features = extract_features(hand_landmarks, rotation_invariant=rotation_invariant)
                save_features(features, current_label)
                recording_frames_left -= 1

                if recording_frames_left == 0:
                    mode = "IDLE"
                    print(f"Saved samples for '{current_label}'")

        cv2.imshow("Webcam", frame) #will show the frame

        # --- Handle Inputs ---

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

        elif key == ord("1") and mode == "IDLE":
            current_label = "UP"
            last_label = current_label
            mode = "COUNTDOWN"
            countdown_start_time = timestamp_ms

        elif key == ord("2") and mode == "IDLE":
            current_label = "DOWN"
            last_label = current_label
            mode = "COUNTDOWN"
            countdown_start_time = timestamp_ms

        #New Label
        elif key == ord("L") and mode == "IDLE": #user added label for the gesture
            current_label = input("Enter gesture label: ").strip() #remove leading/trailing spaces
            if current_label == "":
                print("Label cannot be empty")
            else:
                rot = input("Rotation invariant? (y/n): ").strip().lower()
                rotation_invariant = (rot == "y")
                #configure the gesture
                gesture_config[current_label] = {
                    "rotation_invariant": rotation_invariant
                }

                # Save config immediately
                with open(CONFIG_PATH, "w") as f:
                    yaml.safe_dump(gesture_config, f)

                last_label = current_label
                mode = "COUNTDOWN"
                countdown_start_time = timestamp_ms

        #used the last used label
        elif key == ord("R") and mode == "IDLE":
            if last_label is None:
                print("No previous label to resue") 
            else:
                current_label = last_label
                mode = "COUNTDOWN"
                countdown_start_time = timestamp_ms
                print(f"Reusing label: {current_label}")


    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()