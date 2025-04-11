# Sumo Bot Main Behavior Script
# This script controls a robot in sumo mode.
# It avoids the ring, searches for opponents, and reacts to being pushed.

from zumo_2040_robot import robot  # Import robot library
import time                        # For delays and timers
import urandom                     # For random behavior (not currently used)
import math                        # Math functions (not currently used)

# Initialize robot components
motors = robot.Motors()                        # Motor controller
proximity_sensors = robot.ProximitySensors()  # Front proximity sensors
line_sensors = robot.LineSensors()            # Reflectance sensors (detect white ring)
encoders = robot.Encoders()                   # Wheel encoders (for movement tracking)
button_a = robot.ButtonA()                    # Button A interface
display = robot.Display()                     # OLED screen
buzzer = robot.Buzzer()                       # Piezo buzzer
rgb_leds = robot.RGBLEDs()                    # RGB LED controller
rgb_leds.set_brightness(3)                    # Set LED brightness (0–15)

# === CONFIGURABLE VARIABLES (Change these to tune robot behavior) ===
# Movement and Speed
MAX_SPEED = 6000                 # Max forward motor speed. Increase = faster bot, but may overshoot. Range: 0–6000
BACK_SPEED = -MAX_SPEED          # Reverse speed when avoiding edge. Usually negative of MAX_SPEED
TURN_SPEED = 3000                # Speed used when rotating in place. Higher = faster but less precise turns
CHARGE_SPEED = MAX_SPEED         # Speed when attacking opponent. Usually same as MAX_SPEED

# Sensors and Thresholds
LINE_THRESHOLD = 300             # If any sensor reads below this, assume white ring edge. White ≈ 0–300, Black ≈ 800–1000
OPPONENT_THRESHOLD = 2           # If proximity sensor reads above this, assume an opponent is near. Range: 0 (none) to ~12 (very close)
ENCODER_DELTA_THRESHOLD = 10     # Detects if robot is stuck/pushed. Lower = more sensitive to being blocked

# Timing Values (in milliseconds unless noted)
AVOID_BACK_MS = 400              # How long to reverse when avoiding ring
AVOID_SPIN_MS = 300              # How long to spin after reversing
CHARGE_DURATION_MS = 300         # How long to charge forward before rechecking line
FIND_OPPONENT_SPIN_MS = 1500     # How long to spin when searching for strongest signal
FIND_OPPONENT_SAMPLE_DELAY = 20  # Delay between proximity samples while spinning
PRE_CHARGE_PAUSE_MS = 100        # Pause before charging after aligning
COUNTDOWN_TIME_S = 1             # Countdown per number (in seconds)
LOOP_DELAY_MS = 50               # Delay between main loop cycles

# Print a message to the screen
def draw_text(text):
    display.fill(0)  # Clear display
    display.text(text, 0, 0, 1)  # Write message at top-left corner
    display.show()  # Update display

# Draw proximity bars and display label/state
def show_proximity(left, right, label):
    display.fill(0)  # Clear screen
    display.text(label, 0, 0, 1)  # Display the current mode/state
    display.text(f"L:{left} R:{right}", 0, 10, 1)  # Show left/right proximity values
    bar_l = min(left, 6)  # Clamp bar height
    bar_r = min(right, 6)
    scale = 24 // 6  # Bar scaling
    display.fill_rect(30, 64 - bar_l * scale, 10, bar_l * scale, 1)  # Left bar
    display.fill_rect(88, 64 - bar_r * scale, 10, bar_r * scale, 1)  # Right bar
    display.show()  # Refresh display

# Escape from ring edge (back up + spin)
def avoid_ring():
    rgb_leds.set(0, [255, 0, 0])  # Red = danger
    rgb_leds.show()  # Show LED color
    draw_text("Avoiding")  # Show message
    motors.set_speeds(BACK_SPEED, BACK_SPEED)  # Drive backward
    time.sleep_ms(AVOID_BACK_MS)  # Back up delay
    motors.set_speeds(TURN_SPEED, -TURN_SPEED)  # Turn in place
    time.sleep_ms(AVOID_SPIN_MS)  # Spin delay
    motors.off()  # Stop motors

# Start full-speed forward drive
def charge():
    motors.set_speeds(CHARGE_SPEED, CHARGE_SPEED)

# Wait for Button A press to begin match
def wait_for_button_a():
    draw_text("Press A to start")
    motors.off()
    buzzer.beep()  # Audible signal
    while not button_a.check():  # Wait until pressed
        pass
    while button_a.check():  # Wait until released
        pass
    for i in range(COUNTDOWN_TIME_S, 0, -1):  # Display countdown
        display.fill(0)
        display.text("Starting in:", 0, 0, 1)
        display.text(str(i), 64, 20, 1)
        display.show()
        time.sleep(1)
    buzzer.beep()  # Final beep
    show_proximity(0, 0, "FIGHT!")
    time.sleep_ms(300)

# MAIN LOOP
while True:
    wait_for_button_a()  # Wait for start trigger
    line_sensors.calibrate()  # Calibrate sensors for floor
    last_encoders = encoders.get_counts()  # Get initial encoder values

    while True:
        if button_a.check():  # Exit/reset if Button A pressed again
            while button_a.check(): pass
            break

        line_sensors.start_read()  # Begin line sensor read
        line = line_sensors.read()  # Get line values
        if min(line) < LINE_THRESHOLD:  # If white line detected
            avoid_ring()  # Back off and turn
            continue

        proximity_sensors.read()  # Read proximity sensors
        left = proximity_sensors.left_counts_with_left_leds() + proximity_sensors.front_counts_with_left_leds()  # Combine left & front-left
        right = proximity_sensors.right_counts_with_right_leds() + proximity_sensors.front_counts_with_right_leds()  # Combine right & front-right
        total = left + right  # Total proximity signal

        if total > OPPONENT_THRESHOLD:  # If enemy detected
            rgb_leds.set(0, [0, 255, 0])  # Green = tracking
            rgb_leds.show()
            show_proximity(left, right, "Facing")  # Indicate mode

            best_total = 0  # Track best detection strength
            best_left = 0
            best_right = 0
            best_time = time.ticks_ms()

            motors.set_speeds(-TURN_SPEED, TURN_SPEED)  # Begin spinning to locate enemy
            while time.ticks_diff(time.ticks_ms(), best_time) < FIND_OPPONENT_SPIN_MS:  # Spin for fixed time
                proximity_sensors.read()  # Check new readings
                left = proximity_sensors.left_counts_with_left_leds() + proximity_sensors.front_counts_with_left_leds()
                right = proximity_sensors.right_counts_with_right_leds() + proximity_sensors.front_counts_with_right_leds()
                total = left + right
                if total > best_total:  # If stronger signal found
                    best_total = total
                    best_left = left
                    best_right = right
                    best_time = time.ticks_ms()  # Update best timestamp
                time.sleep_ms(FIND_OPPONENT_SAMPLE_DELAY)  # Wait between samples

            motors.off()  # Stop turn
            time.sleep_ms(PRE_CHARGE_PAUSE_MS)  # Pause before attack

            show_proximity(best_left, best_right, "Charging!")  # Show final detection
            charge()  # Start charging
            # Keep charging until line sensor sees white edge
            while True:
                line_sensors.start_read()
                if min(line_sensors.read()) < LINE_THRESHOLD:
                    avoid_ring()
                    if best_total > OPPONENT_THRESHOLD:  # Only reorient if we had a valid target
                        if best_left > best_right:
                            motors.set_speeds(-TURN_SPEED, TURN_SPEED)  # Turn left
                        else:
                            motors.set_speeds(TURN_SPEED, -TURN_SPEED)  # Turn right
                        time.sleep_ms(AVOID_SPIN_MS)  # Spin to reorient
                    motors.off()  # Stop before scanning again  # Pause before scanning again
                    break  # Break out of charge loop to return to facing logic
                time.sleep_ms(10)  # Check edge frequently

            line_sensors.start_read()  # Check line again
            if min(line_sensors.read()) < LINE_THRESHOLD:  # If edge seen
                avoid_ring()  # Bail out

        else:
            # Stand still unless opponent is detected
            if total > OPPONENT_THRESHOLD:
                show_proximity(left, right, "Scanning")
                spin_speed = int((abs(left - right) / 12) * TURN_SPEED)
                spin_speed = max(500, min(spin_speed, TURN_SPEED))  # Clamp speed between 500 and TURN_SPEED
                if left > right:
                    motors.set_speeds(-spin_speed, spin_speed)  # Turn left with scaled speed
                elif right > left:
                    motors.set_speeds(spin_speed, -spin_speed)  # Turn right with scaled speed
                else:
                    motors.off()
            else:
                motors.off()
                show_proximity(left, right, "Idle")

        time.sleep_ms(LOOP_DELAY_MS)  # Main loop delay
