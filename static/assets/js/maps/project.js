document.addEventListener("DOMContentLoaded", async () => {

    const container = document.getElementById("collection-map");

    if (!container)
        return;

    const points = JSON.parse(
        document.getElementById("collection-map-data").textContent
    );

    await BalthubMaps.render({

        container,
        points,

        zoom: 14,

    });

});