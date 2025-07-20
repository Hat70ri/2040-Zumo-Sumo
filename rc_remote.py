from zumo_2040_robot import robot
from machine import Pin, time_pulse_us
from micropython import const
import time

# === Constants for PWM signal decoding ===
CENTER_US = const(1500)     # Center pulse width in microseconds (neutral position)
RANGE_US = const(500)       # Half the range of PWM (e.g. 1000–2000us total)
DEADBAND_US = const(40)     # Ignore small jitters around center (±40us)

# === Initialize hardware ===
motors = robot.Motors()         # Control left and right motors
button_a = robot.ButtonA()      # Button A to toggle drive on/off
display = robot.Display()       # OLED display

# === Setup RC receiver PWM input pins ===
throttle_pin = Pin(18, Pin.IN)  # Channel 1 (throttle) from R6FG
steering_pin = Pin(19, Pin.IN)  # Channel 2 (steering) from R6FG

# === State variables ===
drive_enabled = False           # Whether robot should move
last_throttle = 0               # Last calculated throttle speed
last_steering = 0               # Last calculated steering delta

# === Reads pulse width in microseconds from a given pin ===
def read_pwm(pin):
    try:
        # Measure length of high pulse (1) with a 25ms timeout
        return time_pulse_us(pin, 1, 25000)
    except OSError:
        return None  # Timeout or signal error

# === Converts pulse width to motor speed (from -6000 to 6000) ===
def pwm_to_speed(pulse_us):
    if pulse_us is None:
        return 0
    delta = pulse_us - CENTER_US
    if abs(delta) < DEADBAND_US:
        return 0  # Ignore small changes around center
    speed = int((delta / RANGE_US) * robot.Motors.MAX_SPEED)
    # Clamp speed to allowed range
    return max(-robot.Motors.MAX_SPEED, min(robot.Motors.MAX_SPEED, speed))

# === Draws basic UI on the OLED screen ===
def draw_ui():
    display.fill(0)  # Clear screen
    display.text("A: RC " + ("off" if not drive_enabled else "on"), 0, 0)
    display.text("Thr: " + str(last_throttle), 0, 16)
    display.text("Str: " + str(last_steering), 0, 32)
    display.show()

draw_ui()  # Initial display

# === Main loop ===
while True:
    # Check if Button A was pressed to toggle drive mode
    if button_a.check():
        while button_a.check(): pass  # Wait for release
        drive_enabled = not drive_enabled
        if not drive_enabled:
            motors.set_speeds(0, 0)  # Stop motors immediately
        draw_ui()
        time.sleep_ms(200)  # Debounce delay

    # Read PWM values from RC receiver
    throttle_pulse = read_pwm(throttle_pin)
    steering_pulse = read_pwm(steering_pin)

    # Convert pulse width to motor speeds
    last_throttle = pwm_to_speed(throttle_pulse)
    last_steering = pwm_to_speed(steering_pulse)

    # If enabled, compute motor speeds and drive
    if drive_enabled:
        # Mixing: throttle + steering for left, throttle - steering for right
        left = last_throttle + last_steering
        right = last_throttle - last_steering

        # Clamp to motor limits
        left = max(-robot.Motors.MAX_SPEED, min(robot.Motors.MAX_SPEED, left))
        right = max(-robot.Motors.MAX_SPEED, min(robot.Motors.MAX_SPEED, right))

        motors.set_speeds(left, right)

    draw_ui()  # Update screen with latest info
    time.sleep_ms(20)  # Loop delay (~50Hz update rate)
