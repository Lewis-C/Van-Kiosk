#!/bin/sh
/usr/bin/python3 /home/pi/shared/scripts/python/live_gps_data.py &
/usr/bin/python3 /home/pi/shared/scripts/python/live_tilt_data.py &

sleep 15
/usr/bin/python3 /home/pi/shared/scripts/python/live_tank_data.py &