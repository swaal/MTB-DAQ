# ADXL375 DRIVER 
#=========================================================================
# @file ADXL375_driver.py
#=========================================================================
# ABOUT:
# This code implements a driver for the ADXL375BCCZ-ND accelerometer. More
# information about the accelerometer and links to the datasheets can be 
# found here: https://www.digikey.com/product-detail/en/analog-devices-inc/ADXL375BCCZ/ADXL375BCCZ-ND/4376342
#=========================================================================
# WRITTEN BY: Steven Waal
# DATE: 05.28.2019
#=========================================================================
# NOTES:
# 05.28.2019 - File created (SRW)
# 06.07.2019 - Added more constants and fixed read/write methods
# 09.07.2019 - Added more bit masks/constants. Added more functions.
# 03.05.2020 - Added functions to configure interrupts and FIFO buffer.
# 06.11.2020 - Final comments added, code cleaned up
#=========================================================================
# SCHEMATIC:
# The axes of the ADXL375 are configured as follows(note the mark in the 
# upper right hand corner)                                                                        
#                                                                         
#                                                                         
#      Z AXIS                                                                     
#        |                                                     
#        |           Y AXIS                                                         
#        |          /     ___________________________________                                                     
#        |         /     /                                  /|                                      
#        |        /     /                              *   / |                                      
#        |       /     /                                  / /                                       
#        |      /     /                                  / /                                     
#        |     /     /                                  / /                                         
#        |    /     /                                  / /                                          
#        |   /     /                                  / /                                           
#        |  /     /__________________________________/ /                                                             
#        | /      |__________________________________|/                                                              
#        |/                                                                     
#        |_________________________________________________________ X AXIS                                                                     
#
#
#
#=========================================================================
# COPYRIGHT:
# @copyright This program is copyrighted by Steven Waal and released under 
# the GNU Public License, version 3.0.
#=========================================================================










#=========================================================================
# IMPORT MODULES
#=========================================================================
import micropython
#from pyb import SPI










#=========================================================================
# CLASS DEFINITION
#=========================================================================
class ADXL375:
    ''' This class defines a driver for the Analog Devices ADXL375BCCZ-ND accelerometer.'''

    #=========================================================================
    # CONSTANTS
    #=========================================================================
    # -------------------------------------
    # GENERAL
    # -------------------------------------
    SCALE_FACTOR        = 0.0488            # [g/LSB]

    # -------------------------------------
    # BIT MASKS
    # -------------------------------------
    # These masks are used to set reading and writing protocols.
    READ_MASK           = const(0b10000000)
    WRITE_MASK          = const(0b00000000)
    READ_2_BYTES_MASK   = const(0b01000000)

    # -------------------------------------
    # REGISTER MAP (page 20 of datasheet)
    # -------------------------------------
    # All registers in the ADXL375 are eight bits in length.
    DEVID               = 0x00              # Device ID
    # Reserved            0x01 to 0x1C      # Reserved; do not access
    THRESH_SHOCK        = 0x1D              # Shock threshold
    OFSX                = 0x1E              # X-axis offset
    OFSY                = 0x1F              # Y-axis offset
    OFSZ                = 0x20              # Z-axis offset
    DUR                 = 0x21              # Shock duration
    Latent              = 0x22              # Shock latency
    Window              = 0x23              # Shock window
    THRESH_ACT          = 0x24              # Activity threshold
    THRESH_INACT        = 0x25              # Inactivity threshold
    TIME_INACT          = 0x26              # Inactivity time
    ACT_INACT_CTL       = 0x27              # Axis enable control for activity and inactivity detection
    SHOCK_AXES          = 0x2A              # Axis control for single shock/double shock
    ACT_SHOCK_STATUS    = 0x2B              # Source of single shock/double shock
    BW_RATE             = 0x2C              # Data rate and power mode control
    POWER_CTL           = 0x2D              # Power saving features control
    INT_ENABLE          = 0x2E              # Interrupt enable control
    INT_MAP             = 0x2F              # Interrupt mapping control
    INT_SOURCE          = 0x30              # Interrupt source
    DATA_FORMAT         = 0x31              # Data format control
    DATAX0              = 0x32              # X-axis Data 0
    DATAX1              = 0x33              # X-axis Data 1
    DATAY0              = 0x34              # Y-axis Data 0
    DATAY1              = 0x35              # Y-axis Data 1
    DATAZ0              = 0x36              # Z-axis Data 0
    DATAZ1              = 0x37              # Z-axis Data 1
    FIFO_CTL            = 0x38              # FIFO control
    FIFO_STATUS         = 0x39              # FIFO status

    # -------------------------------------
    # REGISTER BIT DESCRIPTIONS
    # -------------------------------------
    # These constants define either bit masks for individual bits in each
    # register, or constant values that can be used to set various settings
    # in the register.

    # Register 0x27—ACT_INACT_CTL (Read/Write) bits
    ACT_AC_DC           = micropython.const(0b10000000)
    ACT_X_enable        = micropython.const(0b01000000)
    ACT_Y_enable        = micropython.const(0b00100000)
    ACT_Z_enable        = micropython.const(0b00010000)
    INACT_AC_DC         = micropython.const(0b00001000)
    INACT_X_enable      = micropython.const(0b00000100)
    INACT_Y_enable      = micropython.const(0b00000010)
    INACT_Z_enable      = micropython.const(0b00000001)

    # Register 0x2A—SHOCK_AXES (Read/Write) bits
    Suppress            = micropython.const(0b00001000)
    SHOCK_X             = micropython.const(0b00000100)
    SHOCK_Y             = micropython.const(0b00000010)
    SHOCK_Z             = micropython.const(0b00000001)     

    # Register 0x2B-ACT_SHOCK_STATUS (Read only) bits
    ACT_X_source        = micropython.const(0b01000000)
    ACT_Y_source        = micropython.const(0b00100000)
    ACT_Z_source        = micropython.const(0b00010000)
    Asleep              = micropython.const(0b00001000)
    SHOCK_X_source      = micropython.const(0b00000100)
    SHOCK_Y_source      = micropython.const(0b00000010)
    SHOCK_Z_source      = micropython.const(0b00000001)

    # Register 0x2C—BW_RATE (Read/Write) bits
    LOW_POWER           = micropython.const(0b00010000)
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

    # Register 0x2D-POWER_CTL (Read/Write) bits
    Link                = micropython.const(0b00100000)
    AUTO_SLEEP          = micropython.const(0b00010000)
    Measure             = micropython.const(0b00001000)
    Sleep               = micropython.const(0b00000100)
    Wakeup_8HZ          = micropython.const(0b00000000)
    Wakeup_4HZ          = micropython.const(0b00000001)
    Wakeup_2HZ          = micropython.const(0b00000010)
    Wakeup_1HZ          = micropython.const(0b00000011)

    # Register 0x2E-INT_ENABLE (Read/Write) bits
    DATA_READY_enable   = micropython.const(0b10000000)
    SINGLE_SHOCK_enable = micropython.const(0b01000000)
    DOUBLE_SHOCK_enable = micropython.const(0b00100000)
    Activity_enable     = micropython.const(0b00010000)
    Inactivity_enable   = micropython.const(0b00001000)
    Watermark_enable    = micropython.const(0b00000010)
    Overrun_enable      = micropython.const(0b00000001) 

    # Register 0x2F-INT_MAP (Read/Write) bits
    DATA_READY_map      = micropython.const(0b10000000)
    SINGLE_SHOCK_map    = micropython.const(0b01000000)
    DOUBLE_SHOCK_map    = micropython.const(0b00100000)
    Activity_map        = micropython.const(0b00010000)
    Inactivity_map      = micropython.const(0b00001000)
    Watermark_map       = micropython.const(0b00000010)
    Overrun_map         = micropython.const(0b00000001)    

    # Register 0x30-INT_SOURCE (Read only) bits
    DATA_READY_source   = micropython.const(0b10000000)
    SINGLE_SHOCK_source = micropython.const(0b01000000)
    DOUBLE_SHOCK_source = micropython.const(0b00100000)
    Activity_source     = micropython.const(0b00010000)
    Inactivity_source   = micropython.const(0b00001000)
    Watermark_source    = micropython.const(0b00000010)
    Overrun_source      = micropython.const(0b00000001)    

    # Register 0x31-DATA_FORMAT (Read/Write) bits
    SELF_TEST           = micropython.const(0b10000000)
    SPI                 = micropython.const(0b01000000)
    INT_INVERT          = micropython.const(0b00100000)
    Justify             = micropython.const(0b00000100)

    # Register 0x38-FIFO_CTL (Read/Write) bits
    FIFO_MODE_Bypass    = micropython.const(0b00000000)
    FIFO_MODE_FIFO      = micropython.const(0b01000000)
    FIFO_MODE_Stream    = micropython.const(0b10000000)
    FIFO_MODE_Trigger   = micropython.const(0b11000000)
    Trigger             = micropython.const(0b00100000)

    # Register 0x39-FIFO_STATUS (Read only) bits
    FIFO_TRIG           = micropython.const(0b10000000)



    # -------------------------------------
    # CONSTRUCTOR
    # -------------------------------------
    def __init__(self, spi, CS_pin):
        ''' Constructor for an ADXL375BCCZ-ND object.
            @param spi the spi bus object used for communication with the accelerometer
        '''

        self.spi     = spi
        self.CS_pin  = CS_pin
        self.buf     = bytearray(2) # Buffer used to store values when reading/writing to sensor
        self.buf_2   = bytearray(3) # Buffer used to store values from multi-reading

        self.CS_pin.high() # CS pin needs to idle high







    # -------------------------------------
    # UTILITY FUNCTIONS
    # -------------------------------------
    def mem_read(self, mem_addr):
        '''This function reads data from the address specified by @param mem_addr and stores
            it in the second byte of @param buf.
        '''
        # Sets proper bit in order to read data
        self.buf[0] = (mem_addr | self.READ_MASK)
        self.buf[1] = 0b00000000 # Set a value just to maintain order of buffer


        self.CS_pin.low()
        self.spi.send_recv(self.buf, self.buf)
        self.CS_pin.high()

    def mem_read_2bytes(self, mem_addr):
        '''This function reads two consequetive bytes of data starting from the address specified
            @param mem_addr. The value is stored in the last two bytes of @param buf_2
        '''

        # Sets proper bit in order to read data
        self.buf_2[0] = (mem_addr | self.READ_MASK | self.READ_2_BYTES_MASK)

        self.CS_pin.low()
        self.spi.send_recv(self.buf_2, self.buf_2)
        self.CS_pin.high()

    def mem_write(self, mem_addr, data):
        '''This function writes the data given by @param data to the memory address specified by
            @param mem_addr. Note that @param data must be 1 byte.
        '''

        # Save desired address to write to in @param buf.
        self.buf[0] = mem_addr
        self.buf[1] = data

        self.CS_pin.low()
        self.spi.send(self.buf)
        self.CS_pin.high()

    def twos_comp(self, val, bits):
        '''Computes the 2's complement value of @param val, a binary number of length @param bits. 
           @return The 2's complement value of @param val. The acceleration data stored in the registers
           is stored as 2's complement format. Therefore, this function is needed in order to properly 
           interpret the acceleration data from the accelerometer.
        '''
        if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
            val     = val - (1 << bits)        # compute negative value
        return val                         # return positive value as is




    # -------------------------------------
    # FUNCTIONS
    # -------------------------------------
    def config(self, data_rate, power_mode):
        '''config'''

        self.standby() #Puts the sensor in standby mode in order to configure

        # Sets data rate
        reg_value   = self.get_BW_RATE()  # Read current register value
        data        = reg_value | data_rate
        self.set_BW_RATE(data)


    # -------------------------------------
    # DATA RATE AND POWER MODE CONTROL
    # Register 0x2C—BW_RATE (Read/Write) bits
    # -------------------------------------
    def low_power_mode(self):
        '''This function puts the ADXL375 into low power mode. Note that low power mode has
            somewhat higher noise. Low power mode is only recommended for the following 
            output data rates: 400Hz, 200Hz, 100Hz, 50Hz, 25Hz, 12.5Hz. For output data rates
            not listed here, the use of low power mode does not provide any advantages.
        '''
        reg_value   = self.get_BW_RATE() # Read current register value
        data        = reg_value | self.LOW_POWER   # Set LOW_POWER bit to 1
        self.set_BW_RATE(data)

    def normal_power_mode(self):
        '''This function puts the ADXL375 into normal power mode. This is the default mode
            the device is set to upon start up.'''
        reg_value   = self.get_BW_RATE()  # Read current register value
        data        = reg_value & ~self.LOW_POWER   # Set LOW_POWER bit to 0
        self.set_BW_RATE(data)

    def odr(self, odr):
        '''This function sets the output data rate of the ADXL375. @param odr the desired 
            output data. This value must be chosen according to the possiblities listed in
            Table 6 of the datasheet and summarized as constants above with the following values:
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
        reg_value   = self.get_BW_RATE()
        reg_value   = (reg_value>>4)  # Shift right 4 bits
        reg_value   = (reg_value<<4)  # Shift left 4 bits. The combination of the line above and this one clears the lowest 4 bits.
        data        = reg_value | odr      # Apply desired bitmask
        self.set_BW_RATE(data)


    # -------------------------------------
    # POWER SAVING FEATURES CONTROL
    # Register 0x2D-POWER_CTL (Read/Write) bits
    # -------------------------------------
    def standby(self):
        '''This function puts the ADXL375 into standby mode. The device must be placed in standby
            mode before configuring different settings.'''
        reg_value   = self.get_POWER_CTL()
        temp_data   = (reg_value & ~self.Measure) # Sets the Measure bit to 0
        self.set_POWER_CTL(temp_data)

    def measure(self):
        '''This function puts the ADXL375 into measurement mode.'''
        reg_value   = self.get_POWER_CTL()
        data        = reg_value | self.Measure # Sets the Measure bit to 1
        self.set_POWER_CTL(data)
   

    # -------------------------------------
    # INTERRUPT ENABLE CONTROL
    # Register 0x2E-INT_ENABLE (Read/Write) bits
    # -------------------------------------
    def int_enable(self, int_mask):
        '''This function enables the interrupt specified by the bitmask @param int_mask. According to the datasheet, interrupts should
            be mapped in the INT_MAP register BEFORE enabling them in this register.
            The different interrupt options for @param int_mask are as follows:

                DATA_READY_enable   = micropython.const(0b10000000)
                SINGLE_SHOCK_enable = micropython.const(0b01000000)
                DOUBLE_SHOCK_enable = micropython.const(0b00100000)
                Activity_enable     = micropython.const(0b00010000)
                Inactivity_enable   = micropython.const(0b00001000)
                Watermark_enable    = micropython.const(0b00000010)
                Overrun_enable      = micropython.const(0b00000001) 
        '''
        reg_value   = self.get_INT_ENABLE()
        data        = reg_value | int_mask # Sets the bit specified by int_mask to 1
        self.set_INT_ENABLE(data)

    def int_disable(self, int_mask):
        '''This function disables the interrupt specified by the bitmask @param int_mask. The options for @param int_mask are as follows:

                DATA_READY_enable   = micropython.const(0b10000000)
                SINGLE_SHOCK_enable = micropython.const(0b01000000)
                DOUBLE_SHOCK_enable = micropython.const(0b00100000)
                Activity_enable     = micropython.const(0b00010000)
                Inactivity_enable   = micropython.const(0b00001000)
                Watermark_enable    = micropython.const(0b00000010)
                Overrun_enable      = micropython.const(0b00000001) 
        '''
        reg_value   = self.get_INT_ENABLE()
        data        = (reg_value & ~int_mask) # Sets the bit specified by int_mask to 0
        self.set_INT_ENABLE(data)

    # -------------------------------------
    # INTERRUPT MAPPING CONTROL
    # Register 0x2R-INT_MAP (Read/Write) bits
    # -------------------------------------
    def int_map_int1(self, int_mask):
        '''This function maps the interrupt given by the bit mask @param int_mask to pin INT1. 
            The options for @param int_mask are as follows:

                DATA_READY_enable   = micropython.const(0b10000000)
                SINGLE_SHOCK_enable = micropython.const(0b01000000)
                DOUBLE_SHOCK_enable = micropython.const(0b00100000)
                Activity_enable     = micropython.const(0b00010000)
                Inactivity_enable   = micropython.const(0b00001000)
                Watermark_enable    = micropython.const(0b00000010)
                Overrun_enable      = micropython.const(0b00000001)
        '''
        reg_value   = self.get_INT_MAP()
        data        = (reg_value & ~int_mask) # Sets the bit specified by int_mask to 0
        self.set_INT_MAP(data)    

    def int_map_int2(self, int_mask):
        '''This function maps the interrupt given by the bit mask @param int_mask to pin INT2. 
            The options for @param int_mask are as follows:

                DATA_READY_enable   = micropython.const(0b10000000)
                SINGLE_SHOCK_enable = micropython.const(0b01000000)
                DOUBLE_SHOCK_enable = micropython.const(0b00100000)
                Activity_enable     = micropython.const(0b00010000)
                Inactivity_enable   = micropython.const(0b00001000)
                Watermark_enable    = micropython.const(0b00000010)
                Overrun_enable      = micropython.const(0b00000001)
        '''
        reg_value   = self.get_INT_MAP()
        data        = reg_value | int_mask # Sets the bit specified by int_mask to 1
        self.set_INT_MAP(data)





    # -------------------------------------
    # DATA FORMAT
    # Register 0x31-DATA_FORMAT (Read/Write) bits
    # -------------------------------------
    def begin_self_test(self):
        '''This function begins the self test feature of the ADXL375 by exerting an electrostatic
            force on the sensor.
        '''
        reg_value   = self.get_DATA_FORMAT()
        data        = reg_value | self.SELF_TEST # Sets the SELF_TEST bit to 1
        self.set_DATA_FORMAT(data)   

    def end_self_test(self):
        '''This function ends the self test feature of the ADXL375.'''
        reg_value   = self.get_DATA_FORMAT()
        data        = reg_value & ~self.SELF_TEST # Sets the SELF_TEST bit to 0
        self.set_DATA_FORMAT(data)

    def spi_3_wire(self):
        '''This function configures the ADXL375 for 3 wire SPI mode.'''
        reg_value   = self.get_DATA_FORMAT()
        data        = reg_value | self.SPI # Sets the SPI bit to 1
        self.set_DATA_FORMAT(data)  

    def spi_4_wire(self):
        '''This function configures the ADXL375 for 4 wire SPI mode. This is the default state
            upon startup.
        '''
        reg_value   = self.get_DATA_FORMAT()
        data        = reg_value & ~self.SPI # Sets the SPI bit to 0
        self.set_DATA_FORMAT(data)

    def interrupt_active_low(self):
        '''This function sets the polarity of the interrupt pins to active low.'''
        reg_value   = self.get_DATA_FORMAT()
        data        = reg_value | self.INT_INVERT # Sets the INT_INVERT bit to 1
        self.set_DATA_FORMAT(data)    

    def interrupt_active_high(self):
        '''This function sets the polarity of the interrupt pins to active high.'''
        reg_value   = self.get_DATA_FORMAT()
        data        = reg_value & ~self.INT_INVERT # Sets the INT_INVERT bit to 0
        self.set_DATA_FORMAT(data)  

    def left_justify(self):
        '''This function sets the acceleration data to be left justified (MSB).'''
        reg_value   = self.get_DATA_FORMAT()
        data        = reg_value | self.Justify # Sets the Justify bit to 1
        self.set_DATA_FORMAT(data)

    def right_justify(self):
        '''This function sets the acceleration data to be right justified (LSB) with
            sign extension.
        '''
        reg_value   = self.get_DATA_FORMAT()
        data        = reg_value & ~self.Justify # Sets the Justify bit to 0
        self.set_DATA_FORMAT(data)


    # SELF_TEST           = micropython.const(0b10000000)
    # SPI                 = micropython.const(0b01000000)
    # INT_INVERT          = micropython.const(0b00100000)
    # Justify             = micropython.const(0b00000100)

    # -------------------------------------
    # ACCELERATION DATA
    # Register 0x32-0x37-ACCELERATION DATA (Read only) bits
    # -------------------------------------
    def get_x_acceleration(self):
        '''This function returns the x-axis acceleration of the device. Note that for general
            data acquisition this should be used over 'get_DATAX0()' and 'get_DATAX1()' because
            it reads the two bytes sequentially using the 'mem_read_2bytes()' function. This
            ensures that the data in the registers doesn't change from one read to the next.'''

        self.mem_read_2bytes(self.DATAX0)
        LSB = self.buf_2[1]
        MSB = self.buf_2[2]
        data = (MSB << 8) + LSB
        return self.twos_comp(data, 16)*self.SCALE_FACTOR 

    def get_y_acceleration(self):
        '''This function returns the y-axis acceleration of the device. Note that for general
            data acquisition this should be used over 'get_DATAY0()' and 'get_DATAY1()' because
            it reads the two bytes sequentially using the 'mem_read_2bytes()' function. This
            ensures that the data in the registers doesn't change from one read to the next.'''

        self.mem_read_2bytes(self.DATAY0)
        LSB = self.buf_2[1]
        MSB = self.buf_2[2]
        data = (MSB << 8) + LSB
        return self.twos_comp(data, 16)*self.SCALE_FACTOR  

    def get_z_acceleration(self):
        '''This function returns the x-axis acceleration of the device. Note that for general
            data acquisition this should be used over 'get_DATAZ0()' and 'get_DATAZ1()' because
            it reads the two bytes sequentially using the 'mem_read_2bytes()' function. This
            ensures that the data in the registers doesn't change from one read to the next.'''

        self.mem_read_2bytes(self.DATAZ0)
        LSB = self.buf_2[1]
        MSB = self.buf_2[2]
        data = (MSB << 8) + LSB
        return self.twos_comp(data, 16)*self.SCALE_FACTOR  


    # -------------------------------------
    # FIFO CONTROL
    # Register 0x38-FIFO_CTL (Read/Write) bits
    # -------------------------------------        
    def FIFO_Mode_Bypass(self):
        '''Sets the FIFO buffer to bypass mode (the FIFO buffer is bypassed (ignored))'''

        reg_value   = self.get_FIFO_CTL()
        reg_value   = reg_value & 0b00111111 # Clears the two most significant bits
        data        = reg_value + self.FIFO_MODE_Bypass # Add bit mask to set two most significant bits
        self.set_FIFO_CTL(data)

    def FIFO_Mode_FIFO(self):
        '''Sets the FIFO buffer to FIFO mode'''

        reg_value   = self.get_FIFO_CTL()
        reg_value   = reg_value & 0b00111111 # Clears the two most significant bits
        data        = reg_value + self.FIFO_MODE_FIFO # Add bit mask to set two most significant bits
        self.set_FIFO_CTL(data)

    def FIFO_Mode_Stream(self):
        '''Sets the FIFO buffer to stream mode'''

        reg_value   = self.get_FIFO_CTL()
        reg_value   = reg_value & 0b00111111 # Clears the two most significant bits
        data        = reg_value + self.FIFO_MODE_Stream # Add bit mask to set two most significant bits
        self.set_FIFO_CTL(data)

    def FIFO_Mode_Trigger(self):
        '''Sets the FIFO buffer to trigger mode'''

        reg_value   = self.get_FIFO_CTL()
        reg_value   = reg_value & 0b00111111 # Clears the two most significant bits
        data        = reg_value + self.FIFO_MODE_Trigger # Add bit mask to set two most significant bits
        self.set_FIFO_CTL(data)

    def trigger_int1(self):
        '''Links the trigger output to pin INT1'''

        reg_value   = self.get_FIFO_CTL()
        data        = reg_value & ~self.Trigger # Sets the trigger bit to 0
        self.set_FIFO_CTL(data)

    def trigger_int2(self):
        '''Links the trigger output to pin INT2'''

        reg_value   = self.get_FIFO_CTL()
        data        = reg_value | self.Trigger # Sets the trigger bit to 1
        self.set_FIFO_CTL(data)

    def set_samples(self, num):
        '''Sets the number of samples given by @param num. @param num can be any number from 0 to 32. If @param num is greater than
            32, it is automatically set to 32. If @param num is less than 0, it is automatically set to 0.
            The function of the samples number depends on the FIFO mode selected:

            FIFO MODE:              SAMPLES FUNCTION:
            Bypass                  None
            FIFO                    Specifies how many FIFO entries are needed to trigger a watermark interrupt.
            Stream                  Specifies how many FIFO entries are needed to trigger a watermark interrupt.
            Trigger                 Specifies how many FIFO samples are retained in the FIFO buffer before a trigger event.
        '''
        if num > 32:
            num = 32
        if num < 0:
            num = 0

        reg_value   = self.get_FIFO_CTL()
        reg_value   = reg_value & 0b11100000 # Clears the least significant five bits
        data        = reg_value + num # Set the samples bits according to the value given by num
        self.set_FIFO_CTL(data)


    # Register 0x39-FIFO_STATUS (Read only) bits
    # FIFO_TRIG           = micropython.const(0b10000000)











    # -------------------------------------
    # TESTING FUNCTIONS
    # -------------------------------------

    def config(self):
        '''This function puts the accelerometer into configuration mode. Note that this
            is the default state when the accelerometer first starts up
        '''

    def test_read(self):
        '''This function reads the device ID over and over to test if it works.'''
        print('1')
        self.get_DEVID()
        print('2')
        self.get_DEVID()
        print('3')
        self.get_DEVID()

        print("Read success!")

    def test_write(self):
        '''This function writes  the device ID over and over to test if it works.'''

        print('1')
        self.set_OFSX(0b00000000)
        print('2')
        self.set_OFSX(0b00000000)
        print('3')
        self.set_OFSX(0b00000000)

        print("Write success!")


















    # -------------------------------------
    # 'GETTER' FUNCTIONS
    # -------------------------------------

    def get_DEVID(self):
        '''This function returns the device ID'''
        self.mem_read(self.DEVID)
        return self.buf[1]

    def get_THRESH_SHOCK(self):
        '''This function returns the shock threshold value'''
        self.mem_read(self.THRESH_SHOCK)
        return self.buf[1]

    def get_OFSX(self):
        '''This function returns the x-axis offset'''
        self.mem_read(self.OFSX)
        return self.buf[1]

    def get_OFSY(self):
        '''This function returns the y-axis offset'''
        self.mem_read(self.OFSY)
        return self.buf[1]

    def get_OFSZ(self):
        '''This function returns the z-axis offset'''
        self.mem_read(self.OFSZ)
        return self.buf[1]

    def get_DUR(self):
        '''This function returns the shock duration'''
        self.mem_read(self.DUR)
        return self.buf[1]

    def get_Latent(self):
        '''This function returns the shock latency'''
        self.mem_read(self.Latent)
        return self.buf[1]

    def get_Window(self):
        '''This function returns the shock Window'''
        self.mem_read(self.Window)
        return self.buf[1]

    def get_THRESH_ACT(self):
        '''This function returns the activity threshold'''
        self.mem_read(self.THRESH_ACT)
        return self.buf[1]

    def get_THRESH_INACT(self):
        '''This function returns the inactivity threshold'''
        self.mem_read(self.THRESH_INACT)
        return self.buf[1]

    def get_TIME_INACT(self):
        '''This function returns the inactivity time'''
        self.mem_read(self.TIME_INACT)
        return self.buf[1]

    def get_ACT_INACT_CTL(self):
        '''This function returns the axis enable control for activity and inactivity detection'''
        self.mem_read(self.ACT_INACT_CTL)
        return self.buf[1]

    def get_SHOCK_AXES(self):
        '''This function returns the axis control for single shock/double shock'''
        self.mem_read(self.SHOCK_AXES)
        return self.buf[1]

    def get_ACT_SHOCK_STATUS(self):
        '''This function returns the source of single shock/double shock'''
        self.mem_read(self.ACT_SHOCK_STATUS)
        return self.buf[1]

    def get_BW_RATE(self):
        '''This function returns the data rate and power mode control'''
        self.mem_read(self.BW_RATE)
        return self.buf[1]

    def get_POWER_CTL(self):
        '''This function returns the power saving control feature'''
        self.mem_read(self.POWER_CTL)
        return self.buf[1]

    def get_INT_ENABLE(self):
        '''This function returns the interrupt enable control value'''
        self.mem_read(self.INT_ENABLE)
        return self.buf[1]

    def get_INT_MAP(self):
        '''This function returns the interrupt mapping contol'''
        self.mem_read(self.INT_MAP)
        return self.buf[1]

    def get_INT_SOURCE(self):
        '''This function returns the interrupt source'''
        self.mem_read(self.INT_SOURCE)
        return self.buf[1]

    def get_DATA_FORMAT(self):
        '''This function returns the data format'''
        self.mem_read(self.DATA_FORMAT)
        return self.buf[1]

    def get_DATAX0(self):
        '''This function returns the first byte of the x-axis accelerometer data'''
        self.mem_read(self.DATAX0)
        return self.buf[1]

    def get_DATAX1(self):
        '''This function returns the second byte of the x-axis accelerometer data'''
        self.mem_read(self.DATAX1)
        return self.buf[1]

    def get_DATAY0(self):
        '''This function returns the first byte of the y-axis accelerometer data'''
        self.mem_read(self.DATAY0)
        return self.buf[1]

    def get_DATAY1(self):
        '''This function returns the second byte of the y-axis accelerometer data'''
        self.mem_read(self.DATAY1)
        return self.buf[1]

    def get_DATAZ0(self):
        '''This function returns the first byte of the z-axis accelerometer data'''
        self.mem_read(self.DATAZ0)
        return self.buf[1]

    def get_DATAZ1(self):
        '''This function returns the second byte of the z-axis accelerometer data'''
        self.mem_read(self.DATAZ1)
        return self.buf[1]

    def get_FIFO_CTL(self):
        '''This function returns the FIFO control'''
        self.mem_read(self.FIFO_CTL)
        return self.buf[1]

    def get_FIFO_STATUS(self):
        '''This function returns the FIFO status'''
        self.mem_read(self.FIFO_STATUS)
        return self.buf[1]

    # -------------------------------------
    # 'SETTER' FUNCTIONS
    # -------------------------------------
    def set_THRESH_SHOCK(self, data):
        '''This function sets the shock threshold value with the data
            specified in @param data.
        '''
        self.mem_write(self.THRESH_SHOCK, data)

    def set_OFSX(self, data):
        '''This function sets the x-axis offset with the data
            specified in @param data
        '''
        self.mem_write(self.OFSXF, data)

    def set_OFSY(self, data):
        '''This function sets the y-axis offset with the data
            specified in @param data
        '''
        self.mem_write(self.OFSXY, data)

    def set_OFSZ(self, data):
        '''This function sets the z-axis offset with the data
            specified in @param data
        '''
        self.mem_write(self.OFSXZ, data)

    def set_DUR(self, data):
        '''This function sets the shock duration with the data
            specified in @param data
        '''
        self.mem_write(self.DUR, data)

    def set_Latent(self, data):
        '''This function sets the shock latency with the data
            specified in @param data
        '''
        self.mem_write(self.Latent, data)

    def set_Window(self, data):
        '''This function sets the shock Window with the data
            specified in @param data
        '''
        self.mem_write(self.Window, data)

    def set_THRESH_ACT(self, data):
        '''This function sets the activity threshold with the data
            specified in @param data
        '''
        self.mem_write(self.THRESH_ACT, data)

    def set_THRESH_INACT(self, data):
        '''This function sets the inactivity threshold with the data
            specified in @param data
        '''
        self.mem_write(self.THRESH_INACT, data)

    def set_TIME_INACT(self, data):
        '''This function sets the inactivity time with the data
            specified in @param data
        '''
        self.mem_write(self.TIME_INACT, data)

    def set_ACT_INACT_CTL(self, data):
        '''This function sets the axis enable control for activity and inactivity detection with the data
            specified in @param data
        '''
        self.mem_write(self.ACT_INACT_CTL, data)

    def set_SHOCK_AXES(self, data):
        '''This function sets the axis control for single shock/double shock with the data
            specified in @param data
        '''
        self.mem_write(self.SHOCK_AXES, data)

    def set_BW_RATE(self, data):
        '''This function sets the data rate and power mode control with the data
            specified in @param data
        '''
        self.mem_write(self.BW_RATE, data)

    def set_POWER_CTL(self, data):
        '''This function sets the power saving control feature with the data
            specified in @param data
        '''
        self.mem_write(self.POWER_CTL, data)

    def set_INT_ENABLE(self, data):
        '''This function sets the interrupt enable control value with the data
            specified in @param data
        '''
        self.mem_write(self.INT_ENABLE, data)

    def set_INT_MAP(self, data):
        '''This function sets the interrupt mapping contol with the data
            specified in @param data
        '''
        self.mem_write(self.INT_MAP, data)

    def set_DATA_FORMAT(self, data):
        '''This function sets the data format with the data
            specified in @param data
        '''
        self.mem_write(self.DATA_FORMAT, data)

    def set_FIFO_CTL(self, data):
        '''This function sets the FIFO control'''
        self.mem_write(self.FIFO_CTL, data)





















