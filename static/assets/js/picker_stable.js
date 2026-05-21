/* /opt/balthub/static/assets/js/picker_stable.js */

document.addEventListener("DOMContentLoaded", () => {

    initPickers();

});

class PickerSystem {

    constructor(root) {

        this.root = root;

        this.state = this.parseURL();

        this.bindUI();
        this.renderFromState();
    }

    // =====================================================
    // URL → STATE
    // =====================================================

    parseURL() {

        const params = new URLSearchParams(window.location.search);

        const state = {};

        for (const [key, value] of params.entries()) {

            if (!state[key]) state[key] = [];

            state[key].push(value);
        }

        return state;
    }

    // =====================================================
    // STATE → URL
    // =====================================================

    syncURL() {

        const params = new URLSearchParams();

        for (const key in this.state) {

            this.state[key].forEach(v => {
                params.append(key, v);
            });
        }

        params.delete("page");

        const url = params.toString()
            ? `${location.pathname}?${params}`
            : location.pathname;

        history.pushState({}, "", url);

        this.reload(url);
    }

    // =====================================================
    // UI BINDING
    // =====================================================

    bindUI() {

        // toggle dropdown
        this.root.querySelectorAll(".picker-trigger")
            .forEach(btn => {

                btn.addEventListener("click", (e) => {

                    e.stopPropagation();

                    const picker = btn.closest(".picker");

                    const isOpen = picker.classList.contains("open");

                    // закрываем все
                    document.querySelectorAll(".picker.open")
                        .forEach(p => {
                            p.classList.remove("open");
                        });

                    // если текущий был закрыт — открываем
                    if (!isOpen) {
                        picker.classList.add("open");
                    }

                });

            });

        // select values
        this.root.querySelectorAll("[data-picker-value]").forEach(input => {

            input.addEventListener("change", (e) => {

                const picker = e.target.closest(".picker");
                const name = picker.dataset.pickerName;
                const type = e.target.type;
                const value = e.target.value;

                // =====================================================
                // RADIO (single value)
                // =====================================================

                if (type === "radio") {

                    this.state[name] = [value];   // всегда массив из 1
                    this.syncURL(); 

                    picker.querySelectorAll('input[type="radio"]').forEach(r => {
                        r.checked = (r.value === value);
                    });

                    return;

                }

                // =====================================================
                // CHECKBOX (multi value)
                // =====================================================

                else {

                    if (!this.state[name]) {
                        this.state[name] = [];
                    }

                    if (e.target.checked) {
                        if (!this.state[name].includes(value)) {
                            this.state[name].push(value);
                        }
                    } else {
                        this.state[name] =
                            this.state[name].filter(v => v !== value);
                    }
                }
            });

        });

        // range inputs
        this.root.querySelectorAll("[data-picker-range]")
            .forEach(input => {

                input.addEventListener("input", (e) => {

                    const name = e.target.dataset.pickerRange;

                    const value = e.target.value.trim();

                    if (value) {

                        this.state[name] = [value];

                    } else {

                        delete this.state[name];

                    }

                    // =========================================
                    // AUTO SUBMIT
                    // =========================================

                    const picker = e.target.closest(".picker");

                    if (picker.dataset.autoSubmit === "true") {

                        clearTimeout(this.rangeTimer);

                        this.rangeTimer = setTimeout(() => {
                            this.syncURL();
                        }, 500);
                    }

                });

            });

        // apply button
        this.root.querySelectorAll(".picker-apply")
            .forEach(btn => {

                btn.addEventListener("click", () => {
                    this.syncURL();
                    btn.closest(".picker").classList.remove("open");
                });

            });

        this.root.querySelectorAll("[data-picker-reset]")
            .forEach(btn => {

                btn.addEventListener("click", (e) => {

                    e.stopPropagation();

                    const picker = btn.closest(".picker");
                    const name = picker.dataset.pickerName;

                    // =====================================================
                    // NORMAL STATE CLEAN
                    // =====================================================

                    const rangeInputs = picker.querySelectorAll("[data-picker-range]");

                    if (rangeInputs.length) {

                        rangeInputs.forEach(input => {

                            const key = input.dataset.pickerRange;

                            delete this.state[key];

                            input.value = "";
                        });

                    } else {

                        delete this.state[name];

                        picker.querySelectorAll("[data-picker-value]").forEach(input => {
                            input.checked = false;
                        });
                    }

                    this.syncURL();
                });

            });


        // reset all
        document.querySelectorAll("[data-picker-reset-all]")
            .forEach(btn => {

                btn.addEventListener("click", () => {

                    this.state = {};

                    this.root.querySelectorAll("[data-picker-value], [data-picker-range]")
                        .forEach(input => {
                            input.checked = false;
                        });

                    this.syncURL();

                });

            });            
    }

    // =====================================================
    // STATE → UI
    // =====================================================

    renderFromState() {

        const keys = new Set(Object.keys(this.state));

        // добавляем виртуальный ключ для range
        this.root.querySelectorAll(".picker").forEach(picker => {

            const inputs = picker.querySelectorAll("[data-picker-range]");

            if (!inputs.length) return;

            const fromKey = inputs[0]?.dataset.pickerRange;
            const toKey = inputs[1]?.dataset.pickerRange;

            if (
                this.state[fromKey]?.[0]
                || this.state[toKey]?.[0]
            ) {
                keys.add(picker.dataset.pickerName);
            }
        });

        for (const key of keys) {

            const picker = this.root.querySelector(
                `[data-picker-name="${key}"]`
            );

            if (!picker) continue;

            const isRange = picker.querySelector("[data-picker-range]");
            const trigger = picker.querySelector(".picker-trigger");

            let values = [];
            let hasValue = false;

            // =====================================================
            // RANGE PICKER (price)
            // =====================================================

            if (isRange) {

                const inputs = picker.querySelectorAll("[data-picker-range]");

                const fromKey = inputs[0]?.dataset.pickerRange;
                const toKey = inputs[1]?.dataset.pickerRange;

                const from = this.state[fromKey]?.[0];
                const to = this.state[toKey]?.[0];

                hasValue = Boolean(from || to);

                picker.classList.toggle("has-value", hasValue);

                if (trigger) {

                    if (hasValue) {

                        trigger.textContent =
                            `${from || "0"} — ${to || "∞"}`;

                    } else {

                        trigger.textContent =
                            trigger.dataset.placeholder || "Цена";
                    }
                }

                continue;
            }

            // =====================================================
            // NORMAL PICKERS
            // =====================================================

            values = this.state[key] || [];
            hasValue = values.length > 0;

            picker.classList.toggle("has-value", hasValue);

            picker.querySelectorAll("[data-picker-value]").forEach(input => {

                if (input.type === "radio") {
                    input.checked = input.value === values[0];
                } else {
                    input.checked = values.includes(input.value);
                }
            });

            if (!trigger) continue;

            const checkedLabels = [...picker.querySelectorAll("[data-picker-value]")]
                .filter(i => i.checked)
                .map(i => i.parentElement.textContent.trim());

            if (checkedLabels.length === 0) {

                trigger.textContent =
                    trigger.dataset.placeholder || "Выбрать";

            } else if (checkedLabels.length === 1) {

                trigger.textContent = checkedLabels[0];

            } else {

                trigger.textContent =
                    `${checkedLabels[0]} + ${checkedLabels.length - 1}`;
            }
        }
    }

    // =====================================================
    // AJAX reload
    // =====================================================

    reload(url, mode = "replace") {

        fetch(url, {
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        })
        .then(r => r.text())
        .then(html => {

            // текущий ajax wrapper
            const ajaxWrapper = this.root.closest("[data-ajax-list]");

            if (!ajaxWrapper) return;

            // selector контейнера из data-container
            const containerSelector = ajaxWrapper.dataset.container;

            const container = document.querySelector(containerSelector);

            if (!container) return;

            container.innerHTML = html;

            const anchor = container.querySelector("[data-page-anchor]");

            if (anchor) {

                const top =
                    anchor.getBoundingClientRect().top
                    + window.scrollY
                    - 120;

                requestAnimationFrame(() => {
                    window.scrollTo({
                        top,
                        behavior: "auto"
                    });
                });
            }

            initPickers();

            // re-init infinite scroll
            if (typeof InfiniteScroll !== "undefined") {

                if (window.infiniteScrollInstance) {
                    window.infiniteScrollInstance.disabled = true;
                }

                window.infiniteScrollInstance =
                    new InfiniteScroll(ajaxWrapper);
            }
        });
    }
}

document.addEventListener("click", (e) => {

    document.querySelectorAll(".picker.open").forEach(picker => {

        if (!picker.contains(e.target)) {
            picker.classList.remove("open");
        }

    });

});

function initPickers() {

    document.querySelectorAll("[data-picker]").forEach(root => {

        if (!root.dataset.initialized) {

            root.dataset.initialized = "1";

            const instance = new PickerSystem(root);

            root._pickerInstance = instance; 
        }

    });

    // =========================================
    // INIT INFINITE SCROLL
    // =========================================

    const wrapper = document.querySelector("[data-ajax-list]");

    if (wrapper) {
        if (!window.infiniteScrollInstance) {
            window.infiniteScrollInstance =
                new InfiniteScroll(wrapper);
        }
    }

}

document.addEventListener("click", (e) => {

    const link = e.target.closest(".pagination a");
    if (!link) return;

    e.preventDefault();

    const url = new URL(link.href);
    const page = url.searchParams.get("page");

    // disable infinite scroll
    if (window.infiniteScrollInstance) {
        window.infiniteScrollInstance.disabled = true;
    }

    const loadedPage = document.querySelector(
        `[data-items][data-page="${page}"]`
    );

    // =========================
    // CASE 1: уже загружено
    // =========================
    if (loadedPage) {

        const top =
            loadedPage.getBoundingClientRect().top
            + window.scrollY
            - 120;

        window.scrollTo({
            top,
            behavior: "auto"
        });

        setTimeout(() => {
            if (window.infiniteScrollInstance) {
                window.infiniteScrollInstance.disabled = false;
            }
        }, 300);

        return;
    }

    // =========================
    // CASE 2: нужно reload
    // =========================
    const picker = document.querySelector("[data-picker]");

    if (picker?._pickerInstance) {
        picker._pickerInstance.reload(url);
    }
});

window.infiniteScrollInstance = null;