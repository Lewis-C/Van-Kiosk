#!/bin/sh
echo $(date) >> /home/pi/shared/scripts/shell/bash_cron_log.txt
/usr/bin/python3 /home/pi/shared/scripts/python/live_gps_data.py & >> /home/pi/shared/scripts/shell/bash_cron_log.txt 
/usr/bin/python3 /home/pi/shared/scripts/python/live_tilt_data.py & >> /home/pi/shared/scripts/shell/bash_cron_log.txt

sleep 15
/usr/bin/python3 /home/pi/shared/scripts/python/live_tank_data.py & >> /home/pi/shared/scripts/shell/bash_cron_log.txt

