# HELPER FUNCTIONS
#=========================================================================
# @file helperFunctions.py
#=========================================================================
# ABOUT:
# This file contains useful functions for the MTB DAQ. It was created 
# separately from 'main.py' for organizational purposes.
#=========================================================================
# WRITTEN BY: Steven Waal
# DATE: 05.28.2020
#=========================================================================
# NOTES:
# 05.28.2020 - File created (SRW)
# 06.11.2020 - Final comments added, code cleaned up
#=========================================================================
# COPYRIGHT:
# @copyright This program is copyrighted by Steven Waal and released under 
# the GNU Public License, version 3.0.
#=========================================================================










#=========================================================================
# FUNCTIONS
#=========================================================================
def clear_accel_buf(adxl375):
    '''This function clears the buffer of the @param adxl375 object. The 
    accelerometer should be put in standby mode before calling this
    function in order to prevent the bit from being set immediately 
    after.

    @return the number of values that were in the FIFO buffer'''


    count = 0

    # Empty buffers from sensors
    while (adxl375.get_FIFO_STATUS() & 0b00111111): # Loop until buffer is empty
        adxl375.get_x_acceleration()
        count += 1

    return count

def decode_data(file_count, adxl375):
        '''This function decodes the data written to 'log.bin' and saves it to a *.txt file'''

        # Create data file using file count
        dataFile = open('data' + str(file_count) +'.txt', 'w')
        # Write header of data file
        dataFile.write('{}, {}, {}, {}, {}, {}, {}'.format('TIME (sec)', 'X1_ACCEL (g)', 'Y1_ACCEL (g)', 'Z1_ACCEL (g)', 'X2_ACCEL (g)', 'Y2_ACCEL (g)', 'Z2_ACCEL (g)') + '\n')
       
        SCALE_FACTOR = adxl375.SCALE_FACTOR

        # Create variable to keep track of time
        time = 0 # Overall time that data was taken
        deltaTime = round((1/get_ODR(adxl375)), 6) # Difference in time from one data point to the next. Dependent on ODR of accelerometer. Rounded to 6 decimal places

        # Open binary data file
        try:
            logFile = open('log.bin', 'rb')
        except:
            print("ERROR: LOG FILE DOES NOT EXIST")

        while True:
            line = logFile.read(14) # Read 14 bytes at a time (2 bytes for two read command, 6 bytes for each accelerometer X, Y, Z data)

            if not line:
                break;

            # ADXL375_1
            X1_LSB = line[1]
            X1_MSB = line[2]
            Y1_LSB = line[3]
            Y1_MSB = line[4]
            Z1_LSB = line[5]
            Z1_MSB = line[6]

            X1_DATA = (X1_MSB << 8) + X1_LSB
            Y1_DATA = (Y1_MSB << 8) + Y1_LSB
            Z1_DATA = (Z1_MSB << 8) + Z1_LSB

            X1_ACCEL = twos_comp(X1_DATA, 16)*SCALE_FACTOR
            Y1_ACCEL = twos_comp(Y1_DATA, 16)*SCALE_FACTOR
            Z1_ACCEL = twos_comp(Z1_DATA, 16)*SCALE_FACTOR

            # ADXL375_2
            X2_LSB = line[8]
            X2_MSB = line[9]
            Y2_LSB = line[10]
            Y2_MSB = line[11]
            Z2_LSB = line[12]
            Z2_MSB = line[13]

            X2_DATA = (X2_MSB << 8) + X2_LSB
            Y2_DATA = (Y2_MSB << 8) + Y2_LSB
            Z2_DATA = (Z2_MSB << 8) + Z2_LSB

            X2_ACCEL = twos_comp(X2_DATA, 16)*SCALE_FACTOR
            Y2_ACCEL = twos_comp(Y2_DATA, 16)*SCALE_FACTOR
            Z2_ACCEL = twos_comp(Z2_DATA, 16)*SCALE_FACTOR

            dataFile.write('{}, {}, {}, {}, {}, {}, {}'.format(time, X1_ACCEL, Y1_ACCEL, Z1_ACCEL, X2_ACCEL, Y2_ACCEL, Z2_ACCEL) + '\n')

            time = time + deltaTime

        logFile.close() # Close file when finished

        dataFile.close() # Close file when finished

def twos_comp(val, bits):
    '''Computes the 2's complement value of @param val, a binary number of length @param bits. 
       @return The 2's complement value of @param val. The acceleration data stored in the registers
       is stored as 2's complement format. Therefore, this function is needed in order to properly 
       interpret the acceleration data from the accelerometer.
    '''
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val     = val - (1 << bits)        # compute negative value
    return val                         # return positive value as is


def get_ODR(adxl375):
    '''This function returns the output data rate of the desired
        ADXL375 object. This is used to determine the time associated
        with each data point.

        # Values for ODR based on the accelerometer datasheet
        ODR_3200HZ          = micropython.const(0b00001111)
        ODR_1600HZ          = micropython.const(0b00001110)
        ODR_800HZ           = micropython.const(0b00001101)
        ODR_400HZ           = micropython.const(0b00001100)
        ODR_200HZ           = micropython.const(0b00001011)
        ODR_100HZ           = micropython.const(0b00001010)
        ODR_50HZ            = micropython.const(0b00001001)
        ODR_25HZ            = micropython.const(0b00001000)
        ODR_12_5HZ          = micropython.const(0b00000111)
        ODR_6_25HZ          = micropython.const(0b00000110)
        ODR_3_13HZ          = micropython.const(0b00000101)
        ODR_1_56HZ          = micropython.const(0b00000100)
        ODR_0_78HZ          = micropython.const(0b00000011)
        ODR_0_39HZ          = micropython.const(0b00000010)
        ODR_0_20HZ          = micropython.const(0b00000001)
        ODR_0_10HZ          = micropython.const(0b00000000)
    '''
    
    ODR = (adxl375.get_BW_RATE() & 0b00001111) # The 4 LSB of this value correspond to the output data rate

    ODR_VALUES = [  [3200, 0b1111],
                    [1600, 0b1110],
                    [800, 0b1101],
                    [400, 0b1100],
                    [200, 0b1011],
                    [100, 0b1010],
                    [50, 0b1001],
                    [25, 0b1000],
                    [12.5, 0b0111],
                    [6.25, 0b0110],
                    [3.13, 0b0101],
                    [1.56, 0b0100],
                    [0.78, 0b0011],
                    [0.39, 0b0010],
                    [0.20, 0b0001],
                    [0.10, 0b0000]   ]

    for value in ODR_VALUES:
        if ODR == value[1]:
            return value[0]

    return False
