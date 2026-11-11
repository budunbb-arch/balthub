document.addEventListener("DOMContentLoaded", () => {
    const configureRegistrationForm = form => {
        const name = form.querySelector('[name="name"]');
        const password = form.querySelector('[name="password"]');
        const passwordConfirm = form.querySelector('[name="password_confirm"]');

        const validate = () => {
            name.setCustomValidity(
                name.value.trim()
                    && name.value.trim().split(/\s+/).filter(Boolean).length < 2
                    ? t("username_required")
                    : "",
            );

            let passwordError = "";
            if (password.value && (
                !/\p{Lu}/u.test(password.value)
                || !/\p{Ll}/u.test(password.value)
                || !/[0-9]/.test(password.value)
            )) {
                passwordError = t("password_combination");
            }
            password.setCustomValidity(passwordError);
            passwordConfirm.setCustomValidity(
                passwordConfirm.value && passwordConfirm.value !== password.value
                    ? t("password_mismatch")
                    : "",
            );
        };

        [name, password, passwordConfirm].forEach(input => {
            input.addEventListener("input", validate);
        });
        validate();

        const generateButton = form.querySelector("[data-generate-account-password]");
        if (generateButton) {
            generateButton.addEventListener("click", () => {
                if (!window.crypto?.getRandomValues) {
                    toastr.error(t("passgen_browser"));
                    return;
                }

                const uppercase = "ABCDEFGHJKLMNPQRSTUVWXYZ";
                const lowercase = "abcdefghijkmnopqrstuvwxyz";
                const digits = "23456789";
                const characters = uppercase + lowercase + digits;
                const randomIndex = max => {
                    const limit = Math.floor(0x100000000 / max) * max;
                    const random = new Uint32Array(1);
                    do {
                        window.crypto.getRandomValues(random);
                    } while (random[0] >= limit);
                    return random[0] % max;
                };

                const generated = [
                    uppercase[randomIndex(uppercase.length)],
                    lowercase[randomIndex(lowercase.length)],
                    digits[randomIndex(digits.length)],
                ];
                while (generated.length < 16) {
                    generated.push(characters[randomIndex(characters.length)]);
                }
                for (let index = generated.length - 1; index > 0; index -= 1) {
                    const swapIndex = randomIndex(index + 1);
                    [generated[index], generated[swapIndex]] = [
                        generated[swapIndex],
                        generated[index],
                    ];
                }

                const value = generated.join("");
                password.value = value;
                passwordConfirm.value = value;
                password.dispatchEvent(new Event("input", { bubbles: true }));
                passwordConfirm.dispatchEvent(new Event("input", { bubbles: true }));
            });
        }
    };

    const refreshCaptcha = (form, challenge) => {
        const captcha = form.querySelector("[data-slider-captcha]");
        if (!challenge || !captcha) {
            return false;
        }

        captcha.dataset.target = challenge.target;
        captcha.querySelector('[name="captcha_id"]').value = challenge.id;
        const slider = captcha.querySelector("[data-captcha-slider]");
        slider.value = "0";
        slider.dispatchEvent(new Event("input", { bubbles: true }));
        return true;
    };

    const bindAjaxForm = (form, onSuccess, fallbackError, onError = () => {}) => {
        const submit = form.querySelector('button[type="submit"]');
        if (!submit) {
            return;
        }

        form.addEventListener("submit", async event => {
            event.preventDefault();

            if (form.dataset.submitting === "true") {
                return;
            }
            if (!form.reportValidity()) {
                return;
            }

            const turnstile = form.querySelector(".cf-turnstile");
            if (
                turnstile
                && !form.querySelector('[name="cf-turnstile-response"]')?.value
            ) {
                onError(t("text_notbot"));
                toastr.error(t("text_notbot"));
                return;
            }

            form.dataset.submitting = "true";
            submit.disabled = true;
            onError("");

            try {
                const formData = new FormData(form);
                const response = await fetch(form.action, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": formData.get("csrfmiddlewaretoken"),
                        "X-Requested-With": "XMLHttpRequest",
                        "Accept": "application/json",
                    },
                    body: formData,
                });
                const data = await response.json();

                const captchaRefreshed = refreshCaptcha(form, data.captcha);

                if (response.ok && data.success) {
                    onSuccess(data);
                    return;
                }

                if (window.turnstile && turnstile) {
                    window.turnstile.reset();
                }
                const message = data.error || fallbackError;
                if (!captchaRefreshed) {
                    submit.disabled = false;
                }
                onError(message);
                toastr.error(message);
            } catch (error) {
                console.error("Account form submission failed", error);
                if (window.turnstile && turnstile) {
                    window.turnstile.reset();
                }
                submit.disabled = false;
                const message = t("connection_error");
                onError(message);
                toastr.error(message);
            } finally {
                form.dataset.submitting = "false";
            }
        });
    };

    document.querySelectorAll("[data-account-registration]").forEach(form => {
        configureRegistrationForm(form);
        const modal = form.closest(".modal");
        const success = modal.querySelector(".account-registration-success");
        const successMessage = success.querySelector("p");
        const errorMessage = modal.querySelector(".account-registration-error");

        bindAjaxForm(
            form,
            data => {
                form.hidden = true;
                successMessage.textContent = data.message;
                success.hidden = false;
            },
            t("unknown_error"),
            message => {
                errorMessage.textContent = message;
                errorMessage.hidden = !message;
            },
        );
    });

    document.querySelectorAll("[data-account-login]").forEach(form => {
        bindAjaxForm(
            form,
            data => {
                window.location.assign(data.next_url);
            },
            t("login_error"),
        );
    });

    document.querySelectorAll(".tab-pane").forEach(pane => {
        const loginForm = pane.querySelector("[data-account-login]");
        const resetForm = pane.querySelector("[data-account-password-reset]");
        const resetSuccess = pane.querySelector(".account-password-reset-success");
        if (!loginForm || !resetForm || !resetSuccess) {
            return;
        }

        const showLogin = () => {
            loginForm.hidden = false;
            resetForm.hidden = true;
            resetSuccess.hidden = true;
        };

        pane.querySelectorAll("[data-password-reset-show]").forEach(button => {
            button.addEventListener("click", () => {
                loginForm.hidden = true;
                resetForm.hidden = false;
                resetSuccess.hidden = true;
                const slider = resetForm.querySelector("[data-captcha-slider]");
                slider.dispatchEvent(new Event("input", { bubbles: true }));
            });
        });
        pane.querySelectorAll("[data-password-reset-back]").forEach(button => {
            button.addEventListener("click", showLogin);
        });

        bindAjaxForm(
            resetForm,
            data => {
                resetForm.hidden = true;
                resetSuccess.querySelector("p").textContent = data.message;
                resetSuccess.hidden = false;
                const turnstile = resetForm.querySelector(".cf-turnstile");
                if (window.turnstile && turnstile) {
                    window.turnstile.reset();
                }
            },
            t("passreset_error"),
        );
    });
});
