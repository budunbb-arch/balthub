document.addEventListener("DOMContentLoaded", async () => {

    console.log("DOM ready");

    const el = document.getElementById("house-map");

    console.log(el);

    if (!el)
        return;

    console.log("waiting ymaps");

    await ymaps3.ready;

    console.log("ymaps ready");

    console.log(ymaps3);

    const {
        YMap,
        YMapDefaultSchemeLayer,
        YMapDefaultFeaturesLayer,
        YMapMarker
    } = ymaps3;

    console.log(
        YMap,
        YMapDefaultSchemeLayer,
        YMapDefaultFeaturesLayer,
        YMapMarker
    );

    const lat = Number(el.dataset.lat);
    const lon = Number(el.dataset.lon);

    console.log(lat, lon);

    const map = new YMap(el, {
        location: {
            center: [lon, lat],
            zoom: 16
        }
    });

    console.log(map);

    map.addChild(new YMapDefaultSchemeLayer());
    map.addChild(new YMapDefaultFeaturesLayer());

    const marker = document.createElement("div");
    marker.style.width = "20px";
    marker.style.height = "20px";
    marker.style.background = "red";
    marker.style.borderRadius = "50%";

    map.addChild(
        new YMapMarker(
            {
                coordinates: [lon, lat]
            },
            marker
        )
    );

    console.log("done");
});