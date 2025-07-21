from PIL import Image  # Import Python Imaging Library

# === USER CONFIGURABLE SETTINGS ===
INPUT_FILE = "DEFCON.png"       # Path to input image (can be PNG, JPG, etc.)
OUTPUT_FILE = "splash.pbm"      # Output PBM file to generate
WIDTH = 128                     # Width of the target display (e.g., SH1106)
HEIGHT = 64                     # Height of the target display
# ==================================

def convert_image_to_custom_pbm(input_path, output_path, width=128, height=64):
    # Load image and convert to 1-bit black and white (mode "1")
    img = Image.open(input_path).convert("1")
    
    # Resize the image to the required dimensions
    img = img.resize((width, height))

    # Flatten the image pixels into a list (row-major)
    pixels = list(img.getdata())

    # Initialize bytearray to store the packed image bits
    packed = bytearray()

    # Pack the image pixels row by row, 8 pixels per byte
    for y in range(height):
        for x in range(0, width, 8):
            byte = 0
            for bit in range(8):
                idx = y * width + x + bit
                if idx < len(pixels) and pixels[idx] < 128:  # Black pixel threshold
                    byte |= 1 << (7 - bit)  # Set bit in MSB-first order
            packed.append(byte)

    # Write out the image in raw PBM (P4) format
    with open(output_path, "wb") as f:
        f.write(b"P4\n")                          # PBM binary magic number
        f.write(b"\n")                            # Extra newline for compatibility (important)
        f.write(f"{width} {height}\n".encode())   # Write dimensions
        f.write(packed)                           # Write packed bitmap data

# Run the conversion with the provided filenames and dimensions
convert_image_to_custom_pbm(INPUT_FILE, OUTPUT_FILE, WIDTH, HEIGHT)
