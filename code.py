import board
import digitalio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
import time

try:
    from typing import List, Tuple
except ImportError:
    # typing is not available at runtime
    pass

WAIT_TIME = 0.01  # seconds


class Button:
    """A button is a GPIO pin associated with a list of keycodes."""

    def __init__(self, pin: digitalio.DigitalInOut, *keycodes: Tuple[Keycode]):
        self.pin = pin
        self.pin.direction = digitalio.Direction.INPUT
        self.pin.pull = digitalio.Pull.UP
        self.keycodes = keycodes

    def wait_for_release(self):
        # Wait for the meatbag to release the button
        while self.pin.value is False:
            time.sleep(WAIT_TIME)


class Keymasher:
    """A class that acts a keyboard and sends keycodes when buttons are pressed."""

    DEBOUNCE_TIME = 0.2  # seconds

    def __init__(self, keyboard: Keyboard, buttons: List[Button]):
        self.keyboard = keyboard
        self.buttons = buttons

    def send_keys(self, *keycodes: Tuple[Keycode]):
        # Press the keys and release them
        self.keyboard.press(*keycodes)
        time.sleep(self.DEBOUNCE_TIME)
        self.keyboard.release_all()

    def loop(self):
        # listen for button presses
        while True:
            for button in self.buttons:
                if button.pin.value is False:
                    self.send_keys(*button.keycodes)
                    button.wait_for_release()
            time.sleep(WAIT_TIME)


keyboard = Keyboard(usb_hid.devices)

# Buttons that correspond to Google Meet shortcuts
buttons = [
    # mute/unmute microphone
    Button(digitalio.DigitalInOut(board.GP15), Keycode.COMMAND, Keycode.D),
    # turn on/off camera
    Button(digitalio.DigitalInOut(board.GP14), Keycode.COMMAND, Keycode.E),
    # raise/lower hand
    Button(
        digitalio.DigitalInOut(board.GP16),
        Keycode.CONTROL,
        Keycode.COMMAND,
        Keycode.H,
    ),
    # close tab
    Button(digitalio.DigitalInOut(board.GP17), Keycode.COMMAND, Keycode.W),
]

masher = Keymasher(keyboard, buttons)
masher.loop()
