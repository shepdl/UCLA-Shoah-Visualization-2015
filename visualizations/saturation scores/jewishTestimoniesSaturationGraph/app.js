(function(){
	var app=angular.module('thresholdLookup',[]);
	
	app.controller('TestimonyController',["$scope", function($scope){

		$scope.check=1;
		$scope.refreshCheck=function(){
			$scope.check++;
		};

		//Setting up some scope variables / jsonArrays
		$scope.countArray = [0, 0, 0, 1, 1, 0, 2, 4, 8, 13, 21, 22, 28, 43, 39, 60, 96, 86, 128, 135, 225, 247, 279, 344, 388, 524, 554, 634, 765, 764, 913, 1050, 1105, 1162, 1225, 1400, 1394, 1443, 1382, 1337, 1658, 1356, 1382, 1358, 1271, 1234, 1241, 1188, 1103, 793, 1202, 909, 873, 786, 731, 704, 664, 566, 514, 412, 458, 412, 355, 331, 316, 306, 282, 233, 252, 215, 219, 191, 174, 180, 157, 167, 103, 111, 111, 86, 84, 48, 46, 28, 37, 17, 12, 15, 7, 7, 1, 4, 0, 0, 0, 1, 0, 0, 0, 0, 3];
		$scope.countUniqueArray=[];
		$scope.testimonyDetails10={};
		$scope.testimonyUniqueDetails10={};
		$scope.currentBin="24";
		$scope.readJSON=function(){
			//Setting up the "this" variable for the data bind. 
			var tempThis=$scope;	
			//Read All four JSON files: 
			d3.json("testimony_details_20.json",function(data){
				$scope.$apply(function(){
					tempThis.testimonyDetails10=data;
				});
			});
			
		};


		$scope.preprocessData=function(){
			$scope.readJSON();	
            //Call function to draw the D3 component here.
            $scope.d3Append(10);	
        };
        $scope.d3Append=function(splits){

        	var mydata=$scope.countArray;
        	var margin = {top: 20, right: 20, bottom: 30, left: 40},
        	width = 1078 - margin.left - margin.right,
        	height =1000 - margin.top - margin.bottom;

        	var x = d3.scale.linear()
        	.range([0, width]);

        	var y = d3.scale.linear()
        	.domain([0,height])	
        	.range([height, 0]);

        	var xAxis = d3.svg.axis()
        	.scale(x)
        	.orient("bottom")
        	.ticks(10);

        	var yAxis = d3.svg.axis()
        	.scale(y)
        	.orient("left")
        	.ticks(20);

        	var svg = d3.select("body").select("#graph")
        	.append("svg")
        	.attr("width", width + margin.left + margin.right)
        	.attr("height", height + margin.top + margin.bottom)
        	.style("background-color","white")
        	.append("g")
        	.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

		var i=0;
	  svg.append("g")
		  .attr("class", "x axis")
		  .attr("transform", "translate(0," + height + ")")
		  .call(xAxis);

	  svg.append("g")
		  .attr("class", "y axis")
		  .call(yAxis)
		  .append("text")
		  .attr("transform", "rotate(-90)")
		  .attr("y", 6)
		  .attr("dy", ".50em")
		  .style("text-anchor", "end")
		  .text("No of Testimonies/2");

	  var val=1;
	  svg.selectAll(".bar")
		  .data(mydata)
		  .enter().append("rect")
		  .attr("class", "bar")
		  .attr("x", function(d) { val=val+10; return (val); })
		  .style("fill","#9B73A9")
		  .attr("width", 8)
		  .attr("y", function(d) { return height-d/2; })
		  .attr("height", function(d) { return d/2; })
		  .on("click",function(d,i){
		  	$scope.$apply(function(){
		  		$scope.currentBin=i;
		  	});	
		  })
		  .on("mouseover", function(){ 
					//$scope.currentBin="50";
					var sofar=d3.select(this);
					sofar.style("fill","yellow");
				})
		  .on("mouseout", function(){
		  	var sofar=d3.select(this);
		  	sofar.style("fill","#9B73A9");
		  });
		};
	}]);
})();
