import cv2 #used for camera capture and drawing on frames
import csv #used to save landmark data
import mediapipe as mp #ml library with pre-trained models
import numpy as np
import joblib
import pandas as pd

from .features import extract_features

#initialze Mediapipe
from mediapipe.tasks import python
from mediapipe.tasks.python import vision 

#give different mediapipe classes aliases
BaseOptions = mp.tasks.BaseOptions #used to specfiy the path to the model file
HandLandmarker = mp.tasks.vision.HandLandmarker #detects hands and landmarks
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions #settings for the ml model
VisionRunningMode = mp.tasks.vision.RunningMode #tells the model how to run

#Gesture labels 
#these are used with the hard coded recognition
GESTURE_UP = 'UP'
GESTURE_DOWN = "DOWN"
GESTURE_MIDDLE = "MIDDLE" 
GESTURE_FIST = "FIST"

FINGER_TIPS = [0, 4, 8, 12, 16, 20] #wrist + all finger tips

#Shape scales
CRICLE_SCALE = 0.05
SQUARE_SCALE = 0.08

#ml model
ml_model_path = "models/gesture_model.pkl"

feature_columns_path = "models/feature_columns.pkl" 
csv_path = "gesture_data.csv"
two_features_path = "models/two_hand_feature_columns.pkl"

def distance_px(lm1, lm2, frame_shape):
    h, w, _ = frame_shape
    x1, y1 = int(lm1.x * w), int(lm1.y * h)
    x2, y2 = int(lm2.x * w), int(lm2.y * h)
    return ((x2 - x1)**2 + (y2 - y1)**2) ** 0.5 
    
class GestureRecognizer:
    #constructor
    def __init__(self, model_path: str, ml_model_path: str, feature_columns_path: str, csv_path: str, two_features_path: str, two_hand_model_path: str):
        #model_path is the path to MediaPipes hand model
        #csv_path is where I want to store the gesture landmarks

        #Need to create the MediaPipe hand landmarker
        options = HandLandmarkerOptions(
            base_options = BaseOptions(model_asset_path=model_path),
            running_mode = VisionRunningMode.VIDEO, #used for real-time frame by frame video
            num_hands = 2 #detects 2 hands now
        )

        self.landmarker = HandLandmarker.create_from_options(options) #loads the model
        self.model = joblib.load(ml_model_path)
        self.two_hand_model = joblib.load(two_hand_model_path)
        self.csv_path = csv_path #sets the csv path

        #load feature colums saved during training
        self.feature_columns = joblib.load(feature_columns_path)
        self.two_hand_feature_columns = joblib.load(two_features_path)

        # Prepare the CSV file
        try: #check if file exists
            with open(self.csv_path, "x", newline="") as f:
                writer = csv.writer(f)
                header = []
                for i in range(21): #there are 21 landmarks
                    #this makes the columns for each landmark
                    header += [f"x{i}", f"y{i}", f"z{i}"]
                header.append("label")
                writer.writerow(header)
        except FileExistsError:
            pass #the the already exists

    def recognize(self, frame, timestamp_ms: int, mode="both"):
        #need to convert from OpenCV BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        #need to run hand detection
        #sends the frame to the hand model
        result = self.landmarker.detect_for_video(mp_image, timestamp_ms)

        gestures = []
        hands = result.hand_landmarks or []

        single_hand_gestures = []
        two_hand_gesture = None

        # ---- Draw Landmarks on Frame ---- 
        for hand in hands:
            wrist = hand[0]      #wrist
            middle_mcp = hand[9] #base of middle finger

            # find the palm size (used to determine how the size of drawn landmarks)
            palm_size = distance_px(wrist, middle_mcp, frame.shape)

            
            # circles on everything
            for lm in hand:
                h, w, _ = frame.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                radius = int(palm_size * CRICLE_SCALE)
                #draw small green circles for each landmark 
                cv2.circle(frame, (cx,cy), radius, (0, 255, 0), -1)
            
            # squares around finger tips and wrist
            for i in FINGER_TIPS:
                lm = hand[i]
                h, w, _ = frame.shape
                cx, cy = int(lm.x *w), int(lm.y*h)
                half_size = int(palm_size * SQUARE_SCALE)
                top_left = (cx -half_size, cy - half_size)
                bottom_right = (cx + half_size, cy + half_size)
                cv2.rectangle(frame, top_left, bottom_right, (0, 0, 255), 2)
         
        # ---- Run Models ----
        if mode in ["two", "both"]:
            two_hand_gesture = self.detect_two_hand_gesture(hands)
        
        if mode in ["single", "both"]:
            single_hand_gestures = self.detect_single_hand_gesture(hands)

        # ---- Decide What to Return ---- 
        if mode == "single":
            return single_hand_gestures, hands
        
        elif mode == "two":
            return [two_hand_gesture] if two_hand_gesture else [], hands
        
        elif mode == "both":
            if two_hand_gesture: #give two hands higher priority
                return [two_hand_gesture], hands
            else:
                return single_hand_gestures, hands
            
        return gestures, hands
    
    def _sort_hands_left_right(self, hands):
        return sorted(hands, key=lambda h: h[0].x)
    
    def _hand_centre(self, hand):
        xs = [lm.x for lm in hand]
        ys = [lm.y for lm in hand]
        return np.mean(xs), np.mean(ys)

    def _distance_between_hands(self, hand1, hand2):
        x1, y1 = self._hand_centre(hand1)
        x2, y2 = self._hand_centre(hand2)
        return np.sqrt((x2-x1)**2 + (y2 - y1)**2)

    def detect_single_hand_gesture(self, hands):
        #Only process the first detect hand
        single_hand_gestures = []

        for hand in hands:
         #first get the features needed from the frame
            features = extract_features(hand, Rotation_Independent=True)

            #need to convert a DataFrame with proper column names
            X = pd.DataFrame([features], columns=self.feature_columns)

            #predict probabilities
            probs = self.model.predict_proba(X)[0] 
            confidence = np.max(probs)

            gesture = None
            if confidence > 0.6: 
                gesture = self.model.classes_[np.argmax(probs)]

            single_hand_gestures.append(gesture)
        return single_hand_gestures

    def detect_two_hand_gesture(self, hands):
        #must have two hands
        if len(hands) != 2:
            return None
        
        #need to make sure hands are ordered properly or it could mess up model
        hands = self._sort_hands_left_right(hands)
        left, right = hands

        features_left = extract_features(left, Rotation_Independent=True)
        features_right = extract_features(right, Rotation_Independent=True)

        combined_features = np.concatenate([features_left, features_right])

        X = pd.DataFrame([combined_features], columns=self.two_hand_feature_columns)

        probs = self.two_hand_model.predict_proba(X)[0]
        confidence = np.max(probs)

        two_hand_gesture = None
        if confidence > 0.7:
           two_hand_gesture = self.two_hand_model.classes_[np.argmax(probs)]
        
        return two_hand_gesture