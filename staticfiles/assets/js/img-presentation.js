/* /opt/balthub/static/assets/js/img-presentation.js */

const initImgPresentation = () => {

    const createOverlay = () => {

        const overlay = document.createElement("div");

        overlay.className = "img-presentation-overlay";

        overlay.innerHTML = `
            <button class="img-presentation-close" aria-label="Закрыть">&times;</button>
            <img class="img-presentation-image img-grayscale" src="" alt="">
        `;

        document.body.appendChild(overlay);

        const closeBtn = overlay.querySelector(".img-presentation-close");
        const image = overlay.querySelector(".img-presentation-image");

        const close = () => {
            overlay.classList.remove("is-visible");
            document.body.style.overflow = "";
            setTimeout(() => {
                image.src = "";
                overlay.remove();
            }, 300);
        };

        closeBtn.addEventListener("click", close);

        overlay.addEventListener("click", (e) => {
            if (e.target === overlay) {
                close();
            }
        });

        document.addEventListener("keydown", function handler(e) {
            if (e.key === "Escape") {
                close();
                document.removeEventListener("keydown", handler);
            }
        });

        return { overlay, image };
    };

    document.querySelectorAll(".img-presentation").forEach((img) => {

        img.addEventListener("click", () => {
            const { overlay, image } = createOverlay();
            image.src = img.src;
            image.alt = img.alt;
            document.body.style.overflow = "hidden";
            requestAnimationFrame(() => {
                overlay.classList.add("is-visible");
            });
        });

    });

};

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initImgPresentation);
} else {
    initImgPresentation();
}
