const initMaps = async () => {
    const containers = document.querySelectorAll("[id^='collection-map-']");

    for (const container of containers) {
        try {
            const mapId = container.id;
            const dataId = mapId.replace("collection-map-", "collection-map-data-");
            const pointsEl = document.getElementById(dataId);

            if (!pointsEl || !pointsEl.textContent.trim())
                continue;

            const points = JSON.parse(pointsEl.textContent);

            if (!points || !points.length)
                continue;

            if (typeof BalthubMaps === "undefined" || typeof BalthubMaps.render !== "function") {
                console.warn("[map] BalthubMaps not ready for", mapId);
                continue;
            }

            await BalthubMaps.render({
                container,
                points,
                zoom: parseInt(container.dataset.zoom || "8", 10),
            });
        } catch (err) {
            console.error("[map] failed to render", container.id, err);
        }
    }
};

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initMaps);
} else {
    initMaps();
}
