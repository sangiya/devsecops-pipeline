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

# setuptools ships with the base image at a version behind published CVE
# fixes (CVE-2025-47273); msgpack is a transitive dependency of uvicorn
# pulled in with a known-vulnerable version (GHSA-6v7p-g79w-8964). Both are
# upgraded explicitly before installing the project so pip's resolver picks
# already-patched versions rather than whatever the base image snapshotted.
RUN pip install --no-cache-dir --upgrade pip setuptools msgpack && pip install --no-cache-dir .

USER appuser
EXPOSE 8000
CMD ["uvicorn", "demo_app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
