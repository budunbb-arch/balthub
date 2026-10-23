/* /opt/balthub/static/assets/js/common.js */

/* === TRANSLATIONS === */
const localeNode = document.getElementById("translations-data");
const translations = localeNode ? JSON.parse(localeNode.textContent) : {};
const t = key => translations[key] ?? `[${key}]`;