import cv2
import numpy as np

GESTURE_UP = 'UP'
GESTURE_DOWN = "DOWN"
COOLDOWN_FRAMES = 30
BRIGHTNESS_THRESHOLD = 5


class GestureRecognizer:
    def __init__(self):
        #self.frame_count = 0
        self.prev_brightness = None
        self.cooldown = 0

    def recognize(self, frame):
        if self.cooldown > 0:
            self.cooldown -= 1
            return None
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #will give gray scale

        avg_brightness = np.mean(gray)

        if self.prev_brightness is None:
            self.prev_brightness = avg_brightness
            return None
        
        diff = avg_brightness - self.prev_brightness
        self.prev_brightness = avg_brightness

        if diff > BRIGHTNESS_THRESHOLD:
            self.cooldown = COOLDOWN_FRAMES
            return GESTURE_UP
        elif diff < -BRIGHTNESS_THRESHOLD:
            self.cooldown = COOLDOWN_FRAMES
            return GESTURE_DOWN
        
        return None
        '''self.frame_count += 1

        if self.frame_count > 40:
            self.frame_count = 0
            return "UP"
        else:
            return None'''