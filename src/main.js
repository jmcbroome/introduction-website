var map = L.map('mapid').setView([37.8, -96], 4);

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
    console.log(d)
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
    this._div.innerHTML = '<h4># Clusters in ' + (props ? '<b>' + props.name + '</b><br />' + props.intros.basecount : 'Hover over a state');
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
    geojson.resetStyle(e.target);
    info.update();
}

function zoomToFeature(e) {
    map.fitBounds(e.target.getBounds());
}

function changeView(e) {
    //code to change the displayed heatmaps to the matching intro index
    var clicklayer = e.target;
    //console.log(clicklayer.feature.id);
    //layer.setStyle({fillColor: getColor(layer.feature.properties.intros[layer.id])});
    geojson.eachLayer(function (layer, e = clicklayer) {
        //console.log(e.id)
        //console.log(layer.feature.properties.intros[e.id]);
        layer.setStyle({fillColor: getColorIntro(layer.feature.properties.intros[e.feature.id])})
    });
}

function onEachFeature(feature, layer) {
    layer.on({
        //mouseover: highlightFeature,
        //mouseout: resetHighlight,
        //click: zoomToFeature
        click: changeView
    });
}

info.addTo(map);

var legend = L.control({position: 'bottomright'});

legend.onAdd = function (map) {

    var div = L.DomUtil.create('div', 'info legend'),
        grades = [0, 10, 20, 50, 100, 200, 500, 1000],
        labels = [];

    // loop through our density intervals and generate a label with a colored square for each interval
    for (var i = 0; i < grades.length; i++) {
        div.innerHTML +=
            '<i style="background:' + getColorBase(grades[i] + 1) + '"></i> ' +
            grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + '<br>' : '+');
    }

    return div;
};

legend.addTo(map);