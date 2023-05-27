import collections
import subprocess
import sys
import time
import datetime
import csv
import time

import bluetooth

CONTINUOUS_REPORTING = "04"  # Easier as string with leading zero

COMMAND_LIGHT = 11
COMMAND_REPORTING = 12
COMMAND_REQUEST_STATUS = 15
COMMAND_REGISTER = 16
COMMAND_READ_REGISTER = 17

# input is Wii device to host
INPUT_STATUS = 20
INPUT_READ_DATA = 21

EXTENSION_8BYTES = 32
# end "hex" values

BUTTON_DOWN_MASK = 8

TOP_RIGHT = 0
BOTTOM_RIGHT = 1
TOP_LEFT = 2
BOTTOM_LEFT = 3

BLUETOOTH_NAME = "Nintendo RVL-WBC-01"


class EventProcessor:
    """
    Class to handle events of wiiboard (change in mass)
    """

    def __init__(self):
        """
        Initiliases booleans to flag progress, and empty list to store events
        """

        self._measured = False
        self.done = False
        self.left_weight = 0
        self.right_weight = 0 

    def mass(self, event):
        """
        Function to handle processing mass measurements
        """

        self.left_weight = round(event.leftWeight,2)

        self.right_weight = round(event.rightWeight,2)

class BoardEvent:
    """
    Class to handle the different potential changes in the board based on parameter input
    Currently sums all four weights
    """

    def __init__(
        self, topLeft, topRight, bottomLeft, bottomRight, buttonPressed, buttonReleased
    ):

        self.topLeft = topLeft
        self.topRight = topRight
        self.bottomLeft = bottomLeft
        self.bottomRight = bottomRight
        self.buttonPressed = buttonPressed
        self.buttonReleased = buttonReleased
        # convenience value
        self.leftWeight = topLeft + bottomLeft 
        self.rightWeight =  topRight + bottomRight


class Wiiboard:
    """
    Class to handle the wiiboard itself
    """

    def __init__(self, processor):
        """
        Initiliase the state of the wiiboard, defining proc class and init variables to hold wiiboard connection values
        """


        # Sockets and status, initialises in disconnected state
        self.receivesocket = None
        self.controlsocket = None

        self.processor = processor
        self.calibration = []
        self.calibrationRequested = False
        self.LED = False
        self.address = None
        self.buttonDown = False

        for i in range(3):
            self.calibration.append([])
            for j in range(4):
                self.calibration[i].append(
                    10000
                )  # high dummy value so events with it don't register

        self.status = "Disconnected"
        self.lastEvent = BoardEvent(0, 0, 0, 0, False, False)

        self.receivesocket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
        self.controlsocket = bluetooth.BluetoothSocket(bluetooth.L2CAP)

    def discover(self):
        """
        Find bluetooth address 
        """
        bluetoothdevices = bluetooth.discover_devices(duration=3, lookup_names=True)
        for bluetoothdevice in bluetoothdevices:
            print(bluetoothdevice)
            if bluetoothdevice[1] == BLUETOOTH_NAME:
                return bluetoothdevice[0]
        
        return ""
                

    # Connect to the WiiBoard at bluetooth address <address>
    def connect(self):
        """
        Connect to the WiiBoard at bluetooth address 
        """
        address = self.discover()

        if address == "":
            print("No Device Found")
            return 
        
        try:
            # Sockets must be refreshed on each connection
            # Discovers beforehand to ensure minimal performance loss
            self.receivesocket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
            self.controlsocket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
            self.receivesocket.connect((address, 0x13))
            self.controlsocket.connect((address, 0x11))
        except:
            print("Could not connect to WiiBoard at address " + address)
            return
                
        # If valid,
        if self.receivesocket and self.controlsocket:
            # Print message, set status flag and set address to the address
            print("Connected to WiiBoard at address " + address)
            self.status = "Connected"
            self.address = address
            # Calls the calibrate function 
            self.calibrate()
            # Sends message to wiiboard in hex format
            useExt = "00" + str(COMMAND_REGISTER) + "04" + "A4" + "00" + "40" + "00"
            self.send(useExt)
            self.setReportingType()
            # Prints message now that contact has been made
            print("WiiBoard connected")
        else:
            print("Could not connect to WiiBoard at address " + address)

    
    def isConnected(self):
        """
        Function to set status when connected
        """
        return self.status == "Connected"

    def receive(self):
        """
        
        """

        try:
            # Recieve data
            data = self.receivesocket.recv(25)
            # Get the input type
            intype = int(data.hex()[2:4])
            # If its input status,
            if intype == INPUT_STATUS:
                # TODO: Status input received. It just tells us battery life really
                self.setReportingType()
            # If its readable data
            elif intype == INPUT_READ_DATA:
                # If calibration has been requested
                if self.calibrationRequested:
                    # Format hexcode and parse
                    print("Calibration input received")
                    packetLength = int(int(data[4:5].hex(), 16) / 16) + 1
                    endSlice = 7 + packetLength
                    calibrationResponse = data[7:endSlice]
                    self.parseCalibrationResponse(calibrationResponse)

                    # Once done, allow weighiing and set calibration flag
                    if packetLength < 16:
                        print("Ready for input, please stand on WiiBoard")
                        self.calibrationRequested = False
            # If its a board event
            elif intype == EXTENSION_8BYTES:
                # Create the board event
                boardEvent = self.createBoardEvent(data[2:12])
                # Process the event into the events list
                self.processor.mass(boardEvent)
            else:
                print("ACK to data write received")

        except:
            # Once done, disconnect
            self.status = "Disconnected"
            self.disconnect()

    def disconnect(self):
        """
        Function to close connection to wiiboard and set flags
        """
        if self.status == "Connected":
            self.status = "Disconnecting"
            while self.status == "Disconnecting":
                self.wait(100)
        try:
            self.receivesocket.close()
        except:
            pass
        try:
            self.controlsocket.close()
        except:
            pass
        print("WiiBoard disconnected")



    def createBoardEvent(self, bytes):
        """
        Function to create board event
        """

        # Splits button and weight bytes
        buttonBytes = bytes[0:2]
        bytes = bytes[2:12]
        buttonPressed = False
        buttonReleased = False

        # Gets button state int from bytes
        state = (int(buttonBytes[0:1].hex(), 16) << 8) | int(buttonBytes[1:2].hex(), 16)

        # If down handles
        if state == BUTTON_DOWN_MASK:
            buttonPressed = True
            if not self.buttonDown:
                print("Button pressed")
                self.buttonDown = True

        # If not, handles
        if not buttonPressed:
            if self.lastEvent.buttonPressed:
                buttonReleased = True
                self.buttonDown = False
                print("Button released")

        # Raw data for the top corners
        rawTR = (int(bytes[0:1].hex(), 16) << 8) + int(bytes[1:2].hex(), 16)
        rawBR = (int(bytes[2:3].hex(), 16) << 8) + int(bytes[3:4].hex(), 16)
        rawTL = (int(bytes[4:5].hex(), 16) << 8) + int(bytes[5:6].hex(), 16)
        rawBL = (int(bytes[6:7].hex(), 16) << 8) + int(bytes[7:8].hex(), 16)
        
        # Calculates mass for each one
        topLeft = self.calcMass(rawTL, TOP_LEFT)
        topRight = self.calcMass(rawTR, TOP_RIGHT)
        bottomLeft = self.calcMass(rawBL, BOTTOM_LEFT)
        bottomRight = self.calcMass(rawBR, BOTTOM_RIGHT)

        # Creates the event itself with the values for the processed weights and button status
        boardEvent = BoardEvent(
            topLeft, topRight, bottomLeft, bottomRight, buttonPressed, buttonReleased
        )
        return boardEvent

    def calcMass(self, raw, pos):
        """
        Calculate mass from position on board and raw data
        Uses dependent calibaration data
        """
        val = 0.0
        # calibration[0] is calibration values for 0kg
        # calibration[1] is calibration values for 17kg
        # calibration[2] is calibration values for 34kg
        if raw < self.calibration[0][pos]:
            return val
        elif raw < self.calibration[1][pos]:
            val = 17 * (
                (raw - self.calibration[0][pos])
                / float((self.calibration[1][pos] - self.calibration[0][pos]))
            )
        elif raw > self.calibration[1][pos]:
            val = 17 + 17 * (
                (raw - self.calibration[1][pos])
                / float((self.calibration[2][pos] - self.calibration[1][pos]))
            )

        return val

    def getEvent(self):
        return self.lastEvent

    def getLED(self):
        return self.LED

    def parseCalibrationResponse(self, bytes):
        """
        Handles the calibration response
        """
        index = 0
        if len(bytes) == 16:
            for i in range(2):
                for j in range(4):
                    self.calibration[i][j] = (
                        int((bytes[index : index + 1]).hex(), 16) << 8
                    ) + int((bytes[index + 1 : index + 2]).hex(), 16)
                    index += 2
        elif len(bytes) < 16:
            for i in range(4):
                self.calibration[2][i] = (
                    int(bytes[index : index + 1].hex(), 16) << 8
                ) + int(bytes[index + 1 : index + 2].hex(), 16)
                index += 2


    def send(self, dataHex):
        """
        Send <data> to the Wiiboard
        <data> should be an array of strings, each string representing a single hex byte
        """
        if self.status != "Connected":
            return

        updatedHex = "52" + dataHex[2:]

        self.controlsocket.send(bytes.fromhex(updatedHex))


    def setLight(self, light):
        """
         Turns the power button LED on if light is True, off if False
         The board must be connected in order to set the light
        """
        # If light on, set to on value
        if light:
            val = "10"
        else:
            val = "00"

        # Sends the command to the wiiboard
        message = "00" + str(COMMAND_LIGHT) + val
        self.send(message)
        self.LED = light

    def calibrate(self):
        """
        Function to handle calibration
        """
        message = (
            "00" + str(COMMAND_READ_REGISTER) + "04" + "A4" + "00" + "24" + "00" + "18"
        )
        print("Requesting calibration")
        self.send(message)
        self.calibrationRequested = True

    def setReportingType(self):
        # bytearr = ["00", COMMAND_REPORTING, CONTINUOUS_REPORTING, EXTENSION_8BYTES]
        bytearr = (
            "00"
            + str(COMMAND_REPORTING)
            + str(CONTINUOUS_REPORTING)
            + str(EXTENSION_8BYTES)
        )
        self.send(bytearr)

    def wait(self, millis):
        time.sleep(millis / 1000.0)


def main():
    """
    Function to process
    """
    # Initialise processor
    processor = EventProcessor()

    # Initialise the board using said processor
    board = Wiiboard(processor)

    print("Trying to connect...")
    while True:
        if board.status == "Disconnected":
            board.connect()  # The wii board must be in sync mode at this time
        
            print("Connection failed, retrying")
        elif board.status == "Connected":
            board.receive()
            #time.sleep(15)
            
        with open('/var/www/html/data/tank_levels.csv', "w") as outfile:
            writer = csv.writer(outfile)
            writer.writerow([(datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")),processor.left_weight, processor.right_weight, board.status])
        
if __name__ == "__main__":
    main()
