import smbus
import math
import time
import datetime
import csv


class MPU:
    def __init__(self):
        print("Zeroing Tilt Sensor...")
        
        # Init Gyro Readings
        self.gyro_x = 0
        self.gyro_y = 0
        self.gyro_z = 0

        # Init accelerometer readings
        self.acc_x = 0
        self.acc_y = 0
        self.acc_z = 0

        # Init gyro calibration readings
        self.gyro_x_cal = 0
        self.gyro_y_cal = 0
        self.gyro_z_cal = 0

        # Init gyro angle readings
        self.gyro_roll = 0
        self.gyro_pitch = 0
        self.gyro_yaw = 0

        # Init total angle readings
        self.roll = 0
        self.pitch = 0
        self.yaw = 0

        # Init clock for timing readings
        self.clock_timer = 0

        # Init filter for ration between low and high pass filter of complementarty
        self.filter = 0.98

        # Sets number of passes needed to calibrate the gyro
        self.calibration_passes = 500

        # Stores the scale factor and hex for gyro, handles sensitivity at:
        """
        250 deg/s:  [131.0, 0x00],
        500 deg/s:  [65.5,  0x08], (Default)
        1000 deg/s: [32.8,  0x10],
        2000 deg/s: [16.4,  0x18]
        
        """
        self.gyro_scale_factor = 65.5
        self.gyro_hex = 0x08

        # Stores the scale factor and hex for gyro, handles sensitivity at:
        """
        2g:  [16384.0, 0x00],
        4g:  [8192.0,  0x08], (Default)
        8g:  [4096.0,  0x10],
        16g: [2048.0,  0x18]
        
        """
        self.acc_scale_factor = 8192.0
        self.acc_hex = 0x08


        # Uses SMBus to get MPU-6050, declares address as 0x68
        self.bus = smbus.SMBus(1)
        self.address = 0x68

        self.roll_offset = 2.75
        self.pitch_offset = 0.771



    def set_up(self):
        """
        Function to assign initialised sensor values
        """

        # Activate the MPU-6050
        self.bus.write_byte_data(self.address, 0x6B, 0x00)

        # Configure the accelerometer to settings
        self.bus.write_byte_data(self.address, 0x1C, self.acc_hex)

        # Configure the gyro to settings
        self.bus.write_byte_data(self.address, 0x1B, self.gyro_hex)

    def bit_conversion(self, reg):
        """
        Function to convert bits for rading
        """
        # Reads high and low 8 bit values and shifts them into 16 bit
        h = self.bus.read_byte_data(self.address, reg)
        l = self.bus.read_byte_data(self.address, reg+1)
        val = (h << 8) + l

        # Make 16 bit unsigned value to signed value (0 to 65535) to (-32768 to +32767)
        if (val >= 0x8000):
            return -((65535 - val) + 1)
        else:
            return val

    def get_raw_data(self):
        """
        Function to get raw data for each metric
        """
        self.gyro_x = self.bit_conversion(0x43)
        self.gyro_y = self.bit_conversion(0x45)
        self.gyro_z = self.bit_conversion(0x47)

        self.acc_x = self.bit_conversion(0x3B)
        self.acc_y = self.bit_conversion(0x3D)
        self.acc_z = self.bit_conversion(0x3F)

    def calibrate_gyro(self):
        """
        Function to calibrate the gyro using an average to offset drift
        """

        # for each pass, find sum of readings
        for calibration_pass in range(self.calibration_passes):
            self.get_raw_data()
            self.gyro_x_cal += self.gyro_x
            self.gyro_y_cal += self.gyro_y
            self.gyro_z_cal += self.gyro_z

        # Find average offset value
        self.gyro_x_cal /= self.calibration_passes
        self.gyro_y_cal /= self.calibration_passes
        self.gyro_z_cal /= self.calibration_passes

        # Now that calibrated, start timer
        self.clock_timer = time.time()

    def process_data(self):
        """
        Function to process data
        """
        # Update the raw data
        self.get_raw_data()

        # Subtract the offset calibration values
        self.gyro_x -= self.gyro_x_cal
        self.gyro_y -= self.gyro_y_cal
        self.gyro_z -= self.gyro_z_cal

        # Convert to degrees per second
        self.gyro_x /= self.gyro_scale_factor
        self.gyro_y /= self.gyro_scale_factor
        self.gyro_z /= self.gyro_scale_factor

        # Convert to g force
        self.acc_x /= self.acc_scale_factor
        self.acc_y /= self.acc_scale_factor
        self.acc_z /= self.acc_scale_factor

    def complementary_filter(self):
        """
        Filter processed values for use
        """

        # Get the processed values from IMU
        self.process_data()

        # Get difference in time and record time for next call
        clock_time_passed = time.time() - self.clock_timer
        self.clock_timer = time.time()

        # Acceleration vector angle, using atan with z 
        acc_roll = math.degrees(math.atan2(self.acc_x, self.acc_z))
        acc_pitch = math.degrees(math.atan2(self.acc_y, self.acc_z))

        # Gyro integration angle (angles per second, * seconds)
        self.gyro_roll -= self.gyro_y * clock_time_passed
        self.gyro_pitch += self.gyro_x * clock_time_passed


        # Comp filter (ratios values using filter then adds together to counter gyros drift and acc's stutter)
        self.roll = ((self.filter)*(self.roll - self.gyro_y * clock_time_passed)) + ((1-self.filter)*(acc_roll))
        self.pitch = ((self.filter)*(self.pitch + self.gyro_x * clock_time_passed)) + ((1-self.filter)*(acc_pitch))


def main():
    # Set up class
    mpu = MPU()
    mpu.set_up()
    mpu.calibrate_gyro()



    mpu.complementary_filter()
    roll = round((mpu.roll - mpu.roll_offset),1)
    pitch = round((mpu.pitch*-1) - mpu.pitch_offset,1)              
    with open('/home/pi/shared/scripts/python/zero_val.csv', "w") as outfile:
        writer = csv.writer(outfile)
        writer.writerow([(datetime.datetime.now().strftime("%d/%m/%y %H:%M")),roll, pitch])
    print("Tilt Sensor Zeroed. Please Reboot (sudo reboot)")

# Main loop
if __name__ == '__main__':
    main()
