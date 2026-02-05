import cv2
from src.video.webcam import Webcam
from src.gestures.recognizer import GestureRecognizer

import yaml
with open("config/gestures.yaml") as f:
    gesture_to_command = yaml.safe_load(f)

def main():
    print("Program started")
    cam = Webcam() #
    recognizer = GestureRecognizer()

    current_gesture = None
    display_frames = 0
    last_gesture = None

    while True:
        frame = cam.read()
        if frame is None:
            print("Failed to read frame")
            break
        
        frame = cv2.flip(frame, 1) #mirror the image
        gesture = recognizer.recognize(frame)

        if gesture is not None:
            if gesture != last_gesture:
                current_gesture = gesture
                display_frames = 240
                command = gesture_to_command.get(gesture)
                print("Detected gesture:", gesture)
                print("Executing command:", command)
            
        if current_gesture is not None and display_frames > 0:
            cv2.putText(
                frame, 
                current_gesture,
                (80,80), #postion of the test
                cv2.FONT_HERSHEY_SIMPLEX,
                2,        #font size
                (0,255,0),  #color (blue)
                2           #thickness
            )
            display_frames -= 1

        cv2.imshow("Webcam Test", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
        #this will wait 1 ms, checks if a key is pressed
        #if the key pressed is q, exit
            break

    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()