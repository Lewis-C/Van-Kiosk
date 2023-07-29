
// Constants
const weekdays = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]; // List of weekdays, accessible via day number
const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]; // List of months, accessible via month number

// Global Variables
var date = 0; // Date is declared initially to allow for flag to show date is not set

function startTime() {
  /*
  Function to start the time count. Designed to recurse every second, and retrieve date each time. 
  The date is then restructured to a displayable string and passed to the time html.
  */
  
  const today = new Date(); // Declare constant for current time
  let hours = today.getHours(); // Get hours from constant
  let minutes = today.getMinutes(); // Get  minutes
  let seconds = today.getSeconds(); // Get seconds

  getDate(today); // Calls date function

  hours = checkTime(hours); // Call checktime function to ensure time has 0 before if less than 10
  minutes = checkTime(minutes); // Call checktime function to ensure time has 0 before if less than 10
  seconds = checkTime(seconds); // Call checktime function to ensure time has 0 before if less than 10
  document.getElementById('time').innerHTML =  hours + ":" + minutes + ":" + seconds; // Concat hours minutes and seconds into string and pass to html
  setTimeout(startTime, 1000); // After 1 second, call function again
}

function checkTime(value) {
  /*
  Function to format any values in time to have 0 in front of, if needed
  Takes value as parameter and returns once formatted
  */
  if (value < 10) {value = "0" + value};  // add zero in front of numbers < 10
  return value; // Return formatted value
}

function getDate(today){
  /*
  Function to get date. Retrieves date value, formats for view and updates html
  If statement consider if date is neeeded to be update, not done with time for perfomance
  */ 
  if (date != today.getDate()) { // Finds if day needs to be updated
    let day = weekdays[today.getDay()]; // declares variable for day, taking day int and using days list to find relevant string
    date = today.getDate(); // declares variable for date
    let month = months[today.getMonth()]; // declares variable for month, taking month int and using monmth list to find relevant string
    let year = today.getFullYear(); // declaries variable for year
    document.getElementById('date').innerHTML =`${day} ${date}<sup>${getOrdinalSuffix(date)}</sup> ${month}, ${year}`; // Concat date into string and send to html
  }
}

function getOrdinalSuffix(date){
  if (date > 3 && date < 21) return 'th'; // If date is between 4 and 21, return th
  switch (date % 10) {  // Else switch based on its single digit
    case 1:  return "st"; // st for any 1s
    case 2:  return "nd"; // nd for any 2s
    case 3:  return "rd"; // rd for any 3s
    default: return "th"; // otherwisemm th
  }
}

function getTimezone(){
  /*
  Function to get timezone currently used by pi then format it for display.
  Once formatted, passed to html timezone
  */
  let timezone = (Intl.DateTimeFormat().resolvedOptions().timeZone) // Declares local variable for timezone
  timezone = timezone.split('/')[1] // Gets the second section of the timezone (Europe/London = London)
  timezone = timezone.replace(/_/g, " ") // Replaces any underscores with spaces for view
  document.getElementById('timezone').innerHTML = timezone; // Passes to HTML indicator
}

// Function calls
getTimezone();
startTime();






