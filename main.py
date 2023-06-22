'''
code.py

SeaHawk Vertical Profiling Float Deck Receiver Code

Copyright (C) 2022-2023 Cabrillo Robotics Club

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Cabrillo Robotics Club
6500 Soquel Drive Aptos, CA 95003
cabrillorobotics@gmail.com
'''

# # # # # # # #
# CONSTANTS
# # # # # # # #

# LoRa Device ID for the Float Transceiver
FLOAT_LORA_ID = 18

# LoRa Device ID for the Deck Transceiver
DECK_LORA_ID = 28


# # # # # # # #
# IMPORTS
# # # # # # # #

# python hardware interfaces
import board
import busio
import digitalio
import os

import time
import adafruit_datetime as datetime

# lora radio library
import adafruit_rfm9x

# oled display library
import displayio
import terminalio
import adafruit_displayio_sh1107
from adafruit_display_text import label
from adafruit_display_shapes.rect import Rect

# BUTTONS!!!!!!!!!!!!!!
from digitalio import DigitalInOut, Direction, Pull


# # # # # # # #
# BUS SETUP
# # # # # # # #

# instantiate the spi interface
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# instantiate the i2c interface
i2c = board.I2C()

# LoRa Module Chip Select on Digital Pin 5
CS = digitalio.DigitalInOut(board.D5)

# LoRa Module Reset on Digital Pin 6
RESET = digitalio.DigitalInOut(board.D6)

# set the radio frequency to 915mhz (NOT 868)
RADIO_FREQ_MHZ = 915.0

# key A on the oled screen is on Digital Pin 9
KEY_A = DigitalInOut(board.D9)

# set digital pin 9 to input mode
KEY_A.direction = Direction.INPUT

# add a pull up resistor
KEY_A.pull = Pull.UP

#
# datetime setup
#

epoch = datetime.datetime(2023, 6, 22, 15, 35, 0) + datetime.timedelta(hours=+6)


# # # # # # # #
# LoRa Radio Feather SETUP
# # # # # # # #

# instantiate a rfm9x object
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)

# set my node ID
rfm9x.node = DECK_LORA_ID

# set the destination node
rfm9x.destination = FLOAT_LORA_ID


# # # # # # # #
# OLED Wing SETUP
# # # # # # # #

# reset display to cleanly handle soft reset
displayio.release_displays()

# instantiate a displayio display bus for the oled screen
display_bus = displayio.I2CDisplay(i2c, device_address=0x3c)

# instantiate the display
display = adafruit_displayio_sh1107.SH1107(
    display_bus, width=128, height=64, rotation=0
)

# create a layer for the header on the display
display_group = displayio.Group()
# show the layer on the display
display.show(display_group)


# # # # # # # #
# Display Header
# # # # # # # #

# draw outline for club name
display_group.append(
    Rect(
        0,
        0,
        128,
        16,
        fill=0x000000,
        outline=0xFFFFFF
    )
)


# # # # # # # #
# Wait for keypress to activate robot
# # # # # # # #

while True:

    # detect key press
    if not KEY_A.value:
        rfm9x.send(bytes("CABRILLO VPF DIVE", "utf-8"))
        break


# Draw the club name at the top of the display
display_group.append(
    label.Label(
        terminalio.FONT,
        text="Cabrillo Robotics",
        color=0xFFFFFF,
        x=14,
        y=8
    )
)



# # # # # # # #
# Receive data from radio and process it and display it
# # # # # # # #

while True:

    # listen for a packet
    packet = rfm9x.receive()

    if packet is None:
        pass
    else:
        # blank screen to display new packet
        try:
            display_group.pop(2)
        except:
            pass

        # process packet
        packet_list = packet.decode("utf-8").split()
        team_num = packet_list[0]
        time_rolling = int(packet_list[1])

        processed_packet = "TEAM: " + team_num + "\r\n" + str(epoch + datetime.timedelta(seconds=+time_rolling))

        # write packet data to screen
        display_group.append(
            label.Label(
                terminalio.FONT,
                text=str(processed_packet, "ascii"),
                color=0xFFFFFF,
                x=8,
                y=24
            )
        )
