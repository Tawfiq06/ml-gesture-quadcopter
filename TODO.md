# TODO – ML Gesture-Controlled Quadcopter Simulator

## Phase 1 – Python vertical slice
- [x] Set up Python virtual environment and basic dependencies.
- [x] Implement webcam capture and show raw frames.
- [x] Integrate MediaPipe (or equivalent) to get hand landmarks per frame.
- [x] Design a simple gesture label API (function that returns a string label).
- [x] Implement a basic rule-based gesture recognizer (no ML yet).
- [x] Define a config file `config/gestures.yaml` for gesture → command mapping.
- [x] Implement a Python “command handler” that updates a simple drone state (altitude, yaw, etc.).
- [x] Implement a minimal visualization (console output or simple window).
- [x] Run the end-to-end loop: webcam → landmarks → gesture → command → state update → visualization.

## Phase 2 – Gesture dataset & ML
- [x] Record gesture data with labels and save landmarks/features.
- [x] Add rotation-invariant feature extraction.
- [x] Implement dataset saving in `dataset.py` (raw landmarks + features).
- [ ] Train initial ML model (RandomForest) on single-hand gestures.
- [ ] Evaluate model and iterate on features if needed.
- [ ] Support reusing last gesture label and user-defined labels.

## Phase 3 – Python 2D visualization & testing
- [ ] Implement a simple 2D top-down or side view of the drone.
- [ ] Show drone state in real-time (altitude, yaw, pitch, roll).
- [ ] Connect gesture ML model output to 2D visualization commands.
- [ ] Debug gesture → command → state pipeline before moving to C++.

## Phase 4 – C++ physics simulator
- [ ] Implement quadcopter physics engine in C++ (support for one drone initially).
- [ ] Expose API to update drone state from Python or gesture input.
- [ ] Implement multiple drone support (optional for later).

## Phase 5 – 3D visualization in C++
- [ ] Integrate 3D renderer (OpenGL/GLFW/SDL or a game engine).
- [ ] Render drone(s) and environment based on physics state.
- [ ] Connect gesture ML commands to 3D visualization in real-time.
- [ ] Add debug overlays (optional: show landmarks, rotation, velocity vectors).

## Phase 6 – Two-hand gestures & advanced features
- [ ] Update hand landmark detection for both hands.
- [ ] Extend feature extraction and ML model to multi-hand gestures.
- [ ] Map new gestures to drone commands.
- [ ] Add optional camera-relative rotation/scale adjustments for hands.

## Phase 7 – Polish & optimization
- [ ] Optimize Python ↔ C++ interface.
- [ ] Improve ML accuracy and add fallback for ambiguous gestures.
- [ ] Refine visualization (smooth camera, lighting, UI elements).
- [ ] Package project for reproducibility.
