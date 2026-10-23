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

        let center;

        if (points.length === 1) {

            center = [
                points[0].lon,
                points[0].lat,
            ];

        } else if (points.length > 1) {

            const lon =
                points.reduce((s, p) => s + p.lon, 0) / points.length;

            const lat =
                points.reduce((s, p) => s + p.lat, 0) / points.length;

            center = [lon, lat];
        } else {
            center = options.center || [20.5, 54.7];
        }

        const map = new YMap(container, {

            location: {

                center,

                zoom: options.zoom ?? (points.length ? 14 : 8),

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

        let openMarker = null;

        for (const point of points) {

            const marker = document.createElement("div");

            marker.className = "house-marker";

            const markerOptions = {
                coordinates: [point.lon, point.lat],
            };

            if (options.markerDetails) {
                markerOptions.zIndex = 0;
            }

            const mapMarker = new ymaps3.YMapMarker(markerOptions, marker);

            if (options.markerDetails) {
                marker.setAttribute("role", "button");
                marker.setAttribute("tabindex", "0");
                const projectName = point.project ? `«${point.project}»` : "";
                marker.setAttribute(
                    "aria-label",
                    [point.city, point.project_type_alias, projectName, point.corpus || point.address]
                        .filter(Boolean)
                        .join(", ")
                );
                marker.setAttribute("aria-expanded", "false");

                const details = document.createElement("div");
                details.className = "house-marker-details";
                details.hidden = true;
                details.addEventListener("click", event => event.stopPropagation());

                const city = document.createElement("div");
                city.className = "house-marker-city";
                city.textContent = point.city || "";

                const project = document.createElement("div");
                project.className = "house-marker-project";
                project.textContent = [point.project_type_alias, projectName]
                    .filter(Boolean)
                    .join(" ");

                const house = document.createElement("div");
                house.className = "house-marker-address";
                house.textContent = point.corpus || point.address || "";

                details.append(city, project, house);

                if (point.url) {
                    const link = document.createElement("a");
                    link.className = "house-marker-open-link";
                    link.href = point.url;
                    link.textContent = "Открыть";
                    details.append(link);
                }

                marker.append(details);

                const toggleDetails = () => {
                    if (openMarker && openMarker.element !== marker) {
                        openMarker.element.classList.remove("is-open");
                        openMarker.element.setAttribute("aria-expanded", "false");
                        openMarker.details.hidden = true;
                        openMarker.mapMarker.update({ zIndex: 0 });
                    }

                    const isOpen = marker.classList.toggle("is-open");
                    details.hidden = !isOpen;
                    marker.setAttribute("aria-expanded", String(isOpen));

                    if (isOpen) {
                        mapMarker.update({ zIndex: 1000 });
                        openMarker = { element: marker, details, mapMarker };
                    } else {
                        mapMarker.update({ zIndex: 0 });
                        openMarker = null;
                    }
                };

                marker.addEventListener("click", toggleDetails);
                marker.addEventListener("keydown", event => {
                    if (event.target !== marker) {
                        return;
                    }

                    if (event.key === "Enter" || event.key === " ") {
                        event.preventDefault();
                        toggleDetails();
                    }
                });
            } else if (point.url) {
                marker.title = point.title || point.address || point.project || "";
                marker.addEventListener("click", () => {
                    location.href = point.url;
                });
            }

            map.addChild(mapMarker);
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