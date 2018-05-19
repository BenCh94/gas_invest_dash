shareData = JSON.parse(shareData);
// Utility Functions
function getClosePrices(data){
	closePrices = []
	data.forEach(function(d){
		closePrices.push(Number(d.close));
	})
	console.log(closePrices)
	return closePrices
}

function getDailyLabels(data){
	days = []
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
        }]
    };

var priceOptions = {
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


// Charts
$(document).ready(function(){
    var pageHeight = $(window).height();
    var pageWidth = $(window).width();
    // Price chart
    $('#share-price-chart').height(pageHeight*0.5)
    $('#share-price-chart').width(pageWidth)
    // Rev Chart
    $('#share-revenue-chart').height(pageHeight*0.3)
    $('#share-revenue-chart').width(pageWidth/3)
    var pricectx = document.getElementById("share-price-chart");

    var myLineChart = new Chart(pricectx, {
        type: 'line',
        data: priceData,
        options: priceOptions
    });

    var revctx = document.getElementById("share-revenue-chart");

    var myBarChart = new Chart(revctx, {
        type: 'bar',
        data: revData,
        options: revSetting
    });

    var costrevctx = document.getElementById("share-costrev-chart");

    var myBarChart = new Chart(costrevctx, {
        type: 'bar',
        data: costRevData,
        options: costRevSetting
    });
})
