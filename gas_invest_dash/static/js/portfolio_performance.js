function print_filter(filter){
	var f=eval(filter);
	if (typeof(f.length) != "undefined") {}else{}
	if (typeof(f.top) != "undefined") {f=f.top(Infinity);}else{}
	if (typeof(f.dimension) != "undefined") {f=f.dimension(function(d) { return "";}).top(Infinity);}else{}
	console.log(filter+"("+f.length+") = "+JSON.stringify(f).replace("[","[\n\t").replace(/}\,/g,"},\n\t").replace("]","\n]"));
}
portfolio_data = JSON.parse(portfolio_data);

var ndx = crossfilter(portfolio_data);

var parseDate = d3.time.format("%Y-%m-%d").parse;
for(var i=0;i<portfolio_data.length;i++){
	portfolio_data[i].date = parseDate(portfolio_data[i].date)
}


print_filter(portfolio_data);
/////// Dimensions ////////
var dateDim = ndx.dimension(function(d) {return d.date;});
var investedDim = ndx.dimension(function(d) {return d.invested});
var gainDim = ndx.dimension(function(d) {return d.gain_loss;});
var percentDim = ndx.dimension(function(d) {return d.percentage_gain;});
//////////////////////////
var total_gain = dateDim.group().reduceSum(dc.pluck('gain_loss'));
var sp_benchmark = dateDim.group().reduceSum(dc.pluck('sp_gain'));
var selected_data = dateDim.filter(function(d) {return Math.max(d)});
var total_invested = selected_data.date;
var timeInMarket = ndx.groupAll();
console.log(total_invested);

var minDate = dateDim.bottom(1)[0].date;
var maxDate = dateDim.top(1)[0].date;

var dailyChart = dc.compositeChart("#chart-performance-day");
var dailyWidth = $("#performance_box").width();
// var totalInvested = dc.numberDisplay('#total-invested');
var timeIn = dc.numberDisplay('#time-in-days');
var timeInWidth = $('#time_in_box').width();
var gainsND = dc.numberDisplay('#gains-total');
var gainsWidth = $('#gains_box').width();


dailyChart
	.width(dailyWidth).height(400)
	.title(function(d) {return d.key + ":" + d.value})
	.compose([
		dc.lineChart(dailyChart)
			.dimension(dateDim)
			.group(sp_benchmark, 'S & P 500')
			.renderArea(true)
			.ordinalColors(['#2969CE']),
		dc.lineChart(dailyChart)
			.dimension(dateDim)
			.group(total_gain, 'Portfolio')
			.renderArea(true)
			.ordinalColors(['#17B121'])
	])
	.renderHorizontalGridLines(true)
	.legend(dc.legend().x(50).y(10).itemHeight(13).gap(5))
	.yAxisLabel('($)Gain/Loss')
	.x(d3.time.scale().domain([minDate, maxDate]));

timeIn
	.width(timeInWidth).height(200)
	.formatNumber(d3.format('d'))
	.valueAccessor(function (d){
		return d;
	})
	.group(timeInMarket);


dc.renderAll();
