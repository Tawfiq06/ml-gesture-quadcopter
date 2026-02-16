from .drone_state import DroneMode
from src.control.actions import DroneAction, SystemAction, UIAction
import time

# ---- Varibles/CONSTANTS ----
COMMAND_COOLDOWN = 1 #seconds
_last_command_time = 0

# ---- Drone Action Lookup ----
'''
DRONE_ACTION_MAP = {
    DroneAction.INCREASE_ALTITUDE:
    DroneAction.DECREASE_ALTITUDE: 
    DroneAction.YAW_LEFT:
    DroneAction.YAW_RIGHT

}
'''
def apply_gesture(gesture, gesture_config, state):
    global _last_command_time
    
    if gesture is None:
        return
    
    now = time.time()

    if now - _last_command_time < COMMAND_COOLDOWN:
        return #too soon for a command, ignore it

    cmd = gesture_config.get(gesture)
    if not cmd:
        return #unknown gesture
    
    cmd_type = cmd.get("type")
    action_str = cmd.get("action")

    if not action_str:
        return #training-only gesture
    
    try:
        if cmd_type == "drone":
            action = DroneAction(action_str)
            _apply_drone_command(action, cmd, state)

        elif cmd_type == "system":
            action = SystemAction(action_str)
            _apply_system_command(action, state)

        elif cmd_type == "ui":
            action = UIAction(action_str)
            _apply_ui_command(action)

        else:
            print(f"[WARN] Unknown commad type: {cmd_type}")
            pass
    except ValueError:
        raise RuntimeError(
            f"Invalid action '{action_str}' for gesture '{gesture}'"
        )
    _last_command_time = now

def _apply_drone_command(action: DroneAction, cmd, state):
    delta = cmd.get("delta", 0)

    #need to add checks if its in the correct mode
    if state.mode != DroneMode.AIRBORNE:
        print(f"[REJECT] Drone not airborne - action '{action}' ignored")
        return

    if action == DroneAction.INCREASE_ALTITUDE:
        state.altitude += delta

    elif action == DroneAction.DECREASE_ALTITUDE:
        state.altitude += delta  # delta can be negative

    elif action == DroneAction.YAW_LEFT:
        state.yaw += delta

    elif action == DroneAction.YAW_RIGHT:
        state.yaw += delta

def _apply_system_command(action: SystemAction, state):
    if action == SystemAction.TAKEOFF:
        print("🚀 Takeoff")
        state.takeoff()

    elif action == SystemAction.LAND:
        print("🛬 Landing")
        state.land()

    elif action == SystemAction.EMERGENCY:
        print("🚨 Emergency stop")
        state.emergency()
    
    elif action == SystemAction.ARM:
        print("Arming....")
        state.arm()

def _apply_ui_command(action):
    if action == "take_photo":
        print("📸 Photo Taken")