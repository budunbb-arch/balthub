/* /opt/balthub/static/assets/js/infinite-scroll.js */

class InfiniteScroll {

    constructor(wrapper) {

        this.wrapper = wrapper;

        this.loading = false;

        this.observer = null;

        this.observe();

        this.disabled = false;

    }

    observe() {

        const pagination = this.wrapper.querySelector("[data-pagination]");

        if (!pagination) {
            return;
        }

        // cleanup старого observer
        if (this.observer) {
            this.observer.disconnect();
        }

        this.observer = new IntersectionObserver(entries => {

            entries.forEach(entry => {

                if (!entry.isIntersecting) {
                    return;
                }

                this.loadNext();

            });

        }, {
            rootMargin: "300px"
        });

        this.observer.observe(pagination);

    }

    async loadNext() {

        if (this.loading || this.disabled) {
            return;
        }

        const pagination = this.wrapper.querySelector("[data-pagination]");

        if (!pagination) {
            return;
        }

        const nextLink = pagination.querySelector("[data-next-page]");

        if (!nextLink) {
            return;
        }

        this.loading = true;

        const overlay = this.wrapper.querySelector(".ajax-loader-overlay");

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

            const selector = this.wrapper.dataset.container;

            const currentContainer = this.wrapper.querySelector(
                `${selector} [data-items]`
            );

            const newContainer = doc.querySelector("[data-items]");

            if (!currentContainer || !newContainer) {
                return;
            }

            // append items
            Array.from(newContainer.children).forEach(node => {

                currentContainer.appendChild(node);

            });

            if (typeof initTooltips === "function") {
                initTooltips();
            }

            // replace pagination
            const oldPagination =
                this.wrapper.querySelector("[data-pagination]");

            const newPagination =
                doc.querySelector("[data-pagination]");

            if (oldPagination && newPagination) {

                oldPagination.replaceWith(newPagination);

                if (this.observer) {
                    this.observer.disconnect();
                }

                this.observe();

            } else if (oldPagination) {

                oldPagination.remove();

                if (this.observer) {
                    this.observer.disconnect();
                }
            }

        } catch (e) {

            console.error("Infinite scroll error:", e);

        } finally {

            overlay?.classList.add("hidden");

            this.loading = false;

        }

    }


    destroy() {

        if (this.observer) {
            this.observer.disconnect();
            this.observer = null;
        }

        this.loading = false;
    }

}