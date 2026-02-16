from enum import Enum

class DroneAction(Enum):
    INCREASE_ALTITUDE = "increase_altitude"
    DECREASE_ALTITUDE = "decrease_altitude"
    YAW_LEFT = "yaw_left"
    YAW_RIGHT = "yaw_right"

class SystemAction(Enum):
    ARM = "arm"
    TAKEOFF = "toggle_flight_mode"
    LAND = "land"
    EMERGENCY = "emergency"

class UIAction(Enum):
    PHOTO = "take_photo"