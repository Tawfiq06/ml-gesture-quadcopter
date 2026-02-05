Step 1: 
    Goal: 
        run python script that takes webcam input, detects a hand, assigns a simple gesture label to it, and shows the current gesture + mapped command in real time
    Scope:
        - Use MediaPipe (or OpenCV only) in Python to get hand landmarks.
        - Use a very simple classifier at first (even rule-based / hard-coded) to turn landmarks into a small set of labels, e.g.:
            - open_palm, fist, thumb_up, thumb_down, point_forward.
        - Implement a gesture → command mapping in a config file (e.g. config/gestures.yaml) that maps labels to abstract drone commands like:
            - increase_altitude, decrease_altitude, yaw_left, yaw_right, hover.
        - Implement a Python-only “fake physics”: keep a simple state dict like {altitude, yaw, pitch, roll} and update it each frame based on the command (no C++ yet).    
        - Implement a minimal visualization:
            - At first, text-only (print current gesture + state to console), or
            - A simple 2D plot / window showing a dot representing the drone’s altitude and yaw.