shareData = JSON.parse(shareData);
var pageHeight = $(document).height();
var pageWidth = $(document).width();
$('#share-price-chart').height(pageHeight*0.6)
$('#share-price-chart').width(pageWidth)

function getClosePrices(data){
	closePrices = []
	data.forEach(function(d){
		closePrices.push(Number(d.close));
	})
	console.log(closePrices)
	return closePrices
}

function getLabels(data){
	days = []
	data.forEach(function(d){
		var day = new Date(d.date)
		days.push(day.toDateString());
	})
	console.log(days)
	return days
}

var dataInput =  {
        labels: getLabels(shareData),
        datasets: [{
            label: "Share Price",
            backgroundColor: 'rgb(45, 134, 51, 0.2)',
            borderColor: 'rgb(45, 134, 51)',
            data: getClosePrices(shareData),
        }]
    };

var optionsSetting = {
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

var ctx = document.getElementById("share-price-chart");

var myLineChart = new Chart(ctx, {
    type: 'line',
    data: dataInput,
    options: optionsSetting
});