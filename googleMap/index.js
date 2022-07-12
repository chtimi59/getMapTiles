function initMap() {
  const [latA, lngA] = [50.646993960909164, 3.0301131155001353];
  const [latB, lngB] = [50.57243526433171, 3.1522652309582746];

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

  function drawMarker(pos) {
    new google.maps.Marker({
      position: { lat: pos[0], lng: pos[1] },
      map: map,
    });
  }

  function drawRectangle(layer, color = "#FFFF00") {
    const [lat0, lng0, lat1, lng1] = layer;
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

  // L12_21 (reference)
  // drawRectangle([latA, lngA, latB, lngB], '#ccc')

  // Centre de la Citadelle de Lille
  if (0) {
    drawMarker([50.64093730739812, 3.044522006061694]);
    Object.values({
      L9_: [
        50.79572456377767, 2.7847187532508935, 50.49774847919297,
        3.274055341236909,
      ],
      L10_2: [
        50.64699396090916, 3.030113115500135, 50.49774847919297,
        3.274055341236909,
      ],
      L11_21: [
        50.64699396090916, 3.030113115500135, 50.57243526433171,
        3.1522652309582746,
      ],
      L12_211: [
        50.64699396090916, 3.030113115500135, 50.60973066309945,
        3.091234488218945,
      ],
      L13_2111: [
        50.64699396090916, 3.030113115500135, 50.6283663295535,
        3.0606851386469756,
      ],
      L14_21111: [
        50.64699396090916, 3.030113115500135, 50.637681150235025,
        3.0454019622752355,
      ],
      L15_211112: [
        50.64233780690009, 3.0377582478136955, 50.63768115023503,
        3.045401962275234,
      ],
      L16_2111123: [
        50.64233658529331, 3.0415822093267284, 50.64000820208536,
        3.045404066362463,
      ],
      L17_21111232: [
        50.64117240939486, 3.0434931821506916, 50.64000820208536,
        3.0454040663624644,
      ],
      L18_211112323: [
        50.64117207088177, 3.044449150321467, 50.64058996379741,
        3.0454045924147426,
      ],
      L19_2111123231: [
        50.64117207088177, 3.044449150321467, 50.64088101832115,
        3.044926874137208,
      ],
      L20_21111232310: [
        50.64102663062482, 3.0444490215731954, 50.64088110455886,
        3.0446878834818487,
      ],
      L21_211112323100: [
        50.640953910484626, 3.044448957199339, 50.64088114750523,
        3.04456838815386,
      ],
    }).forEach((v) => drawRectangle(v));
  }

  // DATASET
  if (1) {
    drawRectangle(
      [
        50.63790367370581, 3.05828278697053, 50.63476396066108,
        3.0651009622863867,
      ],
      "#F00"
    );
    Object.values(DATA).forEach((v) => drawRectangle(v));
    Object.values(DATA1).forEach((v) => drawRectangle(v, "#00F"));
  }
}

window.initMap = initMap;
