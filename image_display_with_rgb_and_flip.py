# pbm_viewer_cycle.py
# Displays 128x64 PBM images and cycles through 20 RGB LED modes

import time, os, math, urandom
from zumo_2040_robot.display import Display
from zumo_2040_robot import robot

# === Setup image directory ===
images_dir = "images"
images = [f"{images_dir}/{f}" for f in os.listdir(images_dir) if f.endswith(".pbm")]
images.sort()
if not images:
    raise Exception("No PBM images found in 'images/' folder")

# === Initialize hardware ===
button_a = robot.ButtonA()
button_b = robot.ButtonB()
button_c = robot.ButtonC()
display = robot.Display()
rgb_leds = robot.RGBLEDs()
rgb_leds.set_brightness(5)

# === State variables ===
index = 0
flipped = False
led_mode = 0
hue = 0
pulse_brightness = 0
pulse_direction = 1
frame = 0
chase_index = 0
scanner_pos = 0
scanner_dir = 1

# === Flip image vertically ===
def flip_framebuffer_vertically(src_fb, dest_fb):
    for y in range(64):
        for x in range(0, 128, 8):
            byte = src_fb.pixel(x, y) << 7 | \
                   src_fb.pixel(x+1, y) << 6 | \
                   src_fb.pixel(x+2, y) << 5 | \
                   src_fb.pixel(x+3, y) << 4 | \
                   src_fb.pixel(x+4, y) << 3 | \
                   src_fb.pixel(x+5, y) << 2 | \
                   src_fb.pixel(x+6, y) << 1 | \
                   src_fb.pixel(x+7, y)
            for b in range(8):
                dest_fb.pixel(x + b, 63 - y, (byte >> (7 - b)) & 1)

# === LED animation engine ===
def update_leds():
    global hue, pulse_brightness, pulse_direction, frame, chase_index, scanner_pos, scanner_dir
    rgb_leds.off()

    if led_mode == 0:
        return
    elif led_mode == 1:
        for i in range(6):
            rgb_leds.set_hsv(i, [(hue + i * 60) % 360, 255, 255])
        hue = (hue + 5) % 360
    elif led_mode == 2:
        for i in range(6):
            rgb_leds.set(i, [255, 255, 255])
    elif led_mode == 3:
        for i in range(6):
            rgb_leds.set(i, [255, 0, 0])
    elif led_mode == 4:
        for i in range(6):
            rgb_leds.set(i, [pulse_brightness] * 3)
        pulse_brightness += pulse_direction * 8
        if pulse_brightness >= 255:
            pulse_brightness = 255
            pulse_direction = -1
        elif pulse_brightness <= 0:
            pulse_brightness = 0
            pulse_direction = 1
    elif led_mode == 5:
        for i in range(6):
            rgb_leds.set(i, [0, 0, 255] if (i + frame) % 3 == 0 else [0, 0, 0])
    elif led_mode == 6:
        for i in range(6):
            rgb_leds.set(i, [255 - i * 42, 0, i * 42])
    elif led_mode == 7:
        for i in range(6):
            rgb_leds.set(i, [urandom.getrandbits(8) for _ in range(3)] if urandom.getrandbits(1) else [0, 0, 0])
    elif led_mode == 8:
        brightness = int((1 + math.sin(frame / 10)) * 127)
        for i in range(6):
            rgb_leds.set_hsv(i, [(hue + i * 60) % 360, 255, brightness])
        hue = (hue + 1) % 360
    elif led_mode == 9:
        for i in range(6):
            rgb_leds.set(i, [255, 0, 0] if i % 2 == frame % 2 else [0, 0, 255])
    elif led_mode == 10:
        for i in range(6):
            rgb_leds.set(i, [255, 0, 0] if i < 3 else [0, 0, 255])
        if frame % 10 < 5:
            rgb_leds.off()
    elif led_mode == 11:
        for i in range(6):
            level = max(0, 255 - abs(scanner_pos - i) * 80)
            rgb_leds.set(i, [level, 0, 0])
        scanner_pos += scanner_dir
        if scanner_pos >= 5 or scanner_pos <= 0:
            scanner_dir *= -1
    elif led_mode == 12:
        for i in range(6):
            r = 180 + urandom.getrandbits(6)
            g = 60 + urandom.getrandbits(5)
            rgb_leds.set(i, [r, g, 0])
    elif led_mode == 13:
        for i in range(6):
            rgb_leds.set(i, [0, (frame * 10 + i * 40) % 256, 0])
    elif led_mode == 14:
        for i in range(6):
            dist = abs(i - chase_index)
            brightness = max(0, 255 - dist * 85)
            rgb_leds.set(i, [brightness, 0, 0])
        chase_index = (chase_index + 1) % 6
    elif led_mode == 15:
        for i in range(6):
            offset = (hue + i * 60) % 360
            rgb_leds.set_hsv(i, [offset, 255, 255])
        hue = (hue + (5 if frame % 2 == 0 else -5)) % 360
    elif led_mode == 16:
        for i in range(6):
            if urandom.getrandbits(2) == 0:
                rgb_leds.set_hsv(i, [urandom.getrandbits(8), 255, 255])
            else:
                rgb_leds.set(i, [0, 0, 0])
    elif led_mode == 17:
        for i in range(6):
            val = int((1 + math.sin((frame + i * 4) / 8)) * 127)
            rgb_leds.set(i, [val, 255 - val, 0])
    elif led_mode == 18:
        for i in range(6):
            rgb_leds.set(i, [255, 255, 0] if i == frame % 6 else [0, 0, 0])
    elif led_mode == 19:
        for i in range(6):
            rgb_leds.set_hsv(i, [(-hue + i * 60) % 360, 255, 255])
        hue = (hue + 4) % 360

    rgb_leds.show()
    frame += 1

# === Main loop ===
while True:
    try:
        fb = display.load_pbm(images[index])
        display.fill(0)
        if flipped:
            flip_framebuffer_vertically(fb, display)
        else:
            display.blit(fb, 0, 0)
        display.show()
    except Exception as e:
        display.fill(0)
        display.text("Image error", 0, 20)
        display.text(str(e), 0, 30)
        display.show()

    while not button_a.check():
        if button_b.check():
            while button_b.check(): pass
            led_mode = (led_mode + 1) % 20

        if button_c.check():
            while button_c.check(): pass
            flipped = not flipped
            break

        update_leds()
        time.sleep_ms(40)

    while button_a.check(): pass
    index = (index + 1) % len(images)
