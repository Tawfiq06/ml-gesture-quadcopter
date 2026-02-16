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
def apply_gesture(gesture, gesture_config, drone):
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
            _apply_drone_command(action, cmd, drone)

        elif cmd_type == "system":
            action = SystemAction(action_str)
            _apply_system_command(action, drone)

        elif cmd_type == "ui":
            action = UIAction(action_str)
            _apply_ui_command(action, drone)

        else:
            print(f"[WARN] Unknown commad type: {cmd_type}")
            pass
    except ValueError:
        raise RuntimeError(
            f"Invalid action '{action_str}' for gesture '{gesture}'"
        )
    _last_command_time = now

def _apply_drone_command(action: DroneAction, cmd, drone):
    delta = cmd.get("delta", 0)

    #need to add checks if its in the correct mode
    if drone.mode != DroneMode.AIRBORNE:
        print(f"[REJECT] Drone not airborne - action '{action}' ignored")
        return

    if action == DroneAction.INCREASE_THRUST:
        drone.thrust += delta

    elif action == DroneAction.DECREASE_THRUST:
        drone.thrust += delta  # delta can be negative

    elif action == DroneAction.YAW_LEFT:
        drone.yaw_rate += delta

    elif action == DroneAction.YAW_RIGHT:
        drone.yaw_rate += delta

def _apply_system_command(action: SystemAction, drone):
    if action == SystemAction.TAKEOFF:
        print("🚀 Takeoff")
        drone.takeoff()

    elif action == SystemAction.LAND:
        print("🛬 Landing")
        drone.land()

    elif action == SystemAction.EMERGENCY:
        print("🚨 Emergency stop")
        drone.emergency()
    
    elif action == SystemAction.ARM:
        print("Arming....")
        drone.arm()

def _apply_ui_command(action, drone):
    if action == UIAction.PHOTO:
        print("📸 Photo Taken")
    if action == UIAction.PRINT:
        print(drone)