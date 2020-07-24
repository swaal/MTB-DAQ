# MAIN 
#=========================================================================
# @file main.py
#=========================================================================
# ABOUT:
# This code runs a simple data acquisition system on the MTB-DAQ v2.2 
# board running Micropython PYBv1.1 version 1.12 firmware. The code
# records data from two ADXL375BCCZ accelerometers at 1600Hz over SPI and
# writes the data to binary file on a Micro SD card.
#=========================================================================
# WRITTEN BY: Steven Waal
# DATE: 05.28.2019
#=========================================================================
# NOTES:
# 05.28.2019 - File created (SRW)
# 06.07.2019 - Updated to use SPI bus no. 2 instead of no. 1 (not sure why
#              but for some reason SPI bus no. 1 is not working properly)
# 01.29.2020 - Implemented RTOS system
# 02.12.2020 - Implemented display and SD card tasks.
# 02.12.2020 - Having trouble with timing. I can't get faster than 5msec 
#              between measurements. I tried moving the record state for
#              each task to the very top (to minimize if statements it 
#              takes to get there) but that didn't do too much.
# 02.19.2020 - Implemented code to support ISR
# 03.10.2020 - Changed over to PyBoard. Update pinouts and code to check
#              presence of micro SD card.
# 05.23.2020 - Adapted code to work with MTB DAQ v2.2 main board.
# 06.11.2020 - Final comments added, code cleaned up
#=========================================================================
# COPYRIGHT:
# @copyright This program is copyrighted by Steven Waal and released under 
# the GNU Public License, version 3.0.
#=========================================================================










#=========================================================================
# MISC. NOTES
#=========================================================================
# - There is a completely blank file called "SKIPSD" that is loaded onto 
#   the board. This prompts the microcontroller to boot from the
#   the internal flash instead of the SD card when an SD card is inserted
#   before powering on.










#=========================================================================
# IMPORT MODULES
#=========================================================================
# Import modules for use in this file. Note that there are certain modules
# that automatically come with downloading micropython onto the board. To
# see a list of these modules, type help("modules") in the REPL. This will
# return a list of the available modules. Custom modules can be added by
# saving them as separate *.py files, uploading them to the board, and 
# referring to them here.

# HARDWARE MODULES
from ADXL375_driver import ADXL375
from ht16k33_seg import Seg14x4

# # GENERAL MICROPYTHON MODULES
import micropython, pyb, utime, gc, machine, os

# MISC.
from helperFunctions import clear_accel_buf
from helperFunctions import decode_data
from helperFunctions import twos_comp
from helperFunctions import get_ODR










#=========================================================================
# ALLOCATE MEMORY FOR ERROR REPORTS
#=========================================================================
# According to Micropython docs, "If an error occurs in an ISR, 
# MicroPython is unable to produce an error report unless a special buffer
# is created for the purpose. Debugging is simplified if the following 
# code is included in any program using interrupts."

micropython.alloc_emergency_exception_buf(100)










#=========================================================================
# DEFINE ACCELEROMETER PARAMETERS
#=========================================================================
# Determines how many data points are stored in the FIFO buffer before an 
# an interrupt is generatred. Maximum is 32.
FIFO_BUFF_COUNT     = micropython.const(20)










#=========================================================================
# DEFINE BUFFERS
#=========================================================================
CMD_RD      = bytearray((0b11110010, 0, 0, 0, 0, 0, 0)) # ADXL375_1. Command to read multiple bytes starting with X data
buf1_7      = bytearray(7) # Buffer of ADXL375_1. Make buffer large enough to read data from X, Y, and Z
buf2_7      = bytearray(7) # Buffer of ADXL375_2. Make buffer large enough to read data from X, Y, and Z










#=========================================================================
# CREATE PIN OBJECTS
#=========================================================================
# Create pin objects. Pins are labeled according to the MTB DAQ v2.2 main 
# board schematic.

# SD chip detect pin
CD                      = pyb.Pin(pyb.Pin.cpu.A8, pyb.Pin.IN, pyb.Pin.PULL_UP) # Enables the chip detect pin with internal pull up resistor
# ADXL375 1 chip select pin
SPI1_CS1                = pyb.Pin(pyb.Pin.cpu.A0, pyb.Pin.OUT)
# ADXL375 2 chip select pin
SPI1_CS2                = pyb.Pin(pyb.Pin.cpu.A1, pyb.Pin.OUT)
# Record Button
REC_BTN                 = pyb.Pin(pyb.Pin.cpu.B3, pyb.Pin.IN)
# Record LED
REC_LED                 = pyb.Pin(pyb.Pin.cpu.C4, pyb.Pin.OUT)
# Interrupt Pin
ADXL1_INT1              = pyb.Pin(pyb.Pin.cpu.C0, pyb.Pin.IN, pyb.Pin.PULL_DOWN) # Set internal pull-up resistor so we always know state of pin when not in use










#=========================================================================
# CREATE DISPLAY OBJECT
#=========================================================================
#Create display object. Default to off.
Display = Seg14x4(machine.I2C(1))
Display.text('    ') # Clears display
Display.show()










#=========================================================================
# INITIAL CHECK IF SD CARD IS PRESENT
#=========================================================================
# If SD card is not present, program waits until user inserts one and flashes "SD" on the display.
# Once the SD card is present, the proper files and directories are created if they have been erased.

# If SD is not detected, flash "SD" on the display.
if CD.value():
    Display.text('  SD')
    Display.blink_rate(2)
    Display.show()

# Wait for user to insert SD card if not already done.
while CD.value():
    # Make display LEDs blink. This will hold up the program and ensure that the SD card is mounted before continuing.
    utime.sleep_ms(100)

# Clear display once SD card has been inserted.
utime.sleep(3)
Display.text('    ') # Clears display
Display.blink_rate(0)
Display.show()

try:
    # Once user has inserted SD card, mount it.
    os.mount(pyb.SDCard(), '/sd')
except:
    Display.text('OFF ')
    Display.blink_rate(2)
    Display.show()

# Remake 'log' directory if it has been erased. If not, ignore error
try:
    os.mkdir('/sd/log')
except:
    pass

# Remake 'count' directory if it has been erased. If not, ignore error
try:
    os.mkdir('/sd/count')
except:
    pass

# Check if 'count.txt' was erased. If it was, remake it
try:
    file = open('/sd/count/count.txt', 'x') # The 'x' argument indicates that if the file already exists, through an error
    file.write('0\n')
    file.close()
except:
    pass

# Change directory to SD card to prepare for writing files to it
os.chdir('/sd/log')










#=========================================================================
# CREATE SPI OBJECT
#=========================================================================
# Create SPI object in order to use the spi protocol

# Set baudrate to maximum of 5 MHz
# Set polarity and phase as specified by sensor datasheets.
spi_1 = pyb.SPI(1, pyb.SPI.MASTER, baudrate=5000000, polarity=1, phase=1, bits=8, firstbit=pyb.SPI.MSB)










#=========================================================================
# CREATE ADXL375 ACCELEROMETER OBJECTS AND CONFIGURE SETTINGS
#=========================================================================
# **************************
# *****ADXL375 1 OBJECT*****
# **************************
ADXL375_1 = ADXL375(spi_1, SPI1_CS1)
ADXL375_1.standby() # puts accelerometer in standby mode. this is necessary to configure it
# DATA RATE AND POWER MODE CONTROL
ADXL375_1.odr(ADXL375_1.ODR_1600HZ) # sets data rate to 1600 HZ
ADXL375_1.normal_power_mode()
# DATA FORMAT
ADXL375_1.spi_4_wire()
ADXL375_1.right_justify()
# SETUP INTERRUPTS
ADXL375_1.int_disable(ADXL375_1.Watermark_enable) # Make sure interrupts are disabled before configuring as per datasheet
ADXL375_1.FIFO_Mode_FIFO() # Configures the FIFO buffer to operate in FIFO mode
ADXL375_1.trigger_int1() # Configures the interrupt to pin INT1
ADXL375_1.interrupt_active_high() # Configures the interrupt to be active high
ADXL375_1.set_samples(FIFO_BUFF_COUNT) # Sets the number of samples before the watermark bit is set

# **************************
# *****ADXL375 2 OBJECT*****'
# **************************
ADXL375_2 = ADXL375(spi_1, SPI1_CS2)
ADXL375_2.standby() # Puts accelerometer in standby mode. this is necessary to configure it
# DATA RATE AND POWER MODE CONTROL
ADXL375_2.odr(ADXL375_2.ODR_1600HZ) # Sets data rate to 1600 HZ
ADXL375_2.normal_power_mode()
# DATA FORMAT
ADXL375_2.spi_4_wire()
ADXL375_2.right_justify()










#=========================================================================
# GET FILE COUNT
#=========================================================================
print('GET FILE COUNT')
print()

countFile = open('/sd/count/count.txt', 'r')
last_line = int(countFile.readlines()[-1])
file_count = last_line
countFile.close()










#=========================================================================
# INITIALIZE RECORD LED AND CLEAR DISPLAY
#=========================================================================
print('INITIALIZE RECORD LED AND CLEAR DISPLAY')
print()

# Turn off record LED
REC_LED.value(1)
# Clear display
Display.text('    ') # Clears current text/numbers on display
Display.number(file_count) # Prints the desired number
Display.blink_rate(0)
Display.show() # Updates the display










while True:

    #=========================================================================
    # WAIT FOR INPUT FROM RECORD SWITCH
    #=========================================================================
    print('WAITING FOR INPUT...')
    print()

    while REC_BTN.value() == True: # Wait for user to press button
        pass
    while REC_BTN.value() == False: # Wait for user to let go of button
        pass










    #=========================================================================
    # BEGIN RECORDING
    #=========================================================================
    print('RECORDING')
    print()

    # Turn on record LED
    REC_LED.value(0)
    # Increment file count and save to count file
    file_count += 1 # Increment file count
    countFile = open('/sd/count/count.txt', 'a')
    countFile.write(str(file_count) + "\n")
    countFile.close()

    # Update the display
    Display.text('    ') # Clears current text/numbers on display
    Display.number(file_count) # Prints the desired number
    Display.blink_rate(0)
    Display.show() # Updates the display

    # Clear the accelerometer buffer. Make sure it is in standby mode first
    ADXL375_1.standby()
    clear_accel_buf(ADXL375_1)
    ADXL375_2.standby()

    # Create the data file.
    file = open('data' + str(file_count) +'.bin', 'wb')










    #=========================================================================
    # RECORDING!
    #=========================================================================
    # Enable interrupts and start measuring!
    ADXL375_1.int_enable(ADXL375_1.Watermark_enable)
    ADXL375_1.measure()
    ADXL375_2.measure()

    while REC_BTN.value() == True: # Wait for user to press button
        while ADXL1_INT1.value() == False: # If the INT1 pin is low, wait for accelerometer to collect more data
            pass
        for i in range(FIFO_BUFF_COUNT): # Store values onto SD card in 'log.bin' file
            SPI1_CS1.low(); spi_1.send_recv(CMD_RD, buf1_7); SPI1_CS1.high() # Read ADXL375_1
            SPI1_CS2.low(); spi_1.send_recv(CMD_RD, buf2_7); SPI1_CS2.high() # Read ADXL375_2
            file.write(buf1_7) # Write data to log.bin
            file.write(buf2_7) # Write data to log.bin
    while REC_BTN.value() == False: # Wait for user to let go of button
        pass










    #=========================================================================
    # DONE RECORDING!
    #=========================================================================
    print('DONE RECORDING')
    print()

    # Close data file
    file.close()

    # Turn off accelerometer
    ADXL375_1.standby()
    ADXL375_2.standby()

    # Turn off record LED
    REC_LED.value(1)

    print('FINISHED')
    print()

    Display.text('    ') # Clears current text/numbers on display
    Display.number(file_count) # Prints the desired number
    Display.blink_rate(0)
    Display.show() # Updates the display










