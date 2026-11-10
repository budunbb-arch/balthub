/* /opt/balthub/static/assets/js/account-profile.js */
document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("form[data-account-profile]");
  if (!form) return;

  const contactFields = form.querySelector("#contactFields");
  const addButton = form.querySelector("[data-add-contact]");
  const t = (key) => {
    const node = document.getElementById("translations-data");
    const translations = node ? JSON.parse(node.textContent) : {};
    return translations[key] || "[" + key + "]";
  };

  const buildContactTypeOptions = (selectedId = "") => {
    const types = (window.ACCOUNT_PROFILE_DATA && window.ACCOUNT_PROFILE_DATA.contactTypes) || [];
    return types.map((ct) =>
      '<option value="' + ct.id + '" data-is-telephone="' + ct.isTelephone + '"' + (ct.id == selectedId ? " selected" : "") + ">" + '<i class="' + ct.code + '"></i> ' + ct.name + "</option>"
    ).join("");
  };

  const buildCountryOptions = (selectedCode = "") => {
    const countries = (window.ACCOUNT_PROFILE_DATA && window.ACCOUNT_PROFILE_DATA.phoneCountries) || [];
    return countries.map((c) =>
      '<option value="' + c.phoneCode + '" data-prefix="' + c.phoneCode + '"' + (c.code === "RU" && !selectedCode ? " selected" : "") + ">" + c.name + " (+" + c.phoneCode + ")</option>"
    ).join("");
  };

  const toggleCountryField = (typeSelect) => {
    const row = typeSelect.closest("[data-row]");
    if (!row) return;
    const countryCol = row.querySelector(".country-col");
    const isTelephone = typeSelect.selectedOptions[0] && typeSelect.selectedOptions[0].dataset.isTelephone === "true";
    if (countryCol) countryCol.classList.toggle("d-none", !isTelephone);
  };

  form.querySelectorAll("[data-row] .contact-type").forEach((select) => {
    if (select.dataset.existingId) {
      select.value = select.dataset.existingId;
      select.disabled = true;
    }
    toggleCountryField(select);
    select.addEventListener("change", () => toggleCountryField(select));
  });

  contactFields.addEventListener("click", (e) => {
    const btn = e.target.closest(".btn-remove-contact");
    if (!btn) return;
    const row = btn.closest("[data-row]");
    if (row) row.remove();
  });

  addButton.addEventListener("click", () => {
    const idx = Date.now() + Math.floor(Math.random() * 10000);
    const row = document.createElement("div");
    row.className = "contact-row mb-2";
    row.setAttribute("data-row", "");
    row.innerHTML =
      '<div class="row g-2">' +
      '<div class="col-12 col-xl-3">' +
      '<div class="form-field">' +
      '<select class="form-select contact-type px-xl-3 pe-xl-5" name="contact_type_' + idx + '" aria-label="' + t("text_contact_type") + '">' +
      '<option value="">' + t("text_select_contact_type") + '</option>' +
      buildContactTypeOptions() +
      "</select>" +
      '</div>' +
      "</div>" +
      '<div class="col-12 col-md-5 contact-value-col">' +
      '<div class="form-field field-contact position-relative contact-value-wrapper">' +
      '<input type="text" class="form-control contact-value px-xl-3" name="contact_value_' + idx + '" placeholder="' + t("text_contact_value") + '" data-is-telephone="false">' +
      '<span class="form-field-icon"></span>' +
      "</div>" +
      "</div>" +
      '<div class="col-12 col-md-2 country-col d-none d-flex align-items-end">' +
      '<select class="form-select phone-country" name="phone_country_' + idx + '" aria-label="' + t("text_country") + '">' +
      '<option value="" data-prefix="">' + t("text_country") + '</option>' +
      buildCountryOptions() +
      "</select>" +
      "</div>" +
      '<div class="col-12 col-md-2 d-flex align-items-center">' +
      '<button type="button" class="btn btn-link text-small btn-remove-contact w-100">' +
      '<i class="fa-solid fa-trash"></i> ' + t("text_remove") +
      "</button>" +
      "</div>" +
      "</div>";
    contactFields.appendChild(row);
    const typeSelect = row.querySelector(".contact-type");
    typeSelect.addEventListener("change", () => toggleCountryField(typeSelect));
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    submitButton.disabled = true;
    submitButton.textContent = t("text_send") || "\u041e\u0442\u043f\u0440\u0430\u0432\u043a\u0430\u2026";
    const formData = new FormData(form);
    try {
      const response = await fetch(form.action, {
        method: "POST",
        headers: {
          "X-CSRFToken": formData.get("csrfmiddlewaretoken") || document.querySelector('[name=csrfmiddlewaretoken]').value,
          "X-Requested-With": "XMLHttpRequest",
          "Accept": "application/json",
        },
        body: formData,
      });
      const data = await response.json();
      if (response.ok && data.success) {
        const modal = bootstrap.Modal.getInstance(form.closest(".modal"));
        if (modal) modal.hide();
        toastr.success(data.message || t("text_profile_saved"));
        if (data.contacts) {
          const contactList = document.querySelector(".account-profile .list-unstyled") || document.querySelector(".dashboard-block .list-unstyled");
          if (contactList) {
            contactList.innerHTML = data.contacts.map((c) => {
              const icon = c.code ? '<i class="' + c.code + '"></i>' : "";
              const prefix = c.prefix ? c.prefix : "";
              const postfix = c.postfix ? c.postfix : "";
              return "<li><span class=\"icon\">" + icon + "</span>" + prefix + c.value + postfix + "</li>";
            }).join("");
          }
        }
        const nameInput = form.querySelector("input[name='name']");
        const firstNameBlock = document.querySelector(".dashboard-block .list-unstyled li:first-child");
        if (firstNameBlock && nameInput) firstNameBlock.innerHTML = '<span class="icon"><i class="fa-regular fa-circle-user"></i></span>' + nameInput.value;
      } else {
        toastr.error(data.error || t("unknown_error"));
      }
    } catch (error) {
      console.error("Account profile save failed", error);
      toastr.error(t("connection_error"));
    } finally {
      submitButton.disabled = false;
      submitButton.textContent = originalText;
    }
  });
});
