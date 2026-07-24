(async () => {

    if (!window.ymaps3)
        return;

    await ymaps3.ready;

    const {
        YMap,
        YMapDefaultSchemeLayer,
        YMapDefaultFeaturesLayer,
        YMapMarker
    } = ymaps3;

    document.querySelectorAll(".ymap").forEach(container => {

        const lat = Number(container.dataset.lat);
        const lon = Number(container.dataset.lon);

        const map = new YMap(
            container,
            {
                location: {
                    center: [lon, lat],
                    zoom: 16
                }
            }
        );

        map.addChild(new YMapDefaultSchemeLayer());
        map.addChild(new YMapDefaultFeaturesLayer());

        const marker = document.createElement("div");
        marker.className = "ymap-marker";

        map.addChild(
            new YMapMarker(
                {
                    coordinates: [lon, lat]
                },
                marker
            )
        );

    });

})();