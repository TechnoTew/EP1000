# library for rotary encoder
import rotaryio

# libraries for interfacing with the board
import board
import digitalio

# libraries for interfacing with the SSD1306 OLED Display
import displayio
import terminalio
import busio
import adafruit_displayio_ssd1306
from adafruit_display_text import bitmap_label

# switch debounce library
from adafruit_debouncer import Debouncer

# HID imports
import usb_hid
from adafruit_hid.keyboard import Keyboard
keyboard = Keyboard(usb_hid.devices)
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

# other imports
import time

# initialize display
displayio.release_displays()
i2c = busio.I2C(board.GP21, board.GP20)
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)

# Make the display context
screen = displayio.Group()
display.show(screen)

# setting up white header at top of screen
color_bitmap = displayio.Bitmap(128, 10, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0xFFFFFF  # White
header = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
screen.append(header)

# set global fontas the default terminalio font
font = terminalio.FONT

# variable to manage display
displayMaxWidth = 22

# variables to manage modes
modeTitleArray = ["Debug Mode", "Macro Pad", "Num Pad"]
currentMode = 1
modeSelect = False
modeInitialized = False

# initialize board as HID device
cc = ConsumerControl(usb_hid.devices)

# variables to configure debounce timing
rotaryEncoderSwitchDebounceInterval = 0.005
mechanicalSwitchDebounceInterval = 0.005

# variables to store the switch objects
keyPinArray = [board.GP1, board.GP2, board.GP3, board.GP4, board.GP5, board.GP6, board.GP7, board.GP8, board.GP9, board.GP10, board.GP11, board.GP12]
switchArray = []

# rotary encoder switch
rotaryPin = digitalio.DigitalInOut(board.GP18)
rotaryPin.direction = digitalio.Direction.INPUT
rotaryPin.pull = digitalio.Pull.UP
rotarySwitch = Debouncer(rotaryPin, interval=rotaryEncoderSwitchDebounceInterval)

# all 12 mechanical switches
for keyPin in keyPinArray:
    tempPin = digitalio.DigitalInOut(keyPin)
    tempPin.direction = digitalio.Direction.INPUT
    tempPin.pull = digitalio.Pull.UP
    tempSwitch = Debouncer(tempPin, interval=mechanicalSwitchDebounceInterval)
    switchArray.append(tempSwitch)

# configure rotary enconder
encoder = rotaryio.IncrementalEncoder(board.GP16, board.GP17)
encoderPosition = encoder.position
lastEncoderPosition = encoder.position

# function to clean the whole screen
def clearScreen():
    for _ in range(len(screen) - 1):
        screen.pop()

# main program loop
while True:
    try:
        # update all the switch with debounces
        rotarySwitch.update()
        for switch in switchArray:
            switch.update()

        # update rotary encoder position
        encoderPosition = encoder.position

        # mode selection mode
        if (modeSelect):
            if (not modeInitialized):
                modeInitialized = True
                # write the current mode on the screen initially
                modePadSide = (displayMaxWidth - len("Mode Select")) // 2
                screen.append(bitmap_label.Label(font, text="{}{}{}".format(modePadSide * " ",
    "Mode Select", modePadSide * " "), color=0x000000, x=0, y=4))
                screen.insert(1, bitmap_label.Label(font, text=" {}: {}".format(currentMode, modeTitleArray[currentMode]), color=0xFFFFFF, x=0, y=30))

        # debug mode
        elif (currentMode == 0):
            if (not modeInitialized):
                modeInitialized = True

                # write the current mode on the screen initially
                modePadSide = (displayMaxWidth - len(modeTitleArray[currentMode])) // 2
                screen.append(bitmap_label.Label(font, text="{}{}{}".format(modePadSide * " ",
    modeTitleArray[currentMode], modePadSide * " "), color=0x000000, x=0, y=4))
                screen.insert(1, bitmap_label.Label(font, text="Rotary Encoder: {}".format(encoderPosition), color=0xFFFFFF, x=0, y=15))
                screen.insert(2, bitmap_label.Label(font, text=" ", color=0xFFFFFF, x=0, y=25))
                screen.insert(3, bitmap_label.Label(font, text=" ", color=0xFFFFFF, x=0, y=35))
                screen.insert(4, bitmap_label.Label(font, text=" ", color=0xFFFFFF, x=0, y=45))
                screen.insert(5, bitmap_label.Label(font, text=" ", color=0xFFFFFF, x=0, y=55))

            for switchIndex in range(len(switchArray)):
                if (switchArray[switchIndex].fell or switchArray[switchIndex].rose):
                    if (switchIndex == 0 or switchIndex == 1 or switchIndex == 2):
                        screen.pop(2)
                        screen.insert(2, bitmap_label.Label(font, text="  {}   {}   {}  "
        .format("KEY1" if not switchArray[0].value else "    ", "KEY2" if not switchArray[1].value else "    ",
        "KEY3" if not switchArray[2].value else "    "), color=0xFFFFFF, x=0, y=29))

                    elif (switchIndex == 3 or switchIndex == 4 or switchIndex == 5):
                        screen.pop(3)
                        screen.insert(3, bitmap_label.Label(font, text="  {}   {}   {}  "
        .format("KEY4" if not switchArray[3].value else "    ", "KEY5" if not switchArray[4].value else "    ",
        "KEY6" if not switchArray[5].value else "    "), color=0xFFFFFF, x=0, y=39))

                    elif (switchIndex == 6 or switchIndex == 7 or switchIndex == 8):
                        screen.pop(4)
                        screen.insert(4, bitmap_label.Label(font, text="  {}   {}   {}  "
        .format("KEY7" if not switchArray[6].value else "    ", "KEY8" if not switchArray[7].value else "    ",
        "KEY9" if not switchArray[8].value else "    "), color=0xFFFFFF, x=0, y=49))

                    elif (switchIndex == 9 or switchIndex == 10 or switchIndex == 11):
                        screen.pop(5)
                        screen.insert(5, bitmap_label.Label(font, text=" {}   {}   {}  "
        .format("KEY10" if not switchArray[9].value else "    ", "KEY11" if not switchArray[10].value else "    ",
        "KEY12" if not switchArray[11].value else "    "), color=0xFFFFFF, x=0, y=59))
                    else:
                        pass

        # function mode
        elif (currentMode == 1):
            if (not modeInitialized):
                modeInitialized = True

                # write the current mode on the screen initially
                modePadSide = (displayMaxWidth - len(modeTitleArray[currentMode])) // 2
                screen.append(bitmap_label.Label(font, text="{}{}{}".format(modePadSide * " ",
    modeTitleArray[currentMode], modePadSide * " "), color=0x000000, x=0, y=4))

                screen.append(bitmap_label.Label(font, text="Stream MicMute Deafen", color=0xFFFFFF, x=0, y=20))
                screen.append(bitmap_label.Label(font, text="PrtScn VolMute ConTxt", color=0xFFFFFF, x=0, y=32))
                screen.append(bitmap_label.Label(font, text="BRIDOWN BRIUP Project   ", color=0xFFFFFF, x=0, y=44))
                screen.append(bitmap_label.Label(font, text="   <    Play     >   ", color=0xFFFFFF, x=0, y=56))

            # detecting switch presses
            for switchIndex in range(len(switchArray)):
                if (switchArray[switchIndex].fell):
                    if (switchIndex == 0):
                        keyboard.send(Keycode.F13)
                    elif (switchIndex == 1):
                        keyboard.send(Keycode.F14)
                    elif (switchIndex == 2):
                        keyboard.send(Keycode.F15)
                    elif (switchIndex == 3):
                        keyboard.send(Keycode.PRINT_SCREEN)
                    elif (switchIndex == 4):
                        cc.send(ConsumerControlCode.MUTE)
                    elif (switchIndex == 5):
                        keyboard.send(Keycode.APPLICATION)
                    elif (switchIndex == 6):
                        cc.send(ConsumerControlCode.BRIGHTNESS_DECREMENT)
                    elif (switchIndex == 7):
                        cc.send(ConsumerControlCode.BRIGHTNESS_INCREMENT)
                    elif (switchIndex == 8):
                        keyboard.send(Keycode.GUI, Keycode.P)
                    elif (switchIndex == 9):
                        cc.send(ConsumerControlCode.SCAN_PREVIOUS_TRACK)
                    elif (switchIndex == 10):
                        cc.send(ConsumerControlCode.PLAY_PAUSE)
                    elif (switchIndex == 11):
                        cc.send(ConsumerControlCode.SCAN_NEXT_TRACK)
                    else:
                        pass

        # numpad mode
        elif (currentMode == 2):
            if (not modeInitialized):
                modeInitialized = True

                # write the current mode on the screen initially
                modePadSide = (displayMaxWidth - len(modeTitleArray[currentMode])) // 2
                screen.append(bitmap_label.Label(font, text="{}{}{}".format(modePadSide * " ",
    modeTitleArray[currentMode], modePadSide * " "), color=0x000000, x=0, y=4))

                screen.append(bitmap_label.Label(font, text="   9      8      7", color=0xFFFFFF, x=0, y=20))
                screen.append(bitmap_label.Label(font, text="   4      5      6", color=0xFFFFFF, x=0, y=32))
                screen.append(bitmap_label.Label(font, text="   1      2      3", color=0xFFFFFF, x=0, y=44))
                screen.append(bitmap_label.Label(font, text="   .      0    Enter", color=0xFFFFFF, x=0, y=56))

            # detecting switch presses
            for switchIndex in range(len(switchArray)):
                if (switchArray[switchIndex].fell):
                    if (switchIndex == 0):
                        keyboard.send(Keycode.SEVEN)
                    elif (switchIndex == 1):
                        keyboard.send(Keycode.EIGHT)
                    elif (switchIndex == 2):
                        keyboard.send(Keycode.NINE)
                    elif (switchIndex == 3):
                        keyboard.send(Keycode.FOUR)
                    elif (switchIndex == 4):
                        keyboard.send(Keycode.FIVE)
                    elif (switchIndex == 5):
                        keyboard.send(Keycode.SIX)
                    elif (switchIndex == 6):
                        keyboard.send(Keycode.ONE)
                    elif (switchIndex == 7):
                        keyboard.send(Keycode.TWO)
                    elif (switchIndex == 8):
                        keyboard.send(Keycode.THREE)
                    elif (switchIndex == 9):
                        keyboard.send(Keycode.PERIOD)
                    elif (switchIndex == 10):
                        keyboard.send(Keycode.ZERO)
                    elif (switchIndex == 11):
                        keyboard.send(Keycode.ENTER)
                    else:
                        pass
        else:
            pass

        # executes if the encoder position has changed
        if (encoderPosition != lastEncoderPosition):
            if (modeSelect):
                currentMode = (currentMode + 1) % 3 if (encoderPosition - lastEncoderPosition > 0) else (currentMode + len(modeTitleArray) - 1) % 3
                screen.pop(1)
                screen.insert(1, bitmap_label.Label(font, text=" {}: {}".format(currentMode, modeTitleArray[currentMode]), color=0xFFFFFF, x=0, y=30))
            elif (currentMode == 0):
                screen.pop(1)
                screen.insert(1, bitmap_label.Label(font, text="Rotary Encoder: {}".format(encoderPosition), color=0xFFFFFF, x=0, y=15))
            elif (currentMode == 1):
                # code to adjust volume
                positionChange = encoderPosition - lastEncoderPosition
                if positionChange > 0:
                    for _ in range(positionChange):
                        cc.send(ConsumerControlCode.VOLUME_INCREMENT)
                elif positionChange < 0:
                    for _ in range(-positionChange):
                        cc.send(ConsumerControlCode.VOLUME_DECREMENT)
            elif (currentMode == 2):
                pass

        lastEncoderPosition = encoderPosition

        # if the switch is rotary encoder switch short circuit loop as it always is used to switch to another mode
        if (rotarySwitch.fell):
            modeSelect = not modeSelect
            modeInitialized = False

            # wipe the screen
            clearScreen()

            # skip to the next iteration of the loop
            continue
    except Exception as e:
        print(e)
        print("Error")
        pass
