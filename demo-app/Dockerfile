# Pinned to Debian 12 "bookworm" explicitly rather than the floating
# python:3.12-slim tag, which currently resolves to Debian 13 "trixie" --
# a newer release with a much shorter security-backport track record.
# bookworm is Debian's actively-patched current stable release.
FROM python:3.12-slim-bookworm

RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --uid 10001 appuser
WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

# setuptools and msgpack version floors are declared in pyproject.toml
# (build-system.requires and dependencies respectively) rather than forced
# here -- pip's isolated build environment ignores an outer `pip install
# --upgrade setuptools`, so the version bound has to live where the
# resolver actually reads it.
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir .

USER appuser
EXPOSE 8000
CMD ["uvicorn", "demo_app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
