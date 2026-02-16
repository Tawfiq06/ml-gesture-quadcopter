from enum import Enum
import math

MAX_VERTICAL_SPEED = 5.0
MAX_FORWARD_SPEED = 10.0
FORWARD_ACCEL_FACTOR = 0.5 # how strong pitch creates acceleration
MAX_YAW_RATE = 90.0 # Degrees per second

GRAVITY = -9.81 # m/s^2
DRAG = 0.98 # air resistance

class DroneMode(Enum):
    IDLE = 0
    ARMED = 1
    AIRBORNE = 2
    LANDING = 3
    EMERGENCY = 4

class DroneState:
    def __init__(self):
        self.mode = DroneMode.IDLE # state machine, controls what the drone can do

        self.altitude = 0.0        # postion in z
        self.x = 0.0               # postion in x
        self.y = 0.0

        self.yaw = 0.0             # rotation around z
        self.pitch = 0.0
        self.roll = 0.0

        self.thrust = 0.0          # upward acceleration
        
        #velcoties 
        self.forward_velocity  = 0.0 
        self.vertical_velocity = 0.0 # speed up and down
        self.yaw_rate = 0.0          # rotational velocity

    def __str__(self):
        return (
            f"MODE: {self.mode.name} | "
            f"ALT: {self.altitude:.2f} | "
            f"X: {self.x: .2f} | "
            f"Y: {self.y: .2f} | "
            f"YAW: {self.yaw:.2f} | "
            f"PITCH: {self.pitch:.2f} | "
            f"ROLL: {self.roll:.2f} | "
            f"THRUST: {self.thrust: .2f} | "
            f"VF : {self.forward_velocity: .2f} | "
            f"VV : {self.vertical_velocity: .2f} | "
            f"YR : {self.yaw_rate: .2f}"
        )
    
    def tick(self, dt):
        if self.mode in (DroneMode.AIRBORNE, DroneMode.LANDING):
            # ---- Yaw Rotation ----
            self.yaw += self.yaw_rate * dt

            # ---- Vertical Physics ----      
            acceleration = self.thrust + GRAVITY # Net acceleration = thrust + gravity

            self.vertical_velocity += acceleration * dt
            self.altitude += self.vertical_velocity * dt

            # ---- Forward Physics ----
            # Pitch makes forward acceleration
            forward_acceleration = self.pitch * FORWARD_ACCEL_FACTOR

            self.forward_velocity += forward_acceleration * dt
            self.forward_velocity *= DRAG # air resistance

            # convert Yaw to radians
            yaw_rad = math.radians(self.yaw)

            self.x += math.cos(yaw_rad) * self.forward_velocity * dt
            self.y += math.sin(yaw_rad) * self.forward_velocity * dt
        
        self.clamp() # need to clamp all values

        if self.mode == DroneMode.LANDING and self.altitude == 0:
            self.mode = DroneMode.IDLE
            print ("🛬 Drone landed")
        
        print(self)

    def clamp(self):
        # ---- ANGLE LIMITS ----
        self.pitch = max(-30, min(30, self.pitch))
        self.roll = max(-30, min(30, self.roll))

        # Wrap yaw to 0-360
        self.yaw = self.yaw % 360

        # ---- VELOCITY LIMITS ----
        self.vertical_velocity = max(-MAX_VERTICAL_SPEED, min(MAX_VERTICAL_SPEED, self.vertical_velocity))

        self.yaw_rate = max(-MAX_YAW_RATE, min(MAX_YAW_RATE, self.yaw_rate))

        # ---- FORWARD LIMITS ----
        self.forward_velocity = max(-MAX_FORWARD_SPEED, min(MAX_FORWARD_SPEED, self.forward_velocity))

        # ---- GROUND COLLISION ---- 
        if self.altitude < 0:
            self.altitude = 0
            self.vertical_velocity = 0

    def arm(self):
        if self.mode != DroneMode.IDLE:
            print("[REJECT] Can only arm from IDLE")
            return
        self.mode = DroneMode.ARMED
        print("🔐 Drone armed")

    def takeoff(self):
        if self.mode != DroneMode.ARMED:
            print("[REJECT] Must be ARMED to take off")
            return
        self.mode = DroneMode.AIRBORNE
        print("🚀 Drone airborne")

    def land(self):
        if self.mode != DroneMode.AIRBORNE:
            print("[REJECT] Cannot land")
            return
        
        self.mode = DroneMode.LANDING
        self.thrust = 0
        print("🛬 Landing...")
    
    def emergency(self):
        self.mode = DroneMode.EMERGENCY
        self.altitude = 0