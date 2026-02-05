import cv2 #this will be used to capture video from the webcam

#cv2.VideoCapture is used to open the camera
#cap.read() is used to get frames
#cap.release() is used to close the camera
#cv2.imshow/cv2.waitKey shows images in a window (to be used in main.py)

class Webcam:
    def __init__(self, index: int = 0): #use to open the camera
        self._cap = cv2.VideoCapture(index) 
        if not self._cap.isOpened():
            raise RuntimeError(f"Could not open webcam {index}") #raise an error flag if camera couldnt open
        
    def read(self): #use to return a frame from the camera
        ok, frame = self._cap.read() #ok is a boolean flag, frame is the frame from the camera
        #this is because VideoCapture.read() returns a pair of values (bool, frame)
        if not ok:
            return None #raise an error flag if frame couldnt be read
        return frame #returns the frame from the camera
    def release(self):
        self._cap.release() #use to close the camera