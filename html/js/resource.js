const butaneFull = 5
const butaneEmpty = 0
const butaneMax = butaneFull - butaneEmpty
const waterFull = 5
const waterEmpty = 0
const waterMax = waterFull - waterEmpty

function getReadings() {


    // Read butane sensor readings
    $(document).ready(function() {
        $.ajax({
            type: "GET",
            url: "/data/tank_levels.csv",
            dataType: "text",
            success: function (data){
                data = $.csv.toArray(data);
                // Call function to handle
                dispReadings((data[0]),(parseFloat(data[1])-butaneEmpty),(parseFloat(data[2])-waterEmpty), data[3])
            }
         });
    });
    // After 3 second, call function again
    setTimeout(getReadings, 3000); 
}

function dispReadings(date, butane, water, connected){
    
    // If statement based on if GPS returned valid data, displays icon depending on this
    if (connected == "Connected"){
        icon = "data/icons/bluetooth.svg" 
    } else {
        icon = "data/icons/bluetooth-dc.svg"
    }
    
    // Change to max butane set
    document.getElementById("butane-cap").innerHTML=`
    ${butaneMax}kg
    `
    // Change to max water set
    document.getElementById("water-cap").innerHTML=`
    ${waterMax}kg
    `
    
    // Add element for last update to weather data
    document.getElementById('resource-update').innerHTML=`
    <h4> ${date} </h4><img class="icon icon-bt" src="${icon}">
    `;
    
    // Checks valid value (otherwise ignore and leave as default 0)
    if (!(isNaN(butane)) && !(butane <= 0))  {
        // Change value reading
        document.getElementById("butane-value").innerHTML=`
        ${butane.toFixed(2)}kg
        `
        
        // Change to percentae found
        document.getElementById("butane-percent").innerHTML=`
        ${percentageButane(butane)}%
        `
        
        // Fill gauge
        document.getElementById("butane-gauge").style.backgroundImage = `linear-gradient(to top,${butaneRAG(butane)} ${percentageButane(butane)}%, transparent ${percentageButane(butane)}%, transparent 100%)`
    }
    else {
        // Change value reading
        document.getElementById("butane-value").innerHTML=`
        0kg
        `
        
        // Change to percentae found
        document.getElementById("butane-percent").innerHTML=`
        0%
        `
        
        // Fill gauge
        document.getElementById("butane-gauge").style.backgroundImage = `background-image: linear-gradient(to top,green 0%, transparent 0%, transparent 100%)`
    }

    // Checks if valid value
    if ((!(isNaN(water))) && !(water <= 0)) {
        // Change value reading
        document.getElementById("water-value").innerHTML=`
        ${water.toFixed(2)}kg
        `
        
        // Change to percentae found
        document.getElementById("water-percent").innerHTML=`
        ${percentageButane(water)}%
        `

        
        // Fill gauge
        document.getElementById("water-gauge").style.backgroundImage = `linear-gradient(to top,${butaneRAG(water)} ${percentageButane(water)}%, transparent ${percentageButane(water)}%, transparent 100%)`
    }
    else {
        // Change value reading
        document.getElementById("water-value").innerHTML=`
        0kg
        `
        
        // Change to percentae found
        document.getElementById("water-percent").innerHTML=`
        0%
        `
        
        // Fill gauge
        document.getElementById("water-gauge").style.backgroundImage = `background-image: linear-gradient(to top,green 0%, transparent 0%, transparent 100%)`
    }

}


function percentageButane(butane){
    // Function to get percentage
    return(Math.round((butane/butaneMax)*100))
}

function butaneRAG(butane){
    // Function to return colour dependent and boundaries
    if (butane >= 1.5) {
        return "green"
    }
    else if (butane <= 3){
        return "red"
    }
    else {
        return "orange"
    }
}

function waterButane(water){
    // Function to get percentage
    return(Math.round((water/waterMax)*100))
}

function waterRAG(water){
    // Function to return colour dependent and boundaries
    if (water >= 1.5) {
        return "green"
    }
    else if (water <= 3){
        return "red"
    }
    else {
        return "orange"
    }
}

getReadings() 