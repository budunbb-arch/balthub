/* /opt/balthub/static/assets/js/house-plans.js */

document.addEventListener("DOMContentLoaded", () => {

    const toggles = document.querySelectorAll(".rooms-toggle");

    // =====================================================
    // LOAD GROUP
    // =====================================================

    async function loadGroup(toggle) {

        const rooms = toggle.dataset.rooms || null;

        const content = document.querySelector(
            `#rooms-content-${rooms}`
        );

        if (content.dataset.loaded) {
            return;
        }

        const wrapper = content.querySelector(
            ".plans-wrapper"
        );

        const container = wrapper.querySelector(
            ".plans-container-wrapper"
        );

        const url = rooms
            ? `${content.dataset.plansUrl}?rooms=${rooms}&page=1`
            : `${content.dataset.plansUrl}?page=1`;

        const response = await fetch(url, {
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        });

        const html = await response.text();

        container.innerHTML = html;

        content.dataset.loaded = "1";

        if (!wrapper._infiniteScroll) {

            wrapper._infiniteScroll =
                new InfiniteScroll(wrapper);

        }
    }

    // =====================================================
    // OPEN GROUP
    // =====================================================

    async function openGroup(toggle, shouldScroll = false) {

        const rooms = toggle.dataset.rooms;

        const currentContent = document.querySelector(
            `#rooms-content-${rooms}`
        );

        if (!currentContent) {
            return;
        }

        const alreadyOpen = currentContent.classList.contains("open");

        document.querySelectorAll(".rooms-content").forEach(el => {
            el.classList.remove("open");
        });

        document.querySelectorAll(".rooms-toggle").forEach(btn => {
            btn.classList.remove("is-open");
        });

        if (alreadyOpen) {
            return;
        }

        currentContent.classList.add("open");

        toggle.classList.add("is-open");

        await loadGroup(toggle);
        
        if (shouldScroll) {
            setTimeout(() => {
                toggle.scrollIntoView({ behavior: "smooth", block: "start" });
            }, 150);
        }
    }

    // =====================================================
    // CLICK EVENTS
    // =====================================================

    toggles.forEach(toggle => {

        toggle.addEventListener("click", async () => {

            await openGroup(toggle, true);

        });

    });

    // =====================================================
    // AUTO OPEN FIRST GROUP
    // =====================================================

    document.querySelectorAll(".rooms-content.open").forEach(el => {
        el.classList.remove("open");
    });

    document.querySelectorAll(".rooms-toggle.is-open").forEach(btn => {
        btn.classList.remove("is-open");
    });

    if (toggles.length) {

        openGroup(toggles[0], false);

    }

});