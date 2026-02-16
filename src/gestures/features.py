import numpy as np #useful for the math
import math

def align_hand(landmarks):
    #this will align the hand so that it is straight up
    #helpful with irrotational gestures
    #make all the hands in the same direction

    wrist = np.array(landmarks[0])
    middle_mcp = np.array(landmarks[9])

    dx, dy = middle_mcp - wrist
    angle = math.atan2(dy,dx) #angle of the hand

    cos_a = math.cos(-angle)
    sin_a = math.sin(-angle)

    aligned = []

    for x,y in landmarks:
        #need to rotate wrist
        # x' = x*sin + y cos (this is the change in x)
        # so need to add the orginal x to get the new changed x
        # x_new = x' + x1
        x_new = (x - wrist[0]) * cos_a - (y - wrist[1]) * sin_a + wrist[0]
        y_new = (x - wrist[0]) * sin_a + (y - wrist[1]) * cos_a + wrist[1]
        aligned.append([x_new, y_new])
    return aligned

#use this to calculate the angle
def angle(a, b, c):
    #convert points to vectors
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    #find the distance vectors
    ba = a - b
    bc = c - b

    #find the cosine of the angle (vector math formula)
    cosine = np.dot(ba,bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    #convert and return in degrees
    return np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0)))

#used to determine the features of the hand
def extract_features(hand_landmarks, Rotation_Independent=False):
    # handle both MediaPipe object or plain list
    if hasattr(hand_landmarks, "landmark"):
        lm = hand_landmarks.landmark
    else:
        lm = hand_landmarks  # assume it's already a list of 21 points [x,y,z]

    #helper function to make getting the point easier
    def pt(i): 
        return [lm[i].x, lm[i].y]
    
    landmarks = [pt(i) for i in range(21)]

    #only rotate if needed
    if Rotation_Independent:
        landmarks = align_hand(landmarks)

    features = [] #used to store the features

    #Determine Finger angles
    fingers = [
        (5, 6, 8),    # index
        (9, 10, 12),  # middle
        (13, 14, 16), # ring
        (17, 18, 20), # pinky
        (2, 3, 4)     # thumb
    ]

    for mcp, pip, tip in fingers:
        features.append(angle(landmarks[mcp], landmarks[pip], landmarks[tip]))

    #Distances (normed)
    wrist = np.array(landmarks[0])
    index_tip = np.array(landmarks[8])
    pinky_tip = np.array(landmarks[20])

    #to determine the hand size
    palm_width = np.linalg.norm(index_tip - pinky_tip)

    #finger distances  (from wrist divided by palm width)
    for tip in [8, 12, 16, 20, 4]:
        dist = np.linalg.norm(np.array(landmarks[tip]) - wrist)
        features.append(dist / palm_width)

    return features