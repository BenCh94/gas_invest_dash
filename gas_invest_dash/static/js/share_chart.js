shareData = JSON.parse(shareData);myLineChart = "";
var pageHeight = $(window).height();
console.log(pageHeight);
var pageWidth = $(window).width();
// Utility Functions
function getClosePrices(data){
    var closePrices = []
    data.forEach(function(d){
        closePrices.push(Number(d.close));
    })
    console.log(closePrices)
    return closePrices
}

function getDailyLabels(data){
    var days = []
    data.forEach(function(d){
        var day = new Date(d.date)
        days.push(day.toDateString());
    })
    console.log(days)
    return days
}

// Chart settings

var priceData =  {
        labels: getDailyLabels(shareData),
        datasets: [{
            label: "Share Price",
            backgroundColor: 'rgb(45, 134, 51, 0.2)',
            borderColor: 'rgb(45, 134, 51)',
            data: getClosePrices(shareData),
        }],
    };

var priceOptions = {
    maintainAspectRatio: false,
    elements: {
        line: {
            tension: 0, // disables bezier curves
        }
    },
    scales: {
            xAxes: [{
                time: {
                    unit: 'day'
                },
                display: false
            }]
        }
}


function redrawGraph(data, status){
    // Price chart
    var pricectx = document.getElementById("share-price-chart");
    pricectx.height = pageHeight*0.5;
    priceData =  {
        labels: getDailyLabels(data),
        datasets: [{
            label: "Share Price",
            backgroundColor: 'rgb(45, 134, 51, 0.2)',
            borderColor: 'rgb(45, 134, 51)',
            data: getClosePrices(data),
        }]
    };
    if(myLineChart){
        myLineChart.destroy();
    }

    myLineChart = new Chart(pricectx, {
        type: 'line',
        data: priceData,
        options: priceOptions
    });

}

function getSharePriceData(time){
    ticker=ticker
    $.get("https://api.iextrading.com/1.0/stock/"+ ticker +"/chart/"+time, 
        function(data, status){
            redrawGraph(data, status)
    })
}


// Charts
$(document).ready(function(){
    $(".priceChart").click(function(e){
        $('.priceChart').removeClass('active');
        $('#timeIn').removeClass('active');
        $(this).addClass('active');
        var time = e.target.id;
        console.log(time)
        getSharePriceData(time);
    })
    $('#timeIn').click(function(){
        $('.priceChart').removeClass('active');
        $('#timeIn').addClass('active');
        redrawGraph(shareData, 'Time In');
    })
    var pricectx = document.getElementById("share-price-chart");
    pricectx.height = pageHeight*0.5;

    var myLineChart = new Chart(pricectx, {
        type: 'line',
        data: priceData,
        options: priceOptions
    });
    $('#timeIn').addClass('active');
})