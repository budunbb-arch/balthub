/* /opt/balthub/static/assets/js/infinite-scroll.js  */

class InfiniteScroll {

    constructor() {

        this.loading = false;

        this.init();

    }

    init() {

        document.querySelectorAll("[data-ajax-list]")
            .forEach(wrapper => {

                this.observe(wrapper);

            });

    }

    observe(wrapper) {

        const pagination = wrapper.querySelector("[data-pagination]");

        if (!pagination) {
            return;
        }

        const observer = new IntersectionObserver(entries => {

            entries.forEach(entry => {

                if (!entry.isIntersecting) {
                    return;
                }

                this.loadNext(wrapper);

            });

        }, {
            rootMargin: "300px"
        });

        observer.observe(pagination);

    }

    async loadNext(wrapper) {

        if (this.loading) {
            return;
        }

        const nextLink = wrapper.querySelector("[data-next-page]");

        if (!nextLink) {
            return;
        }

        this.loading = true;

        const overlay = wrapper.querySelector(".ajax-loader-overlay");

        overlay?.classList.remove("hidden");

        try {

            const response = await fetch(nextLink.href, {
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            });

            const html = await response.text();

            const parser = new DOMParser();

            const doc = parser.parseFromString(html, "text/html");

            const selector = wrapper.dataset.container;

            const currentContainer = wrapper.querySelector(
                `${selector} [data-items]`
            );

            const newContainer = doc.querySelector("[data-items]");

            if (!currentContainer || !newContainer) {
                return;
            }

            // append cards
            Array.from(newContainer.children).forEach(node => {

                currentContainer.appendChild(node);

            });

            // replace pagination
            const oldPagination = wrapper.querySelector("[data-pagination]");
            const newPagination = doc.querySelector("[data-pagination]");

            if (oldPagination && newPagination) {
                oldPagination.replaceWith(newPagination);
                this.observe(wrapper);
            } else if (oldPagination) {
                oldPagination.remove();
            }

        } catch (e) {

            console.error("Infinite scroll error:", e);

        } finally {

            overlay?.classList.add("hidden");

            this.loading = false;

        }

    }

}

document.addEventListener("DOMContentLoaded", () => {

    new InfiniteScroll();

});