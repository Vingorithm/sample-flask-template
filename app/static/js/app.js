// Global scripts. Keep page-specific code in {% block scripts %}.

/**
 * fetch() wrapper that sends the CSRF token Flask-WTF expects on
 * POST/PUT/PATCH/DELETE requests. Usage: csrfFetch("/api/x", { method: "POST", ... })
 */
window.csrfFetch = function csrfFetch(url, options = {}) {
  const token = document.querySelector('meta[name="csrf-token"]')?.content;
  const headers = new Headers(options.headers || {});
  if (token) headers.set("X-CSRFToken", token);
  return fetch(url, { credentials: "same-origin", ...options, headers });
};
