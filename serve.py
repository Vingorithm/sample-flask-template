"""Production server: Waitress listening on localhost behind Apache (HTTPS).

Run:  python serve.py
All options come from .env (see WAITRESS_* in .env.example).
"""

from __future__ import annotations

from waitress import serve

from app import create_app
from app.config import env_int, env_str


def main() -> None:
    app = create_app()

    serve(
        app,
        host=env_str("WAITRESS_HOST", "127.0.0.1"),
        port=env_int("WAITRESS_PORT", 8000),
        threads=env_int("WAITRESS_THREADS", 8),
        connection_limit=env_int("WAITRESS_CONNECTION_LIMIT", 100),
        channel_timeout=env_int("WAITRESS_CHANNEL_TIMEOUT", 120),
        # Trust X-Forwarded-* only from Apache, so request.scheme becomes
        # "https", request.remote_addr is the real client IP, and url_for(...,
        # _external=True) builds https:// links.
        trusted_proxy=env_str("WAITRESS_TRUSTED_PROXY", "127.0.0.1"),
        trusted_proxy_count=1,
        trusted_proxy_headers="x-forwarded-for x-forwarded-proto x-forwarded-host",
        clear_untrusted_proxy_headers=True,
        url_prefix=env_str("WAITRESS_URL_PREFIX", ""),
        ident=env_str("APP_NAME", "app"),
    )


if __name__ == "__main__":
    main()
