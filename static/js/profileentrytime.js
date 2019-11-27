function adjustUTC(){
    var utcDateTimes = document.getElementsByClassName("entry_datetime");
    var i = 0;
    for (i=0; i < utcDateTimes.length; i++){
        var new_date = new Date(utcDateTimes[i].innerHTML);
        var time_hours = new_date.getHours();
        var tz = new_date.getTimezoneOffset();
        time_hours -= tz/60;
        if (time_hours < 0){
            time_hours += 24;
        }
        new_date.setHours(time_hours);
        utcDateTimes[i].innerHTML = new_date.toString().slice(0,-33);
    }
}
adjustUTC();