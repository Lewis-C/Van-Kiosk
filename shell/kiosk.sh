#!/bin/bash

URL1="127.0.0.1"

xset s noblank
xset s off
xset -dpms

unclutter -idle 0.5 -root &

python /home/pi/shared/scripts/python/get_weather.py

sed -i 's/"exited_cleanly":false/"exited_cleanly":true/' /home/pi/.config/chromium/Default/Preferences
sed -i 's/"exit_type":"Crashed"/"exit_type":"Normal"/' /home/pi/.config/chromium/Default/Preferences

/usr/bin/chromium-browser --noerrdialogs --disable-infobars --disk-cache-dir=/dev/null --disk-cache-size=1 --kiosk $URL1 &

while true; do
   sleep 10
done
