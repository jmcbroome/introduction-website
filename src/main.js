var map = L.map('mapid', {'tap':false}).setView([37.8, -96], 4);
var global_state = "default";
var global_time = "";
var global_state_id = "00";
// var host = "raw.githubusercontent.com/jmcbroome/introduction-website/main/"
var map_colors = ['#800026','#BD0026','#E31A1C','#FC4E2A','#FD8D3C','#FEB24C','#FED976','#FFEDA0'];
var color_scale = "log";
var max_basecount = 0;
for (i = 0; i < introData.features.length; i++) {
    let bc = introData.features[i]["properties"]["intros"]["basecount"];
    if (bc > max_basecount) {
        max_basecount = bc;
    }
}

function maxClusterCt(region_id,timel) {
    var maxn = 0;
    let item = timel + "raw" + region_id;
    for (i = 0; i < introData.features.length; i++) {
        let c = introData.features[i]["properties"]["intros"][item];
        if (c > maxn) {
            maxn = c;
        }
    }
    return maxn;
}

function getColorBase(d) {
    return d > max_basecount * 0.9 ? map_colors[0] :
           d > max_basecount * 0.75   ? map_colors[1] :
           d > max_basecount * 0.5   ? map_colors[2] :
           d > max_basecount * 0.25   ? map_colors[3] :
           d > max_basecount * 0.1    ? map_colors[4] :
           d > max_basecount * 0.05   ? map_colors[5] :
           d > max_basecount * 0.01    ? map_colors[6] :
                      map_colors[7];
}

function getColorIntroN(d, max) {
    return d > max * 0.9  ? map_colors[0] :
           d > max * 0.75 ? map_colors[1] :
           d > max * 0.5  ? map_colors[2] :
           d > max * 0.25 ? map_colors[3] :
           d > max * 0.1  ? map_colors[4] :
           d > max * 0.05 ? map_colors[5] :
           d > max * 0.01 ? map_colors[6] :
                      map_colors[7];
}

function getColorBin(d, max) {
    return d > max * 0.9  ? '1' :
           d > max * 0.75 ? '2' :
           d > max * 0.5  ? '3' :
           d > max * 0.25 ? '4' :
           d > max * 0.1  ? '5' :
           d > max * 0.05 ? '6' :
           d > max * 0.01 ? '7' :
                      '8';
}

function getColorIntro(d) {
    return d > 1 ? map_colors[0] :
        d > 0.75  ? map_colors[1] :
        d > 0.5  ? map_colors[2] :
        d > 0.25  ? map_colors[3] :
        d > 0   ? map_colors[4] :
        d > -0.25   ? map_colors[5] :
        d > -0.5   ? map_colors[6] :
                    map_colors[7];
}

function setTimeLabels(sel) {
    if (sel == 0) {
        //whole pandemic
        document.getElementById("btn_time_0").classList.add("btn_selected");
        document.getElementById("btn_time_12").classList.remove("btn_selected");
        document.getElementById("btn_time_6").classList.remove("btn_selected");
        document.getElementById("btn_time_3").classList.remove("btn_selected");
    } else if (sel == 12) {
        //last 12 months
        document.getElementById("btn_time_0").classList.remove("btn_selected");
        document.getElementById("btn_time_12").classList.add("btn_selected");
        document.getElementById("btn_time_6").classList.remove("btn_selected");
        document.getElementById("btn_time_3").classList.remove("btn_selected");
    } else if (sel == 6) {
        //last 6 months
        document.getElementById("btn_time_0").classList.remove("btn_selected");
        document.getElementById("btn_time_12").classList.remove("btn_selected");
        document.getElementById("btn_time_6").classList.add("btn_selected");
        document.getElementById("btn_time_3").classList.remove("btn_selected");
    } else if (sel == 3) {
        //last 3 months
        document.getElementById("btn_time_0").classList.remove("btn_selected");
        document.getElementById("btn_time_12").classList.remove("btn_selected");
        document.getElementById("btn_time_6").classList.remove("btn_selected");
        document.getElementById("btn_time_3").classList.add("btn_selected");
    }
}

function style(feature) {
    return {
        fillColor: getColorBase(feature.properties.intros[global_time + "basecount"]),
        weight: 2,
        opacity: 1,
        color: 'white',
        dashArray: '3',
        fillOpacity: 0.7
    };
}

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png?{foo}', {foo: 'bar', attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'}).addTo(map);

var geojson;
geojson = L.geoJson(introData, {
    style: style,
    onEachFeature: onEachFeature
}).addTo(map);

//control to display data for each region on hover
var info = L.control();

info.onAdd = function (map) {
    this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
    this.update();
    return this._div;
};

// method to update the info panel control based on feature properties passed
info.update = function (props) {
    // this._div.innerHTML = '<h4>US Population Density</h4>' +  (props ?
    //     '<b>' + props.name + '</b><br />' + props.density + ' people / mi<sup>2</sup>'
    //     : 'Hover over a state');
    if (global_state == "default") {
        this._div.innerHTML = '<h4># Clusters in ' + (props ? '<b>' + props.name + '</b><br />' + props.intros[global_time + "basecount"] : 'Hover over a state');
    } else {
        str = '<h4># Introductions to ' + global_state + ' from ';
        if (props) {
            keyval = global_time + "raw" + global_state_id;
            if (keyval in props.intros){
                countval = props.intros[keyval];
            } else {
                countval = 0;
            }
            str += '<b>' + props.name + '</b><br />' + countval;
        } else {
            str += 'Hover over a state';
        }
        this._div.innerHTML = str;
    }
};

function highlightFeature(e) {
    var layer = e.target;

    layer.setStyle({
        weight: 5,
        color: '#666',
        dashArray: '',
        fillOpacity: 0.7
    });

    if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
        layer.bringToFront();
    }
    info.update(layer.feature.properties);
}

function resetHighlight(e) {
    //geojson.resetStyle(e.target);
    e.target.setStyle({
        weight: 2,
        opacity: 1,
        color: 'white',
        dashArray: '3',
        fillOpacity: 0.7
    })
    info.update();
}

function resetView(e) {
    geojson.eachLayer(function (layer) {
        geojson.resetStyle(layer);
    });
    global_state = "default";
    global_state_id = "00";
    var btn = document.getElementById("colorbtn");
    btn.disabled = true;
    btn.innerText = "Show Raw Cluster Count";
    color_scale = "log";
    legend.update(global_state);
    showRegion(global_state);
}

function changeMap(time) {
    setTimeLabels(time);
    if (time == 0) {
        //reset to default
        global_time = "";
    } else {
        global_time = time + "_";
    }
    if (global_state != "default") {
        geojson.eachLayer(function (layer) {
            if (layer.feature.id == global_state_id) {
                layer.setStyle({fillColor: "#1a0080"});
            } else {
                colorIntros();
            }
        });
    } else {
        resetView();
    }
}

function zoomToFeature(e) {
    map.fitBounds(e.target.getBounds());
}

function changeView(e) {
    //code to change the displayed heatmaps to the matching intro index
    var clicklayer = e.target;
    if (e.target.options.fillColor == "#1a0080") {
        resetView(e);
    } else {
        global_state = e.target.feature.properties.name;
        global_state_id = e.target.feature.id;
        clicklayer.setStyle({fillColor: "#1a0080"});
        colorIntros();
        document.getElementById("colorbtn").disabled = false;
        legend.update(global_state);
        showRegion(global_state);
    }
}

function colorIntros() {
    if (color_scale == "raw") {
        //find max number of clusters
        let maxn = maxClusterCt(global_state_id,global_time);
        //set colors
        geojson.eachLayer(function (layer) {
            if (layer.feature.id != global_state_id) {
                layer.setStyle({fillColor: getColorIntroN(layer.feature.properties.intros[global_time + "raw" + global_state_id],maxn)});
            }
        });
    } else {
        //set colors
        geojson.eachLayer(function (layer) {
            if (layer.feature.id != global_state_id) {
                layer.setStyle({fillColor: getColorIntro(layer.feature.properties.intros[global_time + global_state_id])});
            }
        });
    }
    // update legend
    legend.update(global_state);
}
function changeScale() {
    var btn = document.getElementById("colorbtn");
    if (color_scale == "log") {
        color_scale = "raw";
        btn.innerText = "Show Log Fold Enrichment";
        colorIntros();
    } else {
        color_scale = "log";
        btn.innerText = "Show Raw Cluster Count";
        colorIntros();
    }
    initCTGrid(host, df, ds);
}

var legend = L.control({position: 'bottomleft'});

legend.onAdd = function (map) {
    this._div = L.DomUtil.create('div', 'info legend'); // create a div with a class "info lengend"
    this.update(global_state);
    return this._div;
};

function getBinVals(grades, max) {
    var threshold = 0;
    var bins = {start:[0, 0, 0, 0, 0, 0, 0, 0],stop:[0, 0, 0, 0, 0, 0, 0, 0]};
    for (var i = 0; i < grades.length; i++) {
        threshold = max * grades[i];
        if(((threshold%1)===0) && (threshold != 0)) {
            // integer not equal to zero
            bins.start[i] = threshold + 1;
        } else {
                bins.start[i] = Math.ceil(threshold);
        }
        if (i == 0) {
            bins.stop[i] = max;
        } else {
            bins.stop[i] = bins.start[i-1] - 1;
        }
    }
    return bins;
}
function getLegendBins(max) {
    var ltext = '';
    // cut points for creating color bins
    const grades = [0.9, 0.75, 0.5, 0.25, 0.1, 0.05, 0.01, 0];
    var threshold = 0;
    var bins = {start:[0, 0, 0, 0, 0, 0, 0, 0],stop:[0, 0, 0, 0, 0, 0, 0, 0]};
    for (var i = 0; i < grades.length; i++) {
        threshold = max * grades[i];
        if(((threshold%1)===0) && (threshold != 0)) {
            // integer not equal to zero
            bins.start[i] = threshold + 1;
        } else {
                bins.start[i] = Math.ceil(threshold);
        }
        if (i == 0) {
            bins.stop[i] = max;
        } else {
            bins.stop[i] = bins.start[i-1] - 1;
        }
    }
    // loop through the bin cut points and generate a label with a colored square for each interval
    for (var i = 0; i < grades.length; i++) {
        if (bins.start[i] <= bins.stop[i]) {
            ltext += '<i style="background:' + map_colors[i] + '"></i> '
            if (bins.start[i] == bins.stop[i]) {
                ltext += bins.stop[i]  + '<br>';
            } else {
                ltext += bins.start[i] + '&ndash;' + bins.stop[i] + '<br>';
            }
        }
    }
    return ltext;
}

// legend for US clusters
const legend_default = '<strong>Number of Clusters</strong><br>' +
        getLegendBins(max_basecount);
// legend for log fold enrichment
const legend_log = '<strong>Introductions</strong><br>'+
         '<small>Log<sub>10</sub>fold enrichment</small><br>' + 
         '<i style="background:#800026"></i>high<br>' +
         '<i style="background:#BD0026"></i><br>' +
         '<i style="background:#E31A1C"></i><br>' +
         '<i style="background:#FC4E2A"></i><br>' +
         '<i style="background:#FD8D3C"></i><br>' +
         '<i style="background:#FEB24C"></i><br>' +
         '<i style="background:#FED976"></i><br>' +
         '<i style="background:#FFEDA0"></i>low' +
         '<br><br><i style="background:#1a0080"></i>Focal Region';


// method to update the legend control based on feature properties passed
legend.update = function (props) {
    var ltext = '';
    if (props != "default") {
        if (color_scale == "raw") {
            //show number of clusters
            let maxn = maxClusterCt(global_state_id,global_time);
            ltext = '<strong>Number of<br>Introductions</strong><br>';
            ltext += getLegendBins(maxn);
            ltext += '<br><i style="background:#1a0080"></i>Focal Region';
        } else {
            //log fold enrichment
            ltext = legend_log;
        }
    } else {
        ltext = legend_default;
    }
    this._div.innerHTML = ltext;
}

function onEachFeature(feature, layer) {
    layer.on({
        mouseover: highlightFeature,
        mouseout: resetHighlight,
        click: changeView
    });
}

info.addTo(map);
legend.addTo(map);
