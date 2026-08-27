"""A minimal FastAPI service used as the target for the pipeline's build/test/scan stages."""

from .main import create_app

__all__ = ["create_app"]
