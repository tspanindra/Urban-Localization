var  MarkersArr = [];

$(document).ready(function(){  
	$('#dateRangeSlider').dateRangeSlider({
      bounds:{
            min: new Date(2013, 0, 1),
            max: new Date(2018, 11, 31)
          },
      
      defaultValues:{
            min: new Date(2013, 0, 1),
            max: new Date(2018, 11, 31)
          },
      step:{
            days : 1
      }
    });

   $('#eventStartDate').datepicker({
        format: "mm/dd/yyyy",
        autoclose: true
    });  

   $('#eventEndDate').datepicker({
        format: "mm/dd/yyyy",
        autoclose: true
    });  

  initMap();
    $('#eventDate').datepicker({
        format: "dd/mm/yyyy"
    });  
       
    $('#submitBtn').click( function(){
       var startDatePicker = $('#eventStartDate');
        var startDate = startDatePicker.val();
        console.log("Event start date = " + startDate);

        var endDatePicker = $('#eventEndDate');
        var endDate = endDatePicker.val();

	      var tagsTxtBox = $('#tagsTxtBox');
	      console.log("tags = " + tagsTxtBox.val());
	      var tag = tagsTxtBox.val();
	      $.post( "http://instalocalize.com:5000/getData", { "tag": tag})
		  	  .done(function( data ) {
		      //findEvents();
		      findEvents();
		  });	

		    $("#dateRangeSlider").dateRangeSlider(
            "bounds", new Date(startDate), new Date(endDate));

          $("#dateRangeSlider").dateRangeSlider(
            "values", new Date(startDate), new Date(endDate));
                      
    });        
});

///To get a cluster information and to show pins on the Map.
function findEvents() {
	 var tagsTxtBox = $('#tagsTxtBox');
	 var tag = tagsTxtBox.val() + ".txt"
	 var fromDatePicker = $('#eventStartDate');
	 var toDatePicker = $('#eventEndDate');
	
	$.ajax({
		type: "POST",
		url: "http://instalocalize.com:5000/find_events",
		data: { "filename": tag, "fromdate" : fromDatePicker.val(), "todate" : toDatePicker.val()},
	 	dataType: "json",
		success: function( data ) {		
    alert(JSON.stringify(data));	
			keys = Object.keys(data["data"])		
			for(key in keys) {
				markerData = data["data"][keys[key]]
				for(marker in markerData) {
					latitude = markerData[marker]["lat"]
					longitude = markerData[marker]["long"]
					title = markerData[marker]["count"]					
					addMarkers(latitude, longitude, title.toString());
			
				}				
			}
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

function addMarkers(latitude, longitude, title) {
	var marker = new google.maps.Marker({
    	position: new google.maps.LatLng(latitude, longitude),
      	map: map,
      	title: title,
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