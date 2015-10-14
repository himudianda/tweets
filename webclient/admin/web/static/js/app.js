function loc_search() {
    var lat = $('#lat_search').val();
    var lng = $('#lng_search').val();
    var radius = $('#radius_search').val();
    var searchString = $('#tweet_search').val();

    if (lat == "" || lng === "" || radius == "") {
      return;
    }

    if (searchString == "") {
      var data = JSON.stringify({lat:lat, lng:lng, radius:radius});
    } else {
      var data = JSON.stringify({lat:lat, lng:lng, radius:radius, hashtag:searchString});
    }

    $.ajax({
        url: '/tweets/api/v1.0/coordinates',
        type: 'post',
        contentType: "application/json; charset=utf-8",
        dataType: 'json',
        success: function (response) {
          // Show tweets on map
          myLayer.setGeoJSON(response.data);

          // List tweets
          var inBounds = [];
          index = 0
          myLayer.eachLayer(function(marker){
            index++;
            inBounds.push(index + ": " + marker.feature.properties.created_at + ' - ' + marker.options.title)
          });
          document.getElementById('coordinates').innerHTML = inBounds.join('\n');

          // Automatically adjust map bounds
          map.fitBounds(myLayer.getBounds());
        },
        data: data
    });
}