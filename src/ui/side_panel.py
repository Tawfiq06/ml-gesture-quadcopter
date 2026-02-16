import cv2
import numpy as np

def render_side_panel(frame, drone):
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