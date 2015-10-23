var  MarkersArr = [];
var pinData = [];

$(document).ready(function(){  
  $("#dateRangeSlider").bind("valuesChanged", function(e, data){
    var minDate = new Date(data.values.min);
    var maxDate = new Date(data.values.max);

    var month = maxDate.getMonth() +1;
    if(month < 10) {
      month = "0"+ month;
    }
    var day = maxDate.getDate();
    if(day < 10) {
      day = "0" + day;
    }
    var minFormat = month + "/" + day + "/" + minDate.getFullYear();
    var maxFormat = month +"/" + day + "/" + maxDate.getFullYear();
    
    deleteMarkers();

     //alert(minFormat + " : " + maxFormat);
     // alert(JSON.stringify(pinData));
    // alert(JSON.stringify(pinData[minFormat]));

    var markerData = pinData[maxFormat];

    if(markerData!= null && markerData.length > 0) {
        for(marker in markerData) {                  
          latitude = markerData[marker]["lat"]              
          longitude = markerData[marker]["long"]
          title = markerData[marker]["count"]          
          addMarkers(latitude, longitude, title.toString());             
        }  
      }
  });

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
        var nextDate = new Date(startDate);
        nextDate.setDate(nextDate.getDate() + 1);

		    $("#dateRangeSlider").dateRangeSlider(
            "bounds", new Date(startDate), new Date(endDate));

          $("#dateRangeSlider").dateRangeSlider(          
            "values", new Date(startDate), nextDate);
                      
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
      pinData = data["data"];
			keys = Object.keys(data["data"]);
      var firstData = false;

			for(key in keys) {
				markerData = data["data"][keys[key]]
        if(markerData.length > 0) {
          for(marker in markerData) {                  
            latitude = markerData[marker]["lat"]              
            longitude = markerData[marker]["long"]
            title = markerData[marker]["count"]          
            addMarkers(latitude, longitude, title.toString()); 
            if(title != null) {
                firstData = true
            }
          }  
        }
        if(firstData == true) {
          break;
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