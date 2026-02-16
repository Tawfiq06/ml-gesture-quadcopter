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

def distance_px(lm1, lm2, frame_shape):
    h, w, _ = frame_shape
    x1, y1 = int(lm1.x * w), int(lm1.y * h)
    x2, y2 = int(lm2.x * w), int(lm2.y * h)
    return ((x2 - x1)**2 + (y2 - y1)**2) ** 0.5 
    
class GestureRecognizer:
    #constructor
    def __init__(self, model_path: str, ml_model_path: str, feature_columns_path: str = "models/feature_columns.pkl", csv_path: str = "gesture_data.csv"):
        #model_path is the path to MediaPipes hand model
        #csv_path is where I want to store the gesture landmarks

        #Need to create the MediaPipe hand landmarker
        options = HandLandmarkerOptions(
            base_options = BaseOptions(model_asset_path=model_path),
            running_mode = VisionRunningMode.VIDEO, #used for real-time frame by frame video
            num_hands = 1 #detects 1 hand right now
        )

        self.landmarker = HandLandmarker.create_from_options(options) #loads the model
        self.model = joblib.load(ml_model_path)
        self.csv_path = csv_path #sets the csv path

        #load feature colums saved during training
        self.feature_columns = joblib.load(feature_columns_path)
        
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

    def recognize(self, frame, timestamp_ms: int):
        #need to convert from OpenCV BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        #need to run hand detection
        #sends the frame to the hand model
        result = self.landmarker.detect_for_video(mp_image, timestamp_ms)

        if result.hand_landmarks: #if the hand is there
            hand = result.hand_landmarks[0]

            wrist = hand[0]      #wrist
            middle_mcp = hand[9] #base of middle finger

            # find the palm size (used to determine how the size of drawn landmarks)
            palm_size = distance_px(wrist, middle_mcp, frame.shape)

            # ---- Draw Landmarks on Frame ---- 
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
            
            # ---- ML Recognitoon ----
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

            # ---- Hard Coded Recognition ---- 
            '''
            #example detection for now
            wrist = hand[0]
            index_tip = hand[8]
            middle_tip = hand[12]
            ring_tip = hand[16]
            pinky_tip = hand[20]
            gesture = None

            THRESHOLD = 0.2 
            #check which fingers are "up"
            middle_up = middle_tip.y < wrist.y - THRESHOLD
            index_up = index_tip.y < wrist.y - THRESHOLD
            ring_up = ring_tip.y < wrist.y - THRESHOLD
            pinky_up = pinky_tip.y < wrist.y - THRESHOLD

            if not index_up & ring_up & pinky_up:
                if middle_up:
                    gesture = GESTURE_MIDDLE
                else:
                    gesture = GESTURE_FIST

            elif middle_tip.y < wrist.y -0.1:
                gesture =  GESTURE_UP
            elif middle_tip.y > wrist.y + 0.1:
                gesture =  GESTURE_DOWN
            '''

            return gesture, hand
        
        return None, None