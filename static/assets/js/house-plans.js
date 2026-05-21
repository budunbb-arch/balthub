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

        new InfiniteScroll(wrapper);
    }

    // =====================================================
    // OPEN GROUP
    // =====================================================

    async function openGroup(toggle) {

        const rooms = toggle.dataset.rooms;

        const currentContent = document.querySelector(
            `#rooms-content-${rooms}`
        );

        const alreadyOpen =
            currentContent.classList.contains("open");

        // закрываем остальные
        document.querySelectorAll(".rooms-content")
            .forEach(el => {

                if (el !== currentContent) {

                    el.classList.remove("open");

                }

            });

        // toggle текущего
        if (alreadyOpen) {

            currentContent.classList.remove("open");

            return;
        }

        currentContent.classList.add("open");

        await loadGroup(toggle);
    }

    // =====================================================
    // CLICK EVENTS
    // =====================================================

    toggles.forEach(toggle => {

        toggle.addEventListener("click", async () => {

            await openGroup(toggle);

        });

    });

    // =====================================================
    // AUTO OPEN FIRST GROUP
    // =====================================================

    if (toggles.length) {

        openGroup(toggles[0]);

    }

});