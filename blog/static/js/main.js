


// Footer Year Update
function myClock() {
    var today = new Date(),
        date = [today.getFullYear()];
    document.getElementById('time').innerHTML = [date];
    setTimeout(myClock, 1000);
}

myClock(); // call