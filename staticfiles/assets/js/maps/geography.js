const initGeographyMap = async () => {
    const container = document.getElementById("geography-map");
    const pointsElement = document.getElementById("geography-map-points");

    if (!container || !pointsElement) {
        return;
    }

    if (typeof ymaps3 === "undefined" || typeof BalthubMaps === "undefined") {
        console.error("[map] Yandex Maps API is unavailable");
        return;
    }

    try {
        await ymaps3.ready;

        const points = JSON.parse(pointsElement.textContent).map(point => ({
            lon: point.lon,
            lat: point.lat,
            title: point.title,
            url: point.url,
            city: point.city,
            project_type_alias: point.project_type_alias,
            project: point.project,
            corpus: point.corpus,
            address: point.address,
        }));

        await BalthubMaps.render({
            container,
            points,
            markerDetails: true,
            center: [20.5, 54.7],
            zoom: Number.parseInt(container.dataset.zoom || "8", 10),
        });
    } catch (error) {
        console.error("[map] Failed to render geography map", error);
    }
};

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initGeographyMap);
} else {
    initGeographyMap();
}
