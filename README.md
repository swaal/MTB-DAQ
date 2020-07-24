# MTB DAQ
A small and portable data acquisition system based on the PyBoard V1.1 designed to collect acceleration data while riding a mountain bike.

## About
The Mountain Bike Data Acquisition System (MTB DAQ) is a system designed to collect acceleration data while riding a mountain bike.
The system was designed as part of a Cal Poly Masters Thesis in Mechanical Engineering focused on quantitatively tuning mountain bike suspension. The MTB DAQ
was designed after the PyBoard V1.1 and is utilizes the same firmware. The acceleration data is stored in binary format on a Micro SD card. 

## Contents
The files included in this project provide almost everything needed to build a MTB DAQ. The folders are arranged as follows:
### BoardFiles
This folder contains all of the Autodesk Eagle schematic and board files. There are three types of boards: the Main Board, the UI Board, and the ADXL375 Board. 
The Main Board and UI Board work together to define the heart of the system, providing the computing power and user interface. The ADXL375 Board provides the necessary power filtering and connections for the ADXL375 accelerometer. The accelerometers are connected to the main board via two ethernet cables, chosen for their wide availability, low cost, and locking connection.
### MicropythonCode
This folder contains the micropython files that run the MTB DAQ. Note that some of the files have been saved as *.mpy* files. This is a bytecote version of the original file. This was done in order to make the files small enough to fit in the flash memory of the microcontroller. The original files are contained within the sub folder "files_converted_to_mpy"
### PyBoardFirmware
A copy of the compatible PyBoard V1.1 firmware.

## Technical Specifications
- Accelerometers: Analog Devices ADXL375BCCZ Accelerometer
- Number of Accelerometers Supported: 2
- Measurement Range: +/- 200g
- Output Data Rate: 1600Hz (can be configured to go up to 3200Hz)
- Battery Life: > 8 hours
