"""Baseline security headers.

HSTS is set by Apache (it owns TLS); these cover the app-level basics and
apply even when the app runs without Apache in front.
"""

from flask import Flask, Response

DEFAULT_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "SAMEORIGIN",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
}


def register_security_headers(app: Flask) -> None:
    @app.after_request
    def set_security_headers(response: Response) -> Response:
        for header, value in DEFAULT_HEADERS.items():
            response.headers.setdefault(header, value)
        return response
