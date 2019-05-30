var activeCategories = {};

var init = function () {
    data = pv.flatten(data)
        .key("topic")
        .key("segment")
        .key("count")
        .array();
    for (var i in data) {
        var index = i.replace(/\W/, "-");
        activeCategories[index] = {
            name : i,
            active: true
        };
        $("#category-list-item-template").clone()
            .text(i)
            .attr("id", "item-" + i.replace(/\W/, '-'))
            .addClass("active")
            .appendTo("#category-list")
            .show();
    }
    $(".category").click(function ($e) {
        var target = $($e.target);
        if (target.hasClass("active")) {
            target.removeClass("active");
            activeCategories[target.attr("id")] = false;
        } else {
            target.addClass("active");
            activeCategories[target.attr("id")] = true;
        }
        drawTimeline();
    });
    drawTimeline();
}

var topicColors = {
    'captivity' : "#0067A5",
    'culture' : "#B3446C",
    'daily life' : "#008000",
    'discrimination' : "#875692",
    'discrimination responses' : "#C2B280",
    'economics' : "#fce5f9",
    'feelings and thoughts' : "#E25822",
    'forced labor' : "#654522",
    'government' : "#F99379",
    'health' : "#604E97",
    'liberation' : "#BE0032",
    'mistreatment and death' : "#DCD300",
    'movement' : "#848482",
    'organizations' : "#882D17",
    'people' : "#E68FAC",
    'politics' : "#008856",
    'post-conflict' : "#F38400",
    'refugee experiences' : "#8DB600",
    'religion and philosophy' : "#A1CAF1",
    'still and moving images' : "#0000FF",
    'time and place' : "#F6A600",
    'weapons' : "#abe16b",
    'world histories' : "#F3C300",
};

var getData = function (victimGroupName) {
    $.get(
        '/data/' + victimGroupName + '.js', 
        {},
        drawTimeline,
        'json'
    );
};

var drawTimeline = function (data) {

    data = pv.flatten(data)
        .key("topic")
        .key("segment")
        .key("count")
        .array();

    // TODO: find sum of topic by segment
    var sumBySegment = pv.nest(data)
            .key(function (d) {
                return d.segment
            })
            .rollup(function (v) {return pv.sum(v, function (d) { return d.count})}),
        sumByTopic = pv.nest(data)
            .key(function (d) { return d.topic})
            .rollup(function(v) { return pv.sum(v, function(d) { return d.count} )});

    data.forEach(function(d) {
        if (isNaN(d.count) || isNaN(d.segment) || isNaN(sumBySegment[d.segment])
            || isNaN(100 * d.count / sumBySegment[d.segment])
        ) {
            d.percent = 0;
        }
        else d.percent = 100 * d.count / sumBySegment[d.segment]
    } );

    /* Sizing parameters and scales. */
    var w = 1000,
        //h = 800,
        h = 700,
        //x = pv.Scale.linear(1850, 2000).range(0, w),
        x = pv.Scale.linear(0, 100).range(0, w),
        y = pv.Scale.linear(0, 100).range(0, h),
        color = pv.Scale.ordinal(1, 2).range("#33f", "#f33"),
        alpha = pv.Scale.linear(pv.values(sumBySegment)).range(.4, .8);

    /* The root panel. */
    var vis = new pv.Panel()
        .canvas("fig")
        .width(w)
        .height(h)
        .top(9.5)
        .left(39.5)
        .right(20)
        .bottom(30);

    /* A background bar to reset the search query.  */
    vis.add(pv.Bar)
        .fillStyle("white")
        // .event("click", function() search(""))
        .cursor("pointer");

    /* Y-axis ticks and labels. */
    vis.add(pv.Rule)
        .data(function() { return y.ticks()} )
        .bottom(y)
        .strokeStyle(function(y) {return  y ? "#ccc" : "#000"} )
      .anchor("left").add(pv.Label)
        .text(function(d) { return y.tickFormat(d) + "%"});

    /* Stack layout. */
    var area = vis.add(pv.Layout.Stack)
        .layers(function() {
            return  pv.nest(data)//.filter(test))
                .key(function(d) {return  d.topic })
            //.key(function(d) { d.gender + d.job})
                .sortKeys(function(a, b) {
                    return  pv.reverseOrder(a.substring(1), b.substring(1))
                } )
            .entries()
        }).values(function(d) { return d.values} )
        //.x(function(d) { x(d.year)} )
            .x(function(d) { return x(d.segment)} )
            .y(function(d) {
                if (d == undefined) {
                    return 0;
                }
                //console.log(d);
                return y( d.percent)
            } )
            //.fillStyle(function (d) { console.log(d); return '#f00';})

      .layer.add(pv.Area)
      .fillStyle(function (d) { return topicColors[d.topic]; })
        //.def("alpha", function(d) { alpha(sumByJob[d.key])} )
        .def("alpha", function(d) {return  alpha(sumByTopic[d.key])} )
        //.fillStyle(function(d) { color(d.gender).alpha(this.alpha())} )
        .cursor("pointer")
        //.event("mouseover", function(d)  { this.alpha(1).title(d.job)} )
        .event("mouseover", function(d)  {return  this.alpha(1).title(d.topic)} )
        .event("mouseout", function(d) { return this.alpha(null)} )
        .event("click", function(d) { return search("^" + d.job + "$") } );

    /* Stack labels. */
    vis.add(pv.Panel)
        .extend(area.parent)
      .add(pv.Area)
        .extend(area)
        .fillStyle(null)
      .anchor("center").add(pv.Label)
        .def("max", function(d) { return pv.max.index(d.values, function(d)  { return d.percent}) } )
        .visible(function() { return this.index == this.max()} )
        .font(function(d) {return  Math.round(5 + Math.sqrt(y(d.percent))) + "px sans-serif"} )
        .textMargin(6)
        .textStyle(function(d) { return "rgba(0, 0, 0, " + (Math.sqrt(y(d.percent)) / 7) + ")"} )
        .textAlign(function() {return  this.index < 5 ? "left" : "right"} )
        .text(function(d, p) { return p.key/*.substring(1)*/} );

    /* X-axis ticks and labels. */
    vis.add(pv.Rule)
        .data(pv.range(0, 100, 10))
        .left(x)
        .bottom(-6)
        .height(5)
      .anchor("bottom").add(pv.Label);

    /* Update the query regular expression when text is entered. */
    function search(text) {
      if (text != re) {
        if (query.value != text) {
          query.value = text;
          query.focus();
        }
        re = new RegExp(text, "i");
        //update();
      }
    }

    /* Tests to see whether the specified datum matches the current filters. */
    function test(d) {
      return (!gender || d.gender == gender) && d.job.match(re);
    }

    /* Recompute the y-scale domain based on query filtering. */
    function update() {
      y.domain(0, Math.min(100, pv.max(pv.values(pv.nest(jobs.filter(test))
          .key(function(d) { return d.year} )
          .rollup(function(v) { return pv.sum(v, function(d) { return d.percent} )} )))));
      vis.render();
    }

    vis.render();
    drawLegend();
}

var legendDrawn = false;
function drawLegend(){
    if (legendDrawn) {
        return
    }
  var table = document.getElementById("table");
  var i = 0;
  for (key in topicColors) {
    var row = table.insertRow(-1);
    var cell1 = row.insertCell(0);
    var cell2 = row.insertCell(1);
    cell1.style.backgroundColor = topicColors[key];
    cell1.style.width = '1vw';
    cell2.innerHTML = key;
    console.log(key);
  }
    legendDrawn = true;
}
