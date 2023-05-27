# Imports
import urllib.request # Used to obtain API requests
import json # Used to write and read JSONs from API requests and for website
import datetime # Used to manage time




# Defines metadata dict for storing location / update data
metadata = {}

# Opens GPS data
with open('/home/pi/shared/scripts/python/gps.json') as gps_data_source:
    gps_data = json.load(gps_data_source)

# Sets gps status as true
gps_status = True

# Formats the last GPS update as a date
last_gps_update_date = (datetime.datetime.strptime(gps_data["last_gps_update"],"%d/%m/%y %H:%M"))
current_time = datetime.datetime.now()
# Finds difference in days between current time
last_gps_update_difference = (current_time - last_gps_update_date).days

# If valid difference, update lat and lon
if last_gps_update_difference <= 3 and gps_data['latitude'] != 0 and gps_data['longitude'] != 0:
    latitude = gps_data['latitude']
    longitude = gps_data['longitude']
# If gps invalid
else:
    # Opens API to access details about IP
    with urllib.request.urlopen("https://ipinfo.io/") as url:
        metadata = (json.load(url))

    # Boolean to flag GPS status as false
    gps_status = False
    # Gets API data for lat and long
    latitude = metadata['loc'].split(",")[0]
    longitude = metadata['loc'].split(",")[1]

# Gets timezone from device
timezone = datetime.datetime.now().astimezone().tzinfo

# Get current times
current_time = (datetime.datetime.now().replace(minute=0, second=0, microsecond=0).isoformat())[:-3]  # No minutes for comparison to weather readings
last_update = (datetime.datetime.now().strftime("%d/%m/%y %H:%M"))  # Log of update time

# Adds current time to metadata for use to display when last updated, as well as flag to show if GPS worked or not. Overwrites timezone
metadata.update({"last_update": last_update})
metadata.update({"gps_status": gps_status})
metadata.update({"last_gps_update": gps_data["last_gps_update"]})
metadata.update({"timezone":str(timezone)})

# If location found using gps
if gps_status == True:
    # Use reverse geocoding using accurate coords
    with urllib.request.urlopen(f"https://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}&zoom=18&addressdetails=1") as geolocator:
        # Gets loc data
        location_data = json.load(geolocator)
    
    try:
        # Gets city and state
        loc_1 = (location_data['address']['city'])
        loc_2 = (location_data['address']['state'])
    except:
        try:
            loc_1 = (location_data['address']['state_district'])
            loc_2 = (location_data['address']['country'])
        except:
            loc_1 = ""
            loc_2 = ""

    # Updates metadata with found GPS details
    metadata.update({"city": loc_1})
    metadata.update({"region": loc_2})


    metadata.update({"latitude": latitude})
    metadata.update({"longitude": longitude})




# Opens weather API using parameters, saves JSON as data
with urllib.request.urlopen(f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m,weathercode,windspeed_10m&daily=sunrise,sunset&current_weather=true&windspeed_unit=mph&timezone={timezone}") as url:
    data = json.load(url)

# Opens dict of weather code translations
with open('/home/pi/shared/scripts/python/code_translation.json') as code_translation_source:
    code_translation = json.load(code_translation_source)

# Def list for weather readings
weather_readings = []

# Updates weather readings with metadata sourced from IP / GPS
weather_readings.append(metadata)

# For each date in the daily times find the current day based on the current time and return its index for later use
for index, date in enumerate(data['daily']['time']):
    if current_time[0:10] == date:
        daily_index = index
        break

# For each date in the hourly times find the current hour based on the current time and return its index for later use
for index, date in enumerate(data['hourly']['time']):
    if current_time == date:
        hourly_index = index
        break

# Create list of all sunset / sunrise times using daily index to slice to current day
sunsets = (data['daily']['sunset'][daily_index:])
sunrises = (data['daily']['sunrise'][daily_index:])

# Create list of all hourly weather metrics using hourly index to slice to current hour
times = (data['hourly']['time'][hourly_index:])
temps = (data['hourly']['temperature_2m'][hourly_index:])
weathercodes = (data['hourly']['weathercode'][hourly_index:])
windspeed = (data['hourly']['windspeed_10m'][hourly_index:])

# Variable to hold string of day status (night or day)
day_code = ""

# Iterate through, compare the first sunset/rise. Return daystatus before that as daycode
for x in range(len(times)):
    for y in range(len(sunrises)):
        if sunrises[y][0:13] == times[x][0:13]:
            day_code = "n"
            break
        if sunsets[y][0:13] == times[x][0:13]:
            day_code = "d"
            break
    if day_code != "":
        break

# For every hour available
for x in range(len(times)):

    # If weather code is not day dependent, return x prefix
    if weathercodes[x] in [56, 57, 66, 67, 77]:
        iconPrefix = "x"
    # Else use daycode
    else:
        iconPrefix = day_code

    # Build a dict with all weather metrics
    weatherReading = {
        "type": "weather",
        "time": (times[x]),
        "temp": (temps[x]),
        "code": iconPrefix + str(weathercodes[x]),
        "weather": (code_translation[str(weathercodes[x])]),
        "windspeed": (windspeed[x])
    }

    # Append the dict to the list of weather readings
    weather_readings.append(weatherReading)

    # iterate through each sunrise
    for y in range(len(sunrises)):

        # If sunrise date (hour only) of hour available matches
        if sunrises[y][0:13] == times[x][0:13]:

            # Create a dict with sunrise details
            sunrise_reading = {
                "type": "sun",
                "time": (sunrises[y]),
                "label": "Sunrise"
            }

            # Add to list (Sunrises will always take place after the hourly weather reading, this is ordered correctly)
            weather_readings.append(sunrise_reading)
            day_code = "d"

        # If sunset date (hour only) of hour available matches (note that each sunrise has a corresponding sunset, so the iteration matches)
        if sunsets[y][0:13] == times[x][0:13]:

            # Create a dict with sunrise details
            sunset_reading = {
                "type": "sun",
                "time": (sunsets[y]),
                "label": "Sunset"
            }

            # Add to list (Sunrises will always take place after the hourly weather reading, this is ordered correctly)
            weather_readings.append(sunset_reading)
            day_code = "n"

# Writes weather readings to JSON file for use with website
weather_readings_json = json.dumps(weather_readings)
with open("/var/www/html/data/weather.json", "w") as outfile:
    outfile.write(weather_readings_json)

