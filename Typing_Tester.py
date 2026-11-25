import time
import json
import usb_cdc
import usb_hid

from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS


# =====================================
# USB SERIAL CONNECTION
# =====================================

serial = usb_cdc.data

if serial is None:
    raise RuntimeError(
        "USB CDC data unavailable. Check boot.py configuration."
    )


# =====================================
# USB KEYBOARD SETUP
# =====================================

keyboard_device = None

for device in usb_hid.devices:
    if device.usage_page == 0x01 and device.usage == 0x06:
        keyboard_device = device
        break

if keyboard_device is None:
    raise RuntimeError("USB keyboard not found")

keyboard = Keyboard(keyboard_device)
layout = KeyboardLayoutUS(keyboard)


# =====================================
# SERIAL COMMUNICATION
# =====================================

buffer = bytearray()


def send_message(message):
    serial.write((message + "\n").encode("utf-8"))


# Tell Windows HackyPi is ready
send_message("HACKYPI_READY")


# =====================================
# MAIN PROGRAM
# =====================================

while True:

    if serial.in_waiting:

        incoming = serial.read(serial.in_waiting)
        buffer.extend(incoming)

        while b"\n" in buffer:

            line, _, remainder = buffer.partition(b"\n")
            buffer = bytearray(remainder)

            try:
                message = json.loads(line.decode("utf-8"))
                action = message.get("action")

                # Connection test
                if action == "ping":

                    send_message("READY")

                # Type supplied text
                elif action == "type":

                    text_to_type = message.get("text", "")
                    wpm = int(message.get("wpm", 40))

                    if not isinstance(text_to_type, str):
                        raise ValueError("Text must be a string")

                    wpm = max(10, min(100, wpm))
                    delay = 12 / wpm

                    send_message("STARTED")

                    # Give time to select the destination window
                    time.sleep(7)

                    for character in text_to_type:
                        layout.write(character)
                        time.sleep(delay)

                    send_message("COMPLETE")

            except Exception as error:

                send_message("ERROR: " + str(error))

    time.sleep(0.01)