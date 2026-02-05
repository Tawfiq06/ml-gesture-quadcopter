Phase 1 – Python vertical slice
    [ ] Set up Python virtual environment and basic dependencies.
    [ ] Implement webcam capture and show raw frames.
    [ ] Integrate MediaPipe (or equivalent) to get hand landmarks per frame.
    [ ] Design a simple gesture label API (e.g. function that returns a string label).
    [ ] Implement a basic rule-based gesture recognizer (no ML yet).
    [ ] Define a config file config/gestures.yaml for gesture → command mapping.
    [ ] Implement a Python “command handler” that updates a simple drone state (altitude, yaw, etc.).
    [ ] Implement a minimal visualization (console output or simple window).
    [ ] Run the end-to-end loop: webcam → landmarks → gesture → command → state update → visualization.