import cv2
import numpy as np

def render_gesture_panel(frame, gestures):
    if frame is None:
        return None
    
    h, w, _ = frame.shape
    panel_w = 350
    panel = np.zeros((h, panel_w, 3), dtype=np.uint8)
    panel[:] = (30, 30, 30)  # dark gray background

    for i, g in enumerate(gestures):
        if g is None:
            g = "None"
        y_pos = 50 + i * 50
        cv2.putText(panel, f"Hand {i+1}: {g}", (10, y_pos),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
    combined = np.hstack([frame, panel])
    return combined

def render_drone_panel(frame, drone):
    h, w, _ = frame.shape
    panel_w = 350
    panel = np.full((h, panel_w, 3), 220, dtype=np.uint8)

    cv2.putText(
        panel, 
        "DRONE STATE",
        (20,40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 0, 0),
        2,
        cv2.LINE_AA)

    y_offset = 70

    for line in str(drone).split("|"):
        cv2.putText(
            panel,
            line.strip(),
            (20, y_offset),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 0),
            1,
            cv2.LINE_AA)

        y_offset += 25

    combined = np.hstack((frame, panel))
    return combined