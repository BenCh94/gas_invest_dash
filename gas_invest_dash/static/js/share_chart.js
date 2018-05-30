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

function getRevenue(data){
    revenues = []
    data.forEach(function(d){
        revenues.push(Number(d.totalRevenue));
    })
    console.log(revenues)
    return revenues
}

function getFinLabels(data){
    days = []
    data.forEach(function(d){
        var day = new Date(d.reportDate)
        days.push(day.toDateString());
    })
    console.log(days)
    return days
}

function getCostRev(data){
    costRevs = []
    data.forEach(function(d){
        costRevs.push(Number(d.costOfRevenue));
    })
    console.log(costRevs)
    return costRevs
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

var revData =  {
        labels: getFinLabels(shareFin.financials),
        datasets: [{
            label: "Total Revenue",
            backgroundColor: 'rgb(45, 134, 51, 0.2)',
            borderColor: 'rgb(45, 134, 51)',
            data: getRevenue(shareFin.financials),
        }]
    };

var revSetting = {
    elements: {
        line: {
            tension: 0, // disables bezier curves
        }
    },
    scales: {
            xAxes: [{
                time: {
                    unit: 'day'
                }
            }]
        }
}

var costRevData =  {
        labels: getFinLabels(shareFin.financials),
        datasets: [{
            label: "Cost Of Revenue",
            backgroundColor: 'rgb(45, 134, 51, 0.2)',
            borderColor: 'rgb(45, 134, 51)',
            data: getCostRev(shareFin.financials),
        }]
    };

var costRevSetting = {
    elements: {
        line: {
            tension: 0, // disables bezier curves
        }
    },
    scales: {
            xAxes: [{
                time: {
                    unit: 'day'
                }
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

    var revctx = document.getElementById("share-revenue-chart");

    var myRevChart = new Chart(revctx, {
        type: 'bar',
        data: revData,
        options: revSetting
    });

    var costrevctx = document.getElementById("share-costrev-chart");

    var myCosRevChart = new Chart(costrevctx, {
        type: 'bar',
        data: costRevData,
        options: costRevSetting
    });
})