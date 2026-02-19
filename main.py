import cv2
import yaml
from src.video.webcam import Webcam
from src.gestures.recognizer import GestureRecognizer
from src.gestures.features import extract_features
from src.gestures.dataset import save_features, save_raw_landmarks
from src.control.command_handler import apply_gesture
from src.control.drone_state import DroneState, DroneMode
from src.ui.side_panel import render_drone_panel, render_gesture_panel
# ---- SET-UP ----

#Recording Settings
RECORD_FRAMES = 120
COUNTDOWN_SECONDS = 3

#Paths
CONFIG_PATH = "config/gestures.yaml"
MODEL_PATH = "models/hand_landmarker.task"
ML_MODEL_PATH = "models/gesture_model.pkl"
TWO_HAND_MODEL_PATH = "models/two_hand_model.pkl"
FEATURE_COLUMNS_PATH = "models/feature_columns.pkl"
TWO_FEATURES_PATH = "models/two_hand_feature_columns.pkl"
CSV_PATH = "gesture_data.csv"
#current modes: IDLE, COUNTDOWN, RECORDING
#drone modes:
APP_MODE = "train" # "train" or "flight"

#open the gesture YAML
try:
    with open(CONFIG_PATH, "r") as f:
        gesture_config = yaml.safe_load(f) or {}
except FileNotFoundError:
    gesture_config = {}

# ---- MAIN ---- 
def main():
    print("Program started")

    cam = Webcam()
    recognizer = GestureRecognizer(MODEL_PATH, ML_MODEL_PATH, FEATURE_COLUMNS_PATH, CSV_PATH, TWO_FEATURES_PATH ,TWO_HAND_MODEL_PATH)
    drone = DroneState()

    timestamp_ms = 0
    
    mode = "IDLE"
    current_label = None
    last_label = None

    recording_frames_left = 0
    countdown_start_time = 0
    
    #Print Keys
    print("Keys:")
    print(" l = new label")
    print(" r = reuse last label")
    print(" p = print drone stats")
    print(" q = quit")
    print(" 1 = UP")
    print(" 2 = DOWN")

    try: #if program can run
        while True:
            frame = cam.read() #read the frame
            frame = cv2.flip(frame, 1) #mirror the image
            
            gestures, hands = recognizer.recognize(frame, timestamp_ms)
            timestamp_ms += int(1000/30)
        
            # ----  MODE HANDILING  ----

            # ---- Countdown
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
                    
            # ---- Recording ----
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

                if not hands:
                    print("Hand lost, stopping early")
                    mode = "IDLE"
                    recording_frames_left = 0
                else:
                    hand_landmarks = [0] # use first detected hand

                    cfg = gesture_config.get(current_label, {})
                    Rotation_Independent = cfg.get("Rotation_Independent", False)

                    #save raw landmarks
                    save_raw_landmarks(hand_landmarks, current_label)

                    # extract features then save
                    features = extract_features(hand_landmarks, Rotation_Independent=Rotation_Independent)
                    save_features(features, current_label)
                    recording_frames_left -= 1

                    if recording_frames_left == 0:
                        mode = "IDLE"
                        print(f"Saved samples for '{current_label}'")
            
            # ---- Flight Mode ----
            if mode == "IDLE" and APP_MODE == "flight":
                drone.tick(1/30)

                if gestures:
                    for g in gestures:
                        if g:
                            apply_gesture(g, gesture_config, drone)

            # ---- Render ----
            if APP_MODE == "flight":
                combined = render_drone_panel(frame, drone)  #will add the side panel
                cv2.imshow("Webcam", combined) #will show the frame
            else:
                if not gestures:
                    gestures = ["None", "None"]
                combined = render_gesture_panel(frame, gestures)
                cv2.imshow("Webcam", combined) #if you just want the camera

            # --- Handle Inputs ---

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break
            
            if key == ord("p"):
                print(drone)

            if mode == "IDLE":

                if key == ord("1") and mode == "IDLE":
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
                elif key == ord("l") and mode == "IDLE": #user added label for the gesture
                    current_label = input("Enter gesture label: ").strip() #remove leading/trailing spaces
                    if current_label == "":
                        print("Label cannot be empty")
                    else:
                        rot = input("Rotation Independent? (y/n): ").strip().lower()
                        Rotation_Independent = (rot == "y")
                        #configure the gesture
                        gesture_config[current_label] = {
                            "Rotation_Independent": Rotation_Independent
                        }

                        # Save config immediately
                        with open(CONFIG_PATH, "w") as f:
                            yaml.safe_dump(gesture_config, f)

                        last_label = current_label
                        mode = "COUNTDOWN"
                        countdown_start_time = timestamp_ms

                #used the last used label
                elif key == ord("r") and mode == "IDLE":
                    if last_label is None:
                        print("No previous label to resue") 
                    else:
                        current_label = last_label
                        mode = "COUNTDOWN"
                        countdown_start_time = timestamp_ms
                        print(f"Reusing label: {current_label}")

    finally: #if program fails
        cam.release()
        cv2.destroyAllWindows()

        #Emergency Landing
        #need to land the drone if we quit before landing it
        if APP_MODE == "flight" and drone.mode == DroneMode.AIRBORNE:
            print("⚠️ Program exiting while airborne, triggering emergency landing")
            drone.emergency()

        print(drone)
        
if __name__ == "__main__":
    main()