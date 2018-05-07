function print_filter(filter){
	var f=eval(filter);
	if (typeof(f.length) != "undefined") {}else{}
	if (typeof(f.top) != "undefined") {f=f.top(Infinity);}else{}
	if (typeof(f.dimension) != "undefined") {f=f.dimension(function(d) { return "";}).top(Infinity);}else{}
	console.log(filter+"("+f.length+") = "+JSON.stringify(f).replace("[","[\n\t").replace(/}\,/g,"},\n\t").replace("]","\n]"));
}

function orderByDate(d){
    return d.date
}

portfolio_data = JSON.parse(portfolio_data);
// console.log(portfolio_data);

var ndx = crossfilter(portfolio_data);

var parseDate = d3.time.format("%Y-%m-%d").parse;
for(var i=0;i<portfolio_data.length;i++){
	portfolio_data[i].date = parseDate(portfolio_data[i].date);
    portfolio_data[i].purchase_date = parseDate(portfolio_data[i].purchase_date);
}
// Dimensions //
var dateDim = ndx.dimension(function(d) {return d.date});
var shareDim = ndx.dimension(function(d) {return d.name});

// Filters //
var total_gain = dateDim.group().reduceSum(dc.pluck('gain_loss'));
var sp_gain = dateDim.group().reduceSum(dc.pluck('sp_gain_loss'));
var share_gain = shareDim.group().reduceSum(dc.pluck('invested'));
var daysIn = shareDim.groupAll();


// Utilities //
var minDate = dateDim.bottom(1)[0].date;
var maxDate = dateDim.top(1)[0].date;
var dailyWidth = $("#performance_box").width();
var colorScale = d3.scale.ordinal().range(['#003430', '#0D4E49', '#236863', '#41837E', '#699D99', '#2D8633', '#54A759', '#86C98A']);


// Graphs //
var dailyChart = dc.compositeChart("#chart-performance-day");
var sharePieChart = dc.pieChart('#share-pie');

dailyChart
	.width(dailyWidth*0.8).height(450)
	.title(function(d) {return d.key + ":" + d.value})
	.compose([
		dc.lineChart(dailyChart)
			.dimension(dateDim)
			.group(total_gain, 'Portfolio')
			.renderArea(true)
			.ordinalColors(['#17B121']),
		dc.lineChart(dailyChart)
			.dimension(dateDim)
			.group(sp_gain, 'S and P 500')
			.renderArea(true)
			.ordinalColors(['#2969CE'])
	])
	.renderHorizontalGridLines(true)
	.legend(dc.legend().x(50).y(10).itemHeight(13).gap(5))
	.yAxisLabel('($)Gain/Loss')
    .elasticY(true)
	.x(d3.time.scale().domain([minDate, maxDate]));

sharePieChart
    .width(300).height(400)
    .dimension(shareDim)
    .group(share_gain)
    .colors(colorScale)
    .innerRadius(40);

dc.renderAll();