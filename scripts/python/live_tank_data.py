import collections
import time
import bluetooth
import sys
import subprocess

import datetime
import csv

CONTINUOUS_REPORTING = "04"
COMMAND_LIGHT = 11
COMMAND_REPORTING = 12
COMMAND_REGISTER = 16
COMMAND_READ_REGISTER = 17
INPUT_STATUS = 20
INPUT_READ_DATA = 21
EXTENSION_8BYTES = 32
BUTTON_DOWN_MASK = 8
TOP_RIGHT = 0
BOTTOM_RIGHT = 1
TOP_LEFT = 2
BOTTOM_LEFT = 3

SAMPLE_SIZE = 100

class WiiBoard:
    def __init__(self):
        # Bluetooth Sockets
        self.recieveSocket = None
        self.controlSocket = None

        self.address = None

        self.status = "Disconnected"

        try:
            self.recieveSocket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
            self.controlSocket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
        except ValueError:
            raise Exception("Error: Bluetooth not Found")

    def isConnected(self):
        return self.recieveSocket and self.controlSocket


def send(controlSocket, data):
    data[0] = "52"

    sendData = ' '.join(str(x) for x in data)
    

    sendData = bytes.fromhex(sendData)

    controlSocket.send(sendData)


def setLight(controlSocket, light):
    if light:
        val = "10"
    else:
        val = "00"

    message = ["00", COMMAND_LIGHT, val]
    send(controlSocket, message)


def parseCalibrationResponse(calibration, bytes):
    index = 0
    if len(bytes) == 16:
        for i in range(2):
            for j in range(4):
                calibration[i][j] = (
                        int((bytes[index : index + 1]).hex(), 16) << 8
                    ) + int((bytes[index + 1 : index + 2]).hex(), 16)
                index += 2
    elif len(bytes) < 16:
        for i in range(4):
            calibration[2][i] = (
                    int(bytes[index : index + 1].hex(), 16) << 8
                ) + int(bytes[index + 1 : index + 2].hex(), 16)
            index += 2
    return calibration


def calcMass(calibration, raw, pos):
    val = 0.0
    if raw < calibration[0][pos]:
        return val
    elif raw < calibration[1][pos]:
        val = 17 * ((raw - calibration[0][pos]) /
                    float((calibration[1][pos] - calibration[0][pos])))
    elif raw > calibration[1][pos]:
        val = 17 + 17 * \
            ((raw - calibration[1][pos]) /
             float((calibration[2][pos] - calibration[1][pos])))

    return val


def isConnected(address):
    connections = subprocess.check_output(["hcitool", "con"], text=True)

    if address in connections.split():
        return True
    return False


def main():

    address = None
    buttonDown = False
    calibration = []
    sampleGroup = []
    totalLeftWeight = 0
    totalRightWeight = 0
    buttonPressCount = 0
    zeroLeftWeight = 0.0
    zeroRightWeight = 0.0
    maxLeftWeight = 0.0
    maxRightWeight = 0.0

    for i in range(3):
        calibration.append([])
        for j in range(4):
            # high dummy value so events with it don't register
            calibration[i].append(10000)
    calibrationRequested = False

    # initialise bluetooth sockets
    recieveSocket = None
    controlSocket = None
    try:
        recieveSocket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
        controlSocket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
    except ValueError:
        raise Exception("Error: Bluetooth not Found")

    # disconnect already-connected devices
    try:
        subprocess.check_output(
            ["bluez-test-input", "disconnect", address], stderr=subprocess.STDOUT)
        subprocess.check_output(
            ["bluez-test-input", "disconnect", address], stderr=subprocess.STDOUT)
    except:
        pass

    while True:

        if address is not None and isConnected(address):
            
            # connected to a wii board
            try:
                # get board data
                data = recieveSocket.recv(25)
                intype = int(data.hex()[2:4])
                if intype == INPUT_STATUS:
                    # set Reporting Type
                    bytearr = ["00", COMMAND_REPORTING,
                               CONTINUOUS_REPORTING, EXTENSION_8BYTES]
                    send(controlSocket, bytearr)
                elif intype == INPUT_READ_DATA:
                    if calibrationRequested:
                        packetLength = int(int(data[4:5].hex(), 16) / 16) + 1
                        calibration = parseCalibrationResponse(
                            calibration, data[7:(7 + packetLength)])

                        if packetLength < 16:
                            calibrationRequested = False
                elif intype == EXTENSION_8BYTES:
                    bytes = data[2:12]
                    buttonBytes = bytes[0:2]
                    bytes = bytes[2:12]
                    buttonPressed = False
                    buttonReleased = False

                    state = (int(buttonBytes[0:1].hex(), 16) << 8) | int(buttonBytes[1:2].hex(), 16)
                    if state == BUTTON_DOWN_MASK:
                        buttonPressed = True
                        if not buttonDown:
                            # button pressed
                            buttonDown = True
                    if not buttonPressed:
                        if buttonDown:
                            # button released
                            buttonReleased = True
                            buttonDown = False

                    rawTR = (int(bytes[0:1].hex(), 16) << 8) + int(bytes[1:2].hex(), 16)
                    rawBR = (int(bytes[2:3].hex(), 16) << 8) + int(bytes[3:4].hex(), 16)
                    rawTL = (int(bytes[4:5].hex(), 16) << 8) + int(bytes[5:6].hex(), 16)
                    rawBL = (int(bytes[6:7].hex(), 16) << 8) + int(bytes[7:8].hex(), 16)

                    topLeft = calcMass(calibration, rawTL, TOP_LEFT)
                    topRight = calcMass(calibration, rawTR, TOP_RIGHT)
                    bottomLeft = calcMass(calibration, rawBL, BOTTOM_LEFT)
                    bottomRight = calcMass(calibration, rawBR, BOTTOM_RIGHT)

                    leftWeight = topLeft + bottomLeft
                    rightWeight = topRight + bottomRight

                    sampleGroup.append((leftWeight, rightWeight, int(buttonReleased)))

                    if ((len(sampleGroup))>=SAMPLE_SIZE):
                        for i in range(SAMPLE_SIZE):
                            totalLeftWeight += sampleGroup[i][0]
                            totalRightWeight += sampleGroup[i][1]
                            buttonPressCount += sampleGroup[i][2]

                        sampledLeftWeight = totalLeftWeight / SAMPLE_SIZE
                        sampledRightWeight = totalRightWeight / SAMPLE_SIZE
                        print(buttonPressCount)

                        if buttonPressCount == 1:
                            print("Writing Max Value")
                            maxLeftWeight = sampledLeftWeight
                            maxRightWeight = sampledRightWeight
                        elif buttonPressCount >= 1:
                            print("Writing Zero Value")
                            zeroLeftWeight = sampledLeftWeight
                            zeroRightWeight = sampledRightWeight
                        
                        
                        print("Writing Value")
                        with open('/var/www/html/data/tank.csv', "w") as outfile:
                            writer = csv.writer(outfile)
                            writer.writerow([(datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")),sampledLeftWeight, sampledRightWeight, maxLeftWeight, maxRightWeight, zeroLeftWeight, zeroRightWeight])

                        print([(datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")),sampledLeftWeight, sampledRightWeight, maxLeftWeight, maxRightWeight, zeroLeftWeight, zeroRightWeight])


                        sampleGroup = []
                        totalLeftWeight, totalRightWeight, buttonPressCount = 0,0,0

                        

                    sys.stdout.flush()

                    


            except:
                address = None
                print('{ "connected": false }')
                sys.stdout.flush()

        else:
            # not connected to a wii board
            address = None
            print('{ "connected": false }')
            sys.stdout.flush()
            try:
                recieveSocket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
                controlSocket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
            except ValueError:
                raise Exception("Error: Bluetooth not Found")
            # discover a wii board
            bluetoothdevices = bluetooth.discover_devices(
                duration=3, lookup_names=True)
            for bluetoothdevice in bluetoothdevices:
                if bluetoothdevice[1] == "Nintendo RVL-WBC-01":
                    address = bluetoothdevice[0]
                    # try to connect to address
                    recieveSocket.connect((address, 0x13))
                    controlSocket.connect((address, 0x11))
                    if recieveSocket and controlSocket:
                        buttonDown = False
                        # calibrate
                        message = ["00", COMMAND_READ_REGISTER,
                                   "04", "A4", "00", "24", "00", "18"]
                        send(controlSocket, message)
                        
                        calibrationRequested = True
                        #
                        useExt = ["00", COMMAND_REGISTER,
                                  "04", "A4", "00", "40", "00"]
                        send(controlSocket, useExt)
                        # set Reporting Type
                        bytearr = ["00", COMMAND_REPORTING,
                                   CONTINUOUS_REPORTING, EXTENSION_8BYTES]
                        
                        send(controlSocket, bytearr)

                        # light blinking notifier
                        time.sleep(0.2)
                        setLight(controlSocket, False)
                        time.sleep(0.5)
                        setLight(controlSocket, True)
                        # connected to a board
                        break

        


if __name__ == "__main__":
    main()