const initProjectMap = async () => {

    const container = document.querySelector("[id^='collection-map-project']");

    if (!container)
        return;

    const dataId = container.id.replace("collection-map-", "collection-map-data-");

    const pointsEl = document.getElementById(dataId);

    if (!pointsEl)
        return;

    const points = JSON.parse(pointsEl.textContent);

    if (!points || !points.length)
        return;

    if (typeof BalthubMaps === "undefined" || typeof BalthubMaps.render !== "function") {
        console.warn("[map] BalthubMaps not ready for", container.id);
        return;
    }

    await BalthubMaps.render({

        container,

        points,

        zoom: parseInt(container.dataset.zoom || "14", 10),

    });

};

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initProjectMap);
} else {
    initProjectMap();
}
