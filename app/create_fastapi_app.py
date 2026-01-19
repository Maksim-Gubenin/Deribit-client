"""
FastAPI application factory with custom documentation and lifespan management.

This module provides a factory function for creating FastAPI applications with
customized Swagger UI and ReDoc documentation, async lifespan management,
and ORJSON response serialization.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.responses import HTMLResponse, ORJSONResponse

from app.api import api_router
from app.api.frontend import frontend_router
from app.core import db_helper


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Async context manager for FastAPI application lifecycle.

    Handles startup and shutdown events for the application, including
    database connection management.

    Args:
        app: The FastAPI application instance.

    Yields:
        None: Control passes to the application runtime.

    """
    # Startup: Resources are initialized here
    yield
    # Shutdown: Cleanup resources
    await db_helper.dispose()


def register_static_docs_routes(app: FastAPI) -> None:
    """
    Register custom static documentation routes for Swagger UI and ReDoc.

    This function sets up custom endpoints for API documentation with
    configurable CDN URLs for JavaScript and CSS resources.

    Args:
        app: FastAPI application instance to register routes on.

    Endpoints Created:
        - GET /docs: Custom Swagger UI interface
        - GET /oauth2-redirect.html: OAuth2 redirect handler for Swagger UI
        - GET /redoc: Custom ReDoc interface

    """

    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html() -> HTMLResponse:
        """
        Custom Swagger UI HTML endpoint.

        Returns:
            HTMLResponse: Rendered Swagger UI interface.

        Configuration:
            - Uses external CDN for Swagger UI assets
            - Includes OAuth2 redirect support
            - Custom title with application name
        """
        # Используем пустую строку вместо None
        openapi_url = app.openapi_url or ""
        oauth2_redirect_url = app.swagger_ui_oauth2_redirect_url or ""

        return get_swagger_ui_html(
            openapi_url=openapi_url,
            title=app.title + " - Swagger UI",
            oauth2_redirect_url=oauth2_redirect_url,
            swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
            swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
        )

    # Используем дефолтный URL если app.swagger_ui_oauth2_redirect_url None
    oauth2_redirect_url = app.swagger_ui_oauth2_redirect_url or "/oauth2-redirect.html"

    @app.get(oauth2_redirect_url, include_in_schema=False)
    async def swagger_ui_redirect() -> HTMLResponse:
        """
        OAuth2 redirect handler for Swagger UI.

        Returns:
            HTMLResponse: OAuth2 redirect page for Swagger UI authentication.
        """
        return get_swagger_ui_oauth2_redirect_html()

    @app.get("/redoc", include_in_schema=False)
    async def redoc_html() -> HTMLResponse:
        """
        Custom ReDoc HTML endpoint.

        Returns:
            HTMLResponse: Rendered ReDoc interface.

        Configuration:
            - Uses external CDN for ReDoc assets
            - Custom title with application name
        """
        # Используем пустую строку вместо None
        openapi_url = app.openapi_url or ""

        return get_redoc_html(
            openapi_url=openapi_url,
            title=app.title + " - ReDoc",
            redoc_js_url="https://unpkg.com/redoc@2/bundles/redoc.standalone.js",
        )


def create_app(
    create_custom_static_urls: bool = False,
) -> FastAPI:
    """
    Factory function for creating configured FastAPI applications.

    Creates a FastAPI application with:
    - ORJSON response serialization for performance
    - Async lifespan management
    - Optional custom documentation endpoints

    Args:
        create_custom_static_urls: If True, registers custom documentation
                                  routes instead of using FastAPI defaults.

    Returns:
        FastAPI: Configured application instance.
    """

    app = FastAPI(
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
        docs_url=None if create_custom_static_urls else "/docs",
        redoc_url=None if create_custom_static_urls else "/redoc",
    )

    app.include_router(api_router)
    app.include_router(frontend_router)

    if create_custom_static_urls:
        register_static_docs_routes(app)

    return app
