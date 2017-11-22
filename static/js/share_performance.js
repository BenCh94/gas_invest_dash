console.log(JSON.parse(shareData));
var parseDate = d3.time.format("%Y-%m-%d").parse;
shareData = JSON.parse(shareData);
var chartWidth = $('#share-price-box').width();
// Set the dimensions of the canvas / graph
var margin = {top: 30, right: 20, bottom: 30, left: 50},
    width = chartWidth - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;
var low = 100000000000;
var high = 0;
var getmin = function(){
    shareData.forEach(function(d){
        if (parseFloat(d.adj_close) < low){
            low = parseFloat(d.adj_close)
        }
        if(parseFloat(d.adj_close) > high){
            high = parseFloat(d.adj_close)
        }
    });
    return low
};
var yscale = getmin();
var assign_values = function(){
    $('#low_val').text(low);
    $('#high_val').text(high);
};
assign_values();
// Set the ranges
var x = d3.time.scale().range([0, width]);
var y = d3.scale.linear().range([height, yscale-2]);

// Define the axes
var xAxis = d3.svg.axis().scale(x)
    .orient("bottom").ticks(5);

var yAxis = d3.svg.axis().scale(y)
    .orient("left").ticks(5);

// Define the line
var valueline = d3.svg.line()
    .x(function(d) { return x(d.date); })
    .y(function(d) { return y(d.adj_close); });


// Adds the svg canvas
var svg = d3.select("#price-chart-day")
    .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
    .append("g")
        .attr("transform",
              "translate(" + margin.left + "," + margin.top + ")");


// Get the data
var drawGrpah = function() {
    shareData.forEach(function(d) {
        d.date = parseDate(d.date);
        d.adj_close = +d.adj_close;
    });

    // Scale the range of the data
    x.domain(d3.extent(shareData, function(d) { return d.date; }));
    y.domain([yscale-2, d3.max(shareData, function(d) { return d.adj_close; })]);

    // Add the valueline path.
    svg.append("path")
        .attr("class", "line")
        .attr("d", valueline(shareData))
        .attr("stroke", 'white')
        .attr("stroke-width", 5)
        .attr("fill", 'none');

    // Add the X Axis
    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    // Add the Y Axis
    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis);

};
drawGrpah();
