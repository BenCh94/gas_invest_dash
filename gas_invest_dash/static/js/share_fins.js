var pageHeight = $(window).height();
console.log(pageHeight);
var pageWidth = $(window).width();


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


$(document).ready(function(){
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
