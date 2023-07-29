
function getReadings() {


    // Read butane sensor readings
    $(document).ready(function() {
        $.ajax({
            type: "GET",
            url: "/data/tank.csv",
            dataType: "text",
            success: function (data){
                data = $.csv.toArray(data);
                // Call function to handle

                var butaneVal = parseFloat(data[2] - data[6]).toFixed(2)

                if (butaneVal < 0){
                    butaneVal = 0
                }

                var waterVal = parseFloat(data[1] - data[5]).toFixed(2)

                if (waterVal < 0){
                    waterVal = 0
                }


                var butaneMax = parseFloat(data[4] - data[6]).toFixed(2)
                
                if (butaneMax < 0){
                    butaneMax = 0
                }

                var waterMax = parseFloat(data[3] - data[5]).toFixed(2)
                
                if (waterMax < 0){
                    waterMax = 0
                }


                dispReadings(butaneVal,waterVal, butaneMax, waterMax)
            }
         });
    });
    // After 3 second, call function again
    setTimeout(getReadings, 3000); 
}

function dispReadings(butane, water, butaneMax, waterMax){
    
    // Change to max butane set
    document.getElementById("butane-cap").innerHTML=`
    ${butaneMax}kg
    `
    // Change to max water set
    document.getElementById("water-cap").innerHTML=`
    ${waterMax}kg
    `
    
    // Checks valid value (otherwise ignore and leave as default 0)
    if (!(isNaN(butane)) && !(butane <= 0))  {
        // Change value reading
        document.getElementById("butane-value").innerHTML=`
        ${butane}kg
        `
        
        // Change to percentae found
        document.getElementById("butane-percent").innerHTML=`
        ${valPercent(butane,butaneMax)}%
        `
        
        // Fill gauge
        document.getElementById("butane-gauge").style.backgroundImage = `linear-gradient(to top,${butaneRAG(valPercent(butane,butaneMax))} ${valPercent(butane,butaneMax)}%, transparent ${valPercent(butane,butaneMax)}%, transparent 100%)`
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
        document.getElementById("butane-gauge").style.backgroundImage = `linear-gradient(to top,green 0%, transparent 0%, transparent 100%)`
    }

    // Checks if valid value
    if ((!(isNaN(water))) && !(water <= 0)) {
        // Change value reading
        document.getElementById("water-value").innerHTML=`
        ${water}kg
        `
        
        // Change to percentae found
        document.getElementById("water-percent").innerHTML=`
        ${valPercent(water,waterMax)}%
        `

        
        // Fill gauge
        document.getElementById("water-gauge").style.backgroundImage = `linear-gradient(to top,${waterRAG(valPercent(water,waterMax))} ${valPercent(water,waterMax)}%, transparent ${valPercent(water,waterMax)}%, transparent 100%)`
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
        document.getElementById("water-gauge").style.backgroundImage = `linear-gradient(to top,green 0%, transparent 0%, transparent 100%)`
    }

}


function valPercent(value,max){
    // Function to get percentage
    return (Math.round((value/max)*100))
}

function butaneRAG(butane){
    // Function to return colour dependent and boundaries
    if (butane >= 50) {
        return "green"
    }
    else if (butane <= 25){
        return "red"
    }
    else {
        return "orange"
    }
}

function waterRAG(water){
    // Function to return colour dependent and boundaries
    if (water >= 50) {
        return "green"
    }
    else if (water <= 25){
        return "red"
    }
    else {
        return "orange"
    }
}

getReadings() 