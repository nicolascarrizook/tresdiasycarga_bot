"""
CORS middleware for Sistema Mayra API.
"""
from fastapi.middleware.cors import CORSMiddleware
from ..core.config import settings


def setup_cors(app):
    """Setup CORS middleware."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )