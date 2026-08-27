"""The demo application the reusable pipeline builds, tests, and scans.

Deliberately small and deliberately clean: this is the target the pipeline
runs against, not a vulnerability showcase. See docs/quality-gates.md for
the thresholds the security scan stages enforce against whatever a real
consumer of this pipeline builds.
"""

from __future__ import annotations

import re

from fastapi import FastAPI
from pydantic import BaseModel, field_validator

__all__ = ["create_app"]

_NAME_PATTERN = re.compile(r"^[A-Za-z ]{1,50}$")


class GreetRequest(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def name_must_be_alphabetic(cls, value: str) -> str:
        # Input validation at the boundary -- rejects anything that isn't
        # plain letters/spaces before it ever reaches a response template,
        # rather than relying on output escaping alone.
        if not _NAME_PATTERN.match(value):
            raise ValueError("name must be 1-50 alphabetic characters")
        return value


def create_app() -> FastAPI:
    app = FastAPI(title="devsecops-pipeline demo app")

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/greet")
    def greet(request: GreetRequest) -> dict[str, str]:
        return {"message": f"Hello, {request.name}!"}

    @app.get("/version")
    def version() -> dict[str, str]:
        return {"version": "1.0.0"}

    return app
