// == global variables ==
let grid; // variable for SlickGrid object
let dataView; // data manipulation variable for SlickGrid object
let data = []; //  variable to store data for grid
let basicDataLoaded = false; // basic cluster data are/not loaded into the grid
let sampleDataLoaded = false; // samples are/not loaded into the grid
// web worker script
const workerScript = `  
  importScripts("https://cdnjs.cloudflare.com/ajax/libs/pako/2.0.4/pako_inflate.min.js");
    self.onmessage = async (evt) => {
      const file = evt.data;
      const buf = await file.arrayBuffer();
      const decompressed = pako.inflate(buf);
      self.postMessage(decompressed, [decompressed.buffer]);
    };
  `;
let sortcol = ''; // column to sort on
let sortdir = 1; // default sort direction (ascending)
let searchString = ''; // string used to search and sort grid
let regionString = ''; // string to filter grid by region


// == functions for attaching data to grid ==
function blankSampleObj() {
  el = {
    'samples': '',
    'samplecol': '...loading data...',
  };
  return el;
}
function blankClusterObj() {
  el = {
    'cid': '...loading data...',
    'region': '...',
    'sampcount': '...',
    'earliest': '...',
    'latest': '...',
    'clade': '...',
    'lineage': '...',
    'origin': '...',
    'confidence': '...',
    'growth': '...',
    'taxlink': '...',
  };
  return el;
}
function getTaxoniumLink(host, cluster) {
  let link = '<a href="https://taxonium.org/?protoUrl=';
  link += host + 'cview.jsonl.gz';
  link += '&xType=x_dist&color=%7B%22field%22:%22meta_region%22%7D';
  link += '&srch=%5B%7B%22key%22:%22aa1%22,%22type%22:%22meta_cluster%22,%22method%22:%22text_exact%22,%22text%22:%22';
  link += cluster;
  link += '%22,%22gene%22:%22S%22,%22position%22:484,%22new_residue%22:%22any%22,%22min_tips%22:0,%22controls%22:true%7D%5D';
  link += '&zoomToSearch=0" target="_blank">View Cluster</a>';
  return link;
}
function clusterObjs(items, host) {
  el = {
    'cid': items[0],
    'region': items[1].replace(/_/g, ' '),
    'sampcount': items[2].toString(),
    'earliest': items[3],
    'latest': items[4],
    'clade': items[5],
    'lineage': items[6],
    'origin': items[7].replace(/_/g, ' '),
    'confidence': items[8].toString(),
    'growth': items[9].toString(),
    'taxlink': getTaxoniumLink(host, items[0]),
  };
  return el;
}
function sampleObjs(items) {
  // full values for searching
  const s = items[0];
  // truncated values for display
  let st = '';
  if (s !== '') {
    const n = s.length <= 50 ? s.length - 1 : 50;
    st = s.slice(0, n) + '...';
  }
  el = {
    'samples': s,
    'samplecol': st,
  };
  return el;
}
function initData(items, type, host = '') {
  const cl = items.length;
  data = Array(cl);
  if (type === 'clusters') {
    for (let i = 0; i < cl; i++) {
      const d = (data[i] = {});
      d.id = i;
      Object.assign(d, clusterObjs(items[i], host));
      Object.assign(d, blankSampleObj());
    }
  } else if (type === 'samples') {
    for (let i = 0; i < cl; i++) {
      const d = (data[i] = {});
      d.id = i;
      Object.assign(d, blankClusterObj());
      Object.assign(d, sampleObjs(items[i]));
    }
  }
}
function appendData(items, type, host = '') {
  const sl = items.length;
  if (type === 'samples') {
    for (let i = 0; i < sl; i++) {
      const newData = sampleObjs(items[i]);
      data[i].samples = newData.samples;
      data[i].samplecol = newData.samplecol;
    }
  } else if (type === 'clusters') {
    const newData = clusterObjs(items[i], host);
    data[i].cid = newData.cid;
    data[i].region = newData.region;
    data[i].sampcount = newData.sampcount;
    data[i].earliest = newData.earliest;
    data[i].latest = newData.latest;
    data[i].clade= newData.clade;
    data[i].lineage = newData.lineage;
    data[i].origin = newData.origin;
    data[i].confidence = newData.confidence;
    data[i].growth = newData.growth;
    data[i].taxlink = newData.taxlink;
  }
}
// function to load the data and wire functions to table
function loadData(dataArr, type, host = '') {
  if (type === 'clusters') {
    if (!sampleDataLoaded) {
      initData(dataArr, type, host);
    } else if (!basicDataLoaded) {
      // call update function
      appendData(dataArr, type, host);
      updateData();
    }
    basicDataLoaded = true;
  } else if (type === 'samples') {
    if (basicDataLoaded) {
      // call update function
      appendData(dataArr, type);
      updateData();
    } else {
      initData(dataArr, type);
    }
    sampleDataLoaded = true;
  }
  setGridView();
} // end of loadData function
async function loadBasicData(host, file) {
  const workerBlob = new Blob([workerScript], {type: 'application/javascript'});
  const workerUrl = URL.createObjectURL(workerBlob);

  const worker = new Worker(workerUrl);

  const compressedBlob1 = await fetch(host + file + '?v=' + new Date().getTime())
      .then((r) => r.blob());

  worker.onmessage = ({data}) => {
    const clusters = JSON.parse(new TextDecoder().decode(data));
    loadData(clusters, 'clusters', host);
  };
  worker.postMessage(compressedBlob1);
}

async function loadSampleData(host, file) {
  const workerBlob = new Blob([workerScript], {type: 'application/javascript'});
  const workerUrl = URL.createObjectURL(workerBlob);
  const worker = new Worker(workerUrl);

  const compressedBlob2 = await fetch(host + file + '?v=' + new Date().getTime())
      .then((r) => r.blob());

  worker.onmessage = ({data}) => {
    const samples = JSON.parse(new TextDecoder().decode(data));
    loadData(samples, 'samples');
  };
  worker.postMessage(compressedBlob2);
}

// == sets up Slick Grid object properties ==
// slickgrid grid options
function gridOpts() {
  const opt = {
    enableCellNavigation: true,
    forceFitColumns: false,
    multiColumnSort: true,
    enableColumnReorder: false,
  };
  return opt;
}
// sets the number of columns and their parameters
function setCols() {
  const cols = [
    {id: 'cid', name: `<span title='${tooltipText[0]}'>Cluster ID</span>`, field: 'cid', width: 160, sortable: true, sorter: sorterStringCompare, customTooltip: {useRegularTooltip: true}, formatter: tooltipFormatter},
    {id: 'region', name: `<span title='${tooltipText[1]}'>Region</span>`, field: 'region', width: 110, sortable: true, sorter: sorterStringCompare, customTooltip: {useRegularTooltip: true}, formatter: tooltipFormatter},
    {id: 'sampcount', name: `<span title='${tooltipText[2]}'>Sample Count</span>`, field: 'sampcount', width: 50, sortable: true, sorter: sorterNumeric, customTooltip: {useRegularTooltip: true}, formatter: tooltipFormatter},
    {id: 'earliest', name: `<span title='${tooltipText[3]}'>Earliest Date</span>`, field: 'earliest', width: 80, sortable: true, sorter: sorterStringCompare, customTooltip: {useRegularTooltip: true}, formatter: tooltipFormatter},
    {id: 'latest', name: `<span title='${tooltipText[4]}'>Latest Date</span>`, field: 'latest', width: 80, sortable: true, sorter: sorterStringCompare, customTooltip: {useRegularTooltip: true}, formatter: tooltipFormatter},
    {id: 'clade', name: `<span title='${tooltipText[5]}'>Clade</span>`, field: 'clade', width: 100, sortable: true, sorter: sorterStringCompare, customTooltip: {useRegularTooltip: true}, formatter: tooltipFormatter},
    {id: 'lineage', name: `<span title='${tooltipText[6]}'>Lineage</span>`, field: 'lineage', sortable: true, sorter: sorterStringCompare, customTooltip: {useRegularTooltip: true}, formatter: tooltipFormatter},
    {id: 'origin', name: `<span title='${tooltipText[7]}'>Best Potential Origins</span>`, field: 'origin', width: 110, sortable: true, sorter: sorterStringCompare, customTooltip: {useRegularTooltip: true}, formatter: tooltipFormatter},
    {id: 'confidence', name: `<span title='${tooltipText[8]}'>Best Origin Regional Indices</span>`, field: 'confidence', width: 70, sortable: true, sorter: sorterNumeric, customTooltip: {useRegularTooltip: true}, formatter: tooltipFormatter},
    {id: 'growth', name: `<span title='${tooltipText[9]}'>Growth Score</span>`, field: 'growth', width: 70, sortable: true, sorter: sorterNumeric, customTooltip: {useRegularTooltip: true}, formatter: tooltipFormatter},
    {id: 'taxlink', name: `<span title='${tooltipText[10]}'>View in Taxonium</span>`, field: 'taxlink', formatter: linkFormatter, sortable: true, sorter: sorterStringCompare},
    {id: 'samplecol', name: `<span title='${tooltipText[12]}'>Samples</span>`, field: 'samplecol', width: 300, sortable: true, sorter: sorterStringCompare, customTooltip: {useRegularTooltip: true}, formatter: tooltipFormatter},
  ];
  return cols;
}
// initalizes grid with blank data except for first row which shows "loading data"
function tempData() {
  const item = [{id: 'id_0'}];
  Object.assign(item[0], blankClusterObj());
  Object.assign(item[0], blankSampleObj());
  return item;
};

// == grid formatting functions ==

// function to add link formatting to cells
function linkFormatter(row, cell, value, columnDef, dataContext) {
  return value;
}
// function to add tool tip text
const tooltipText = [
  'The identifier of the internal node inferred to be the ancestral introduction. Can be used with the public protobuf and matUtils.',
  'Region of this cluster.',
  'Number of samples in this cluster.',
  'Date of the earliest sample from this cluster.',
  'Date of the latest sample from this cluster.',
  'Nextstrain clade of the ancestral introduction.',
  'Pangolin lineage of the ancestral introduction.',
  'The origin region with the greatest index value. May not be the true origin, especially if the corresponding index value is below 0.5.',
  'Regional index for the origin; 1 is maximal, 0 is minimal.',
  'Importance estimate based on cluster size and age. Not directly comparable between regions with varying sequencing levels.',
  'Click to View in Taxonium',
  'Double click cell to view all samples in this cluster',
];
function tooltipFormatter(row, cell, value, column, dataContext) {
  let val = '';
  if (value) {
    val = value;
  }

  // set tool tip text to same as header for most non-header cells
  const tttxt = tooltipText[cell];

  return `<span title='${tttxt}'>${val}</span>`;
}

// == grid filtering and sorting ==
// sets which data to search on
function searchFilter(item, args) {
  // show items if no region and no search string
  if (args.searchString === '' && args.regionString === '') {
    return true;
  }
  // filter out items not in the region
  if (args.regionString !== '' && item.region.indexOf(regionString) === -1) {
    return false;
  }
  // make search string case independent
  const sString = args.searchString.toLowerCase();
  // for text searching, fields in the table to search:
  const searchFields = item.cid.toLowerCase().indexOf(sString) === -1 &&
     item.region.toLowerCase().indexOf(sString) === -1 &&
     item.sampcount.toLowerCase().indexOf(sString) === -1 &&
     item.earliest.toLowerCase().indexOf(sString) === -1 &&
     item.latest.toLowerCase().indexOf(sString) === -1 &&
     item.clade.toLowerCase().indexOf(sString) === -1 &&
     item.lineage.toLowerCase().indexOf(sString) === -1 &&
     item.origin.toLowerCase().indexOf(sString) === -1 &&
     item.confidence.toLowerCase().indexOf(sString) === -1 &&
     item.growth.toLowerCase().indexOf(sString) === -1 &&
     item.taxlink.toLowerCase().indexOf(sString) === -1 &&
     item.samples.toLowerCase().indexOf(sString) === -1;
  // filter out items that don't match search criteria
  if (args.searchString !== '' && searchFields) {
    return false;
  }
  // passes all filters; show item
  return true;
}
function updateFilter() {
  dataView.setFilterArgs({
    regionString,
    searchString,
  });
  dataView.refresh();
}
// function to show/hide data by region
function showRegion(region) {
  if (region === 'default') {
    regionString = '';
  } else {
    regionString = region;
  }
  if (basicDataLoaded) {
    updateFilter();
  } else {
    console.log('basic data not loaded yet');
  }
}
// sort fucntion for strings
function sorterStringCompare(a, b) {
  const x = a[sortcol];
  const y = b[sortcol];
  return sortdir * (x === y ? 0 : (x > y ? 1 : -1));
}
// sort function for numeric data
function sorterNumeric(a, b) {
  const x = (isNaN(a[sortcol]) || a[sortcol] === '' || a[sortcol] === null) ? -99e+10 : parseFloat(a[sortcol]);
  const y = (isNaN(b[sortcol]) || b[sortcol] === '' || b[sortcol] === null) ? -99e+10 : parseFloat(b[sortcol]);
  return sortdir * (x === y ? 0 : (x > y ? 1 : -1));
}


// refreshes grid to show any new data added to data variable
function updateData() {
  dataView.beginUpdate();
  dataView.setItems(data);
  dataView.endUpdate();
  grid.setData(dataView);
  grid.render();
}

function setGridView() {
  // creates data and grid objects
  dataView = new Slick.Data.DataView({inlineFilters: true});
  grid = new Slick.Grid('#myGrid', dataView, setCols(), gridOpts());


  // adds pagination
  let pager = new Slick.Controls.Pager(dataView, grid, $('#pager'));
  // sets # of items to display by default
  dataView.setPagingOptions({pageSize: 20});

  // set column sort default column; put this before grid.onsort since the data is already sorted
  // grid.setSortColumn('growth', false); // columnId, descending sort order


  // adds sorting functionaility
  grid.onSort.subscribe(function(e, args) {
    const cols = args.sortCols;

    dataView.sort(function(dataRow1, dataRow2) {
      const cl = cols.length;
      for (let i = 0; i < cl; i++) {
        sortdir = cols[i].sortAsc ? 1 : -1;
        sortcol = cols[i].sortCol.field;

        const result = cols[i].sortCol.sorter(dataRow1, dataRow2);
        if (result !== 0) {
          return result;
        }
      }
      return 0;
    });
    args.grid.invalidateAllRows();
    args.grid.render();
  });

  // add ability to copy text
  grid.setSelectionModel(new Slick.CellSelectionModel());
  grid.registerPlugin(new Slick.CellExternalCopyManager({
    readOnlyMode: true,
    includeHeaderWhenCopying: false,
  }));

  // wire up model events to drive the grid
  // !! both dataView.onRowCountChanged and dataView.onRowsChanged MUST be wired to correctly update the grid
  // see Issue#91
  dataView.onRowCountChanged.subscribe(function(e, args) {
    grid.updateRowCount();
    grid.render();
  });
  dataView.onRowsChanged.subscribe(function(e, args) {
    grid.invalidateRows(args.rows);
    grid.render();
  });


  // set up double click event to trigger popup
  grid.onDblClick.subscribe((e, p) => {
    // p.row, p.cell
    if (p.cell === 11) {
      // get sample names from data
      txt = grid.getDataItem(p.row).samples;
      $('<div id="sample-popup"></div>').dialog({
        title: 'Samples',
        open: function() {
          txt = txt.replace(/,/g, ',<br/>');
          $(this).html(txt);
          $(this).dblclick(function() {
            $(this).dialog('close');
          });
        },
        close: function() {
          // deselect item
          grid.getSelectionModel().setSelectedRanges([]);
          grid.resetActiveCell();
        },
        height: 300,
      }); // end dialog
    }
  });

  // clear selected items on KeyDown of Esc key
  grid.onKeyDown.subscribe(function(e) {
    if (e.which === 27) {
      // deselect item
      grid.getSelectionModel().setSelectedRanges([]);
      grid.resetActiveCell();
    }
  });

  // wire up the search textbox to apply the filter to the model
  $('#txtSearch').keyup(function(e) {
    // clear on Esc
    if (e.which === 27) {
      this.value = '';
    }
    searchString = this.value;
    if (basicDataLoaded && sampleDataLoaded) {
      updateFilter();
    }
  });

  // initialize the model after all the events have been hooked up
  dataView.beginUpdate();
  dataView.setItems(data);
  dataView.setFilterArgs({
    regionString,
    searchString,
  });
  dataView.setFilter(searchFilter);
  dataView.endUpdate();
} // end of setGridView

// eslint-disable-next-line no-unused-vars
function initCTGrid(host, clusterfile, samplefile) {
  // clear everything
  basicDataLoaded = false;
  sampleDataLoaded = false;
  data = [];
  // sortcol = 'growth';
  sortdir = 1;
  searchString = '';
  regionString = '';
  document.getElementById('txtSearch').value = '';
  // create basic grid object while waiting for data to load
  grid = new Slick.Grid('#myGrid', tempData(), setCols(), gridOpts());

  loadBasicData(host, clusterfile);
  loadSampleData(host, samplefile);
}
