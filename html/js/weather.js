async function getWeatherData(){
    /*
    Asynchronous function to retrieve weather data from json file using fetch
    Async to allow waiting for API response before calling
    */
    const response = await fetch("/data/weather.json"); // Gets JSON response
    const data = await response.json(); // Converts to JSON, stores as data
    addWeatherToPage(data); // Calls function with data
    
}

function addWeatherToPage(data){
    /*
    Function to add to page. Takes data and retrieves needed info, adds to html
    */

    let hourIndex = getHourIndex(data); // Calls function to get index of current hour
    let hourLimit = screen.width / 180 // Variable to control amount of hour windows visible


    // Adds element for location of weather source
    document.getElementById('weather-location').innerHTML=`
    <h2>${data[0].city}, ${data[0].region}</h2>
    `;

    if (hourIndex != 0){ // If the hour index isnt the meta data

        for (let i = hourIndex; i < hourIndex + hourLimit; i++){ // Iterates through each index from current to last

            const hour = document.createElement('ul'); // Creates a list for each hour
            hour.classList.add('reading-list'); // Adds it to class for hour handling
            hour.classList.add('weather-hour'); // Adds it to class for hour handling
            hour.classList.add('box'); // Adds it to class for box 

            if (data[i].type == "weather"){ // If the hour is a weather indicator


                // Build html list of weather
                hour.innerHTML=`
                <li><h2>${data[i].time.slice(11)}</h2></li>
                <li class = "list-icon"><img class="icon icon-weather" src="data/icons/${data[i].code}.svg" ></li>
                <li class = "list-weather"><p>${data[i].weather}</p></li>
                <li class = "list-temp"><h2>${data[i].temp}°</h2></li>
                <li><div class = "flex-container wind"><p>${data[i].windspeed} <br> MPH</p><img class="icon icon-wind" src="data/icons/wind.svg"></div></li>
                `;

            }else if (data[i].type == "sun"){ // If the hour is a sun indicator
                // Build html list of sun(set/rise)
                hour.innerHTML=`
                <li><h2>${data[i].time.slice(11)}</h2></li>
                <li class = "list-icon"><img class="icon icon-sun" src="data/icons/${data[i].label}.svg"></li>
                <li><p>${data[i].label}</p></li>
                `;
            }
            

            document.getElementById('weather-hours').appendChild(hour); // Add the list to weather hours box

        }
    }


    // If statement based on if GPS returned valid data, displays icon depending on this
    if (data[0].gps_status == true){
        gps_icon = `${data[0].last_gps_update} <img class="icon icon-gps" src="data/icons/GPS.svg">  `
    } else {
        gps_icon = '<img class="icon icon-gps" src="data/icons/IP.svg">'
    }


    // Add element for last update to weather data
    document.getElementById('weather-update').innerHTML=`
    <h4> ${data[0].last_update} <img class="icon icon-gps" src="data/icons/weather.svg"> </br>${gps_icon}</h4>
    `;

}

function getHourIndex(data){
    /*
    Function to return index of the current hour
    */
    let currentDate = new Date().toString().substring(0,18); // Declare constant for current time

    for (let i = 1; i < data.length; i++){ // Iterate through data
        if (currentDate == new Date(data[i].time).toString().substring(0,18)){ // If matching current hour
            return i; // Return the index
        }
    }
    return 0 // Return 0 to skip
}


getWeatherData(); // Calls function
