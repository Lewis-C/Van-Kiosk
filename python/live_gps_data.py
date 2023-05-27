import datetime # Used to handle logging last update
import json # Used to write file
from math import asin, degrees # Used to calc degrees

from gps import * # Used to handle GPS





# Loop through GPS reports (should loop)
for report in gps(mode=WATCH_ENABLE):

    # Find valid GPS report type
    if report['class'] == "TPV":
        # Get lat and long
        lat = (getattr(report,"lat", 0))
        lon = (getattr(report,"lon", 0))


        # If valid, update the json
        if (lon != 0 and lat != 0):

            gps = {
                "last_gps_update" : (datetime.datetime.now().strftime("%d/%m/%y %H:%M")), # Log of update time
                "latitude": lat,
                "longitude": lon
            }
            
            with open('/home/pi/shared/scripts/python/gps.json', "w") as outfile:
                print("updating gps")
                json.dump(gps, outfile)  






