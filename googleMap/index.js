function initMap() {
  const [latA, lngA] = [50.646993960909164, 3.0301131155001353];
  //const [latB, lngB] = [50.57243526433171, 3.1522652309582746];

  const map = new google.maps.Map(document.getElementById("map"), {
    zoom: 10,
    center: { lat: latA, lng: lngA },
    mapTypeId: "satellite",
    tilt: 0,
  });

  map.set("styles", [
    {
      featureType: "all",
      elementType: "labels",
      stylers: [{ visibility: "off" }],
    },
  ]);

  /*function drawMarker(pos) {
    new google.maps.Marker({
      position: { lat: pos[0], lng: pos[1] },
      map: map,
    });
  }*/

  function drawRectangle(rectangle) {
    const color = rectangle.color || "#FFFF00";
    const [lat0, lng0, lat1, lng1] = rectangle.data;
    new google.maps.Polyline({
      path: [
        { lat: lat0, lng: lng0 },
        { lat: lat0, lng: lng1 },
        { lat: lat1, lng: lng1 },
        { lat: lat1, lng: lng0 },
        { lat: lat0, lng: lng0 },
      ],
      geodesic: true,
      strokeColor: color,
    }).setMap(map);
  }

  if (DATA) Object.values(DATA).forEach((rect) => drawRectangle(rect));
}

window.initMap = initMap;
