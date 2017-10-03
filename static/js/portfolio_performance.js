function print_filter(filter){
	var f=eval(filter);
	if (typeof(f.length) != "undefined") {}else{}
	if (typeof(f.top) != "undefined") {f=f.top(Infinity);}else{}
	if (typeof(f.dimension) != "undefined") {f=f.dimension(function(d) { return "";}).top(Infinity);}else{}
	console.log(filter+"("+f.length+") = "+JSON.stringify(f).replace("[","[\n\t").replace(/}\,/g,"},\n\t").replace("]","\n]"));
}

var ndx = crossfilter(JSON.parse(portfolio_data));

var dateDim = ndx.dimension(function(d) {return d.date;});
var investedDim = ndx.dimension(function(d) {return d.invested;});
var gainDim = ndx.dimension(function(d) {return d.gain_loss;});
var percentDim = ndx.dimension(function(d) {return d.percentage_gain;});


var invested_filter = investedDim.filter(206.78);
print_filter('invested_filter');