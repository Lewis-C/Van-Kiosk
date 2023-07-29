
function readTilt() {

    // Read tilt sensor readings
    $(document).ready(function() {
        $.ajax({
            type: "GET",
            url: "/data/tilt.csv",
            dataType: "text",
            success: function (data){
                data = $.csv.toArray(data);
                // Call function to handle
                dispTilt(parseFloat(data[0]),parseFloat(data[1]),parseFloat(data[2]))
            }
         });
    });
    // After 3 second, call function again
    setTimeout(readTilt, 3000); 
}

function dispTilt(date, roll, pitch){
    // If not NAN for roll
    if (!(isNaN(roll))) {
        // Change value reading
        document.getElementById("roll-value").innerHTML=`
        ${roll}°
        `
        // Rotate by van icon by degrees
        document.getElementById("roll-icon").style.transform = `rotate(${roll}deg)`
        
        // Rotate bounds (lower and upper of dial)
        document.getElementById("roll-percentage-lb").style.transform= `rotate(${tiltLB(roll)}deg)`
        document.getElementById("roll-percentage-ub").style.transform= `rotate(${tiltUB(roll)}deg)`

        // Chaneg colours dependent on rag
        document.getElementById("roll-percentage-ub").style.backgroundColor = tiltRAG(roll)
        document.getElementById("roll-gauge").style.backgroundColor = tiltRAG(roll)


    }

    // If not nan for pitch
    if (!(isNaN(pitch))) {

        // Change value reading
        document.getElementById("pitch-value").innerHTML=`
        ${pitch}°
        `
        
        // Change rotate of icon 
        document.getElementById("pitch-icon").style.transform = `rotate(${pitch}deg)`

        // Rotate dial (upper bound and lower bound)
        document.getElementById("pitch-percentage-lb").style.transform= `rotate(${tiltLB(pitch)}deg)`
        document.getElementById("pitch-percentage-ub").style.transform= `rotate(${tiltUB(pitch)}deg)`

        // Change RAG colour
        document.getElementById("pitch-percentage-ub").style.backgroundColor = tiltRAG(pitch)
        document.getElementById("pitch-gauge").style.backgroundColor = tiltRAG(pitch)
    }
    
}

function tiltLB(tilt){
    // Function for lower bound of dial
    // Scales to 2 for focus on relevant values
    // Adds 89 (center of dial is 0, so rotate 90 = 0. gap of 2 degrees means 89 - 91 adjustment)
    return((tilt*2)+89)
}

function tiltUB(tilt){
    // Function for lower bound of dial
    // Scales to 2 for focus on relevant values
    // Adds 89 (center of dial is 0, so rotate 90 = 0. gap of 2 degrees means 89 - 91 adjustment)
    return((tilt*2)+91)
}

function tiltRAG(tilt){
    // If within 5 degrees good
    if (tilt > -5 && tilt < 5) {
        return "Green"
    }
    // If out of 5 but within 20 bad
    else if (tilt > -20 || tilt < 20){
        return "Orange"
    }
    // Shit
    else {
        return "Red"
    }
}

readTilt()