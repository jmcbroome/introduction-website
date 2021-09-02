var map = L.map('mapid', {'tap':false}).setView([37.8, -96], 4);
var global_state = "default";
var global_state_id = "00";
// var host = "raw.githubusercontent.com/jmcbroome/introduction-website/main/"


// Map values from geoJSON to a color 
function getColorBase(d) {
    return d > 10000 ? '#800026' :
           d > 5000  ? '#BD0026' :
           d > 1000  ? '#E31A1C' :
           d > 500  ? '#FC4E2A' :
           d > 200   ? '#FD8D3C' :
           d > 100   ? '#FEB24C' :
           d > 50   ? '#FED976' :
                      '#FFEDA0';
}

function getColorIntro(d) {
    return d > 1 ? '#800026' :
        d > 0.75  ? '#BD0026' :
        d > 0.5  ? '#E31A1C' :
        d > 0.25  ? '#FC4E2A' :
        d > 0   ? '#FD8D3C' :
        d > -0.25   ? '#FEB24C' :
        d > -0.5   ? '#FED976' :
                    '#FFEDA0';
}

function style(feature) {
    return {
        fillColor: getColorBase(feature.properties.intros.basecount),
        weight: 2,
        opacity: 1,
        color: 'white',
        dashArray: '3',
        fillOpacity: 0.7
    };
}

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png?{foo}', {foo: 'bar', attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'}).addTo(map);
// L.geoJson(statesData).addTo(map);
// geoJson = L.geoJson(statesData, {style: style}).addTo(map);

var geojson;
geojson = L.geoJson(introStatesData, {
    style: style,
    onEachFeature: onEachFeature
}).addTo(map);

var info = L.control();

info.onAdd = function (map) {
    this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
    this.update();
    return this._div;
};

// method that we will use to update the control based on feature properties passed
info.update = function (props) {
    // this._div.innerHTML = '<h4>US Population Density</h4>' +  (props ?
    //     '<b>' + props.name + '</b><br />' + props.density + ' people / mi<sup>2</sup>'
    //     : 'Hover over a state');
    if (global_state == "default") {
        this._div.innerHTML = '<h4># Clusters in ' + (props ? '<b>' + props.name + '</b><br />' + props.intros.basecount : 'Hover over a state');
    } else {
        this._div.innerHTML = '<h4># Introductions to ' + global_state + ' from ' + (props ? '<b>' + props.name + '</b><br />' + props.intros["raw" + global_state_id] : 'Hover over a state');
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

function loadTargetTable(target) {
    CsvToHtmlTable.init({
        csv_path: target, 
        element: 'table-container', 
        allow_download: false,
        csv_options: {separator: '\t', delimiter: '\t'},
        datatables_options: {"paging": true, "searching": true, "order": [[8,"desc"]]},
        custom_formatting: [
            [9, function (data,type,row,meta) {
                return '<a href="' + encodeURI(data) + '" title="Click to View in Taxodium" target="_blank">View Cluster</a>';
              }
            ],[8, function (data,type,row,meta) {
                return '<div title="Importance estimate based on cluster size and age.">' + data + "</div>"
              }
            ],[7, function (data,type,row,meta) {
                return '<div title="Confidence metric for origin; 1 is maximal, 0 is minimum.">' + data + "</div>"
              }
            ],[6, function (data,type,row,meta) {
                return '<div title="The origin region with the greatest weight. May not be true origin.">' + data + "</div>"
              }
            ],[5, function (data,type,row,meta) {
                return '<div title="Pangolin lineage and nextstrain clade of the ancestral introduction.">' + data + "</div>"
              }
            ],[4, function (data,type,row,meta) {
                return '<div title="Date of the latest sample from this cluster.">' + data + "</div>"
              }
            ],[3, function (data,type,row,meta) {
                return '<div title="Date of the earliest sample from this cluster.">' + data + "</div>"
              }
            ],[2, function (data,type,row,meta) {
                return '<div title="Number of samples in this cluster.">' + data + "</div>"
              }
            ],[1, function (data,type,row,meta) {
                return '<div title="Region of this cluster.">' + data + "</div>"
              }
            ],[0, function (data,type,row,meta) {
                return '<div title="The identifier of the internal node inferred to be the ancestral introduction. Can be used with the public protobuf and matUtils.">' + data + "</div>"
              }
            ]
        ]
      });
}

function resetView(e) {
    geojson.eachLayer(function (layer) {
        geojson.resetStyle(layer);
    });
    loadTargetTable('data/display_tables/default_clusters.tsv');
}

function loadStateTable(e) {
    let path = "data/display_tables/" + e.target.feature.properties.name + "_topclusters.tsv";
    loadTargetTable(path);
}

function zoomToFeature(e) {
    map.fitBounds(e.target.getBounds());
}

function changeView(e) {
    //code to change the displayed heatmaps to the matching intro index
    var clicklayer = e.target;
    if (e.target.options.fillColor == "#1a0080") {
        resetView(e);
        global_state = "default";
        global_state_id = "00";
    } else {
        loadStateTable(e);
        global_state = e.target.feature.properties.name;
        global_state_id = e.target.feature.id;
        clicklayer.setStyle({fillColor: "#1a0080"});
        geojson.eachLayer(function (layer, e = clicklayer) {
            if (e.feature.id != layer.feature.id) {
                layer.setStyle({fillColor: getColorIntro(layer.feature.properties.intros[e.feature.id])})
            }
        });
    }
}

function onEachFeature(feature, layer) {
    layer.on({
        mouseover: highlightFeature,
        mouseout: resetHighlight,
        click: changeView
    });
}

info.addTo(map);

// var legend = L.control({position: 'bottomright'});

// legend.onAdd = function (map) {

//     var div = L.DomUtil.create('div', 'info legend'),
//         grades = [0, 10, 20, 50, 100, 200, 500, 1000],
//         labels = [];

//     // loop through our density intervals and generate a label with a colored square for each interval
//     for (var i = 0; i < grades.length; i++) {
//         div.innerHTML +=
//             '<i style="background:' + getColorBase(grades[i] + 1) + '"></i> ' +
//             grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + '<br>' : '+');
//     }

//     return div;
// };

// legend.addTo(map);