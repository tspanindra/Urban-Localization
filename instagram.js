var  MarkersArr = [];

$(document).ready(function(){
  //getData();
  initMap();
    $('#eventDate').datepicker({
        format: "dd/mm/yyyy"
    });  
       
    $('#submitBtn').click( function(){
	      var tagsTxtBox = $('#tagsTxtBox');
	      console.log("tags = " + tagsTxtBox.val());
	      var tag = tagsTxtBox.val();
	      $.post( "http://instalocalize.com:5000/getData", { "tag": tag})
		  	  .done(function( data ) {
		      alert( "Data Loaded: " + data );
		      //findEvents();
		  });	
    });        
});

///To get a cluster information and to show pins on the Map.
function findEvents() {
	 var tagsTxtBox = $('#tagsTxtBox');
	 var fromDatePicker = $('#fromDate');
	 var toDatePicker = $('#toDate');

	$.ajax({
		type: "POST",
		url: "http://instalocalize.com:5000/find_events",
		data: { "filename": tagsTxtBox.val(), "fromdate" : fromDatePicker.val(), "todate" : toDatePicker.val()},
	 	dataType: "json",
		success: function( data ) {

	  	}		  
	});	
}

///Map related functions.
var map;
function initMap() {
  map = new google.maps.Map(document.getElementById('map'), {
    center: {lat:  20.50505, lng: -8.49090},
    zoom: 2
  });
}

function addMarkers() {
	var marker = new google.maps.Marker({
    	position: StartPosition,
      	map: map,
      	title: "Drag Me",
      	draggable: true
  	});

	MarkersArr.push(marker);
}

function deleteMarkers() {
  for (var i = 0; i < MarkersArr.length; i++) {
    MarkersArr[i].setMap(null);
  }

  MarkersArr = [];
}