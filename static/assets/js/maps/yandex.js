// static/assets/js/maps/yandex.js

window.BalthubMaps = (function () {

    async function render(options) {

        await ymaps3.ready;

        const {
            YMap,
            YMapMarker,
            YMapDefaultSchemeLayer,
            YMapDefaultFeaturesLayer,
        } = ymaps3;

        const container = options.container;
        const points = options.points || [];

        if (!points.length)
            return;

        let center;

        if (points.length === 1) {

            center = [
                points[0].lon,
                points[0].lat,
            ];

        } else {

            const lon =
                points.reduce((s, p) => s + p.lon, 0) / points.length;

            const lat =
                points.reduce((s, p) => s + p.lat, 0) / points.length;

            center = [lon, lat];
        }

        const map = new YMap(container, {

            location: {

                center,

                zoom: options.zoom ?? 14,

            }

        });

        let schemeLayer = new YMapDefaultSchemeLayer();

        try {

            const styleResp = await fetch("/static/assets/js/maps/mapstylejson.json");

            if (styleResp.ok) {

                const style = await styleResp.json();

                schemeLayer = new YMapDefaultSchemeLayer({ customization: style });

            }

        } catch (err) {

            console.warn("[map] custom style load failed", err);

        }

        map.addChild(schemeLayer);
        map.addChild(new YMapDefaultFeaturesLayer());

        //--------------------------------------------------
        // маркеры
        //--------------------------------------------------

        for (const point of points) {

            const marker = document.createElement("div");

            marker.className = "house-marker";

            marker.title = point.title;

            if (point.url) {
                marker.onclick = () => {
                    location.href = point.url;
                };
            }

            map.addChild(

                new ymaps3.YMapMarker(
                    {
                        coordinates: [point.lon, point.lat],
                    },
                    marker
                )

            );
        }

        //--------------------------------------------------
        // TODO
        // если включена кластеризация
        // добавить кластерный слой
        //--------------------------------------------------

        return map;
    }

    return {

        render,

    };

})();