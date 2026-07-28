// /opt/balthub/static/assets/js/maps/house.js

document.addEventListener("DOMContentLoaded", async () => {

    const container = document.getElementById("house-map");

    if (!container)
        return;

    const points = JSON.parse(
        document.getElementById("house-map-data").textContent
    );

    await BalthubMaps.render({

        container,

        points,

        zoom: 16,

    });

});