from enum import Enum
import math

MAX_VERTICAL_SPEED = 5.0
MAX_FORWARD_SPEED = 10.0
FORWARD_ACCEL_FACTOR = 0.5 # how strong pitch creates acceleration
MAX_YAW_RATE = 90.0 # Degrees per second
MAX_THRUST = 20.0

GRAVITY = -9.81 # m/s^2
DRAG = 0.98 # air resistance

HOVER_THRUST = 9.81
THURST_RESPONSE  = 5.0 # how fast do the motors react

class DroneMode(Enum):
    IDLE = 0
    ARMED = 1
    AIRBORNE = 2
    LANDING = 3
    EMERGENCY = 4

class DroneState:
    def __init__(self):
        self.mode = DroneMode.IDLE # state machine, controls what the drone can do

        self.hover_enabled = False
        self.hover_target_altitude = 0.0

        self.altitude = 0.0        # postion in z
        self.x = 0.0               # postion in x
        self.y = 0.0

        self.yaw = 0.0             # rotation around z
        self.pitch = 0.0
        self.roll = 0.0

        self.target_thrust = 0.0          # upward acceleration
        self.current_thrust = 0.0           
        #velcoties 
        self.forward_velocity  = 0.0 
        self.vertical_velocity = 0.0 # speed up and down

        #yaw
        self.yaw_acceleration = 0.0
        self.yaw_input = 0.0
        self.yaw_rate = 0.0          # rotational velocity

    def __str__(self):
        return (
            f"MODE: {self.mode.name} | "
            f"HOVER: {'ON' if self.hover_enabled else 'OFF'} | "
            f"ALT: {self.altitude:.2f} | "
            f"POS: ({self.x:.2f}, {self.y:.2f}) | "
            f"YAW: {self.yaw:.2f} | "
            f"PITCH: {self.pitch:.2f} | "
            f"ROLL: {self.roll:.2f} | "
            f"TGT_THR: {self.target_thrust:.2f} | "
            f"CUR_THR: {self.current_thrust:.2f} | "
            f"VF: {self.forward_velocity:.2f} | "
            f"VV: {self.vertical_velocity:.2f} | "
            f"YR: {self.yaw_rate:.2f}"
        )

    
    def tick(self, dt):
        if self.mode in (DroneMode.AIRBORNE, DroneMode.LANDING):
            # ---- Yaw Rotation ----
            self.yaw_acceleration = self.yaw_input * 200 # torque
            self.yaw_rate += self.yaw_acceleration * dt
            self.yaw_rate *= 0.95 # rotational drag
            self.yaw += self.yaw_rate * dt

            # ---- Vertical Physics ----
            #Thurst motor smoothing
            self.current_thurst += (self.target_thrust - self.current_thurst) * THURST_RESPONSE * dt 

            #Hover controller
            if self.hover_enabled:
                error = self.hover_target_altitude - self.altitude
                derivative = -self.vertical_velocity

                Kp = 2.0 #propotional gain
                Kd = 1.5

                self.target_thrust = HOVER_THRUST + (error * Kp) + (Kd * derivative)

            #Ground effect
            ground_effect = 0
            if self.altitude < 1.0:
                ground_effect = (1.0 - self.altitude) * 2 

            #final vertical acceleration 
            acceleration = self.current_thurst + GRAVITY + ground_effect

            self.vertical_velocity += acceleration * dt
            self.altitude += self.vertical_velocity * dt

            # ---- Forward Physics ----
            # Pitch makes forward acceleration
            drag_force = -0.1 * self.forward_velocity * abs(self.forward_velocity)
            forward_acceleration = self.pitch * FORWARD_ACCEL_FACTOR

            self.forward_velocity += forward_acceleration * dt
            self.forward_velocity += drag_force * dt # air resistance

            # convert Yaw to radians
            yaw_rad = math.radians(self.yaw)

            self.x += math.cos(yaw_rad) * self.forward_velocity * dt
            self.y += math.sin(yaw_rad) * self.forward_velocity * dt
        
        self.clamp() # need to clamp all values

        if self.mode == DroneMode.LANDING and self.altitude == 0:
            self.mode = DroneMode.IDLE
            print ("🛬 Drone landed")

    def clamp(self):
        # ---- ANGLE LIMITS ----
        self.pitch = max(-30, min(30, self.pitch))
        self.roll = max(-30, min(30, self.roll))

        # Wrap yaw to 0-360
        self.yaw = self.yaw % 360

        # ---- VELOCITY LIMITS ----
        self.vertical_velocity = max(-MAX_VERTICAL_SPEED, min(MAX_VERTICAL_SPEED, self.vertical_velocity))
        self.target_thrust = max(0, min(MAX_THRUST, self.target_thrust))
        self.current_thrust = max(0, min(MAX_THRUST, self.current_thrust))

        self.yaw_rate = max(-MAX_YAW_RATE, min(MAX_YAW_RATE, self.yaw_rate))

        # ---- FORWARD LIMITS ----
        self.forward_velocity = max(-MAX_FORWARD_SPEED, min(MAX_FORWARD_SPEED, self.forward_velocity))

        # ---- GROUND COLLISION ---- 
        if self.altitude < 0:
            self.altitude = 0
            self.vertical_velocity = 0


    def toggle_hover(self):
        if self.mode != DroneMode.AIRBORNE:
            print("[REJECT] Can only hover while airborne")
            return
        
        self.hover_enabled = not self.hover_enabled

        if self.hover_enabled:
            self.hover_target_altitude = self.altitude
            print("🟢 Hover enabled")
        else:
            print("🔴 Hover disabled")

    def arm(self):
        if self.mode == DroneMode.ARMED:
            print("Drone is already armed")
            return
        if self.mode != DroneMode.IDLE:
            print("[REJECT] Can only arm from IDLE")
            return
        self.mode = DroneMode.ARMED
        print("🔐 Drone armed")

    def takeoff(self):
        if self.mode == DroneMode.AIRBORNE:
            print("Drone is already airborne")
            return
        elif self.mode != DroneMode.ARMED:
            print("[REJECT] Must be ARMED to take off")
            return
        self.mode = DroneMode.AIRBORNE
        self.target_thrust = 12 #need enough thrust to take off
        print("🚀 Drone airborne")

    def land(self):
        if self.mode != DroneMode.AIRBORNE:
            print("[REJECT] Cannot land")
            return
        self.mode = DroneMode.LANDING
        self.target_thrust = 0
        print("🛬 Landing...")
    
    def emergency(self):
        self.mode = DroneMode.EMERGENCY
        self.altitude = 0
        self.mode = DroneMode.IDLE