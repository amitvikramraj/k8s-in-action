FROM python:3.12-slim-trixie

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV UV_LINK_MODE=copy UV_COMPILE_BYTECODE=1
ENV UV_SYSTEM_PYTHON=false
ENV UV_PROJECT_ENVIRONMENT=/app/.venv
# ^^^https://docs.astral.sh/uv/guides/integration/docker/#optimizations
# ^^^https://docs.astral.sh/uv/guides/integration/docker/#compiling-bytecode
# ^^^https://docs.astral.sh/uv/guides/integration/docker/#caching

# RUN mkdir -p /app/kiada

COPY pyproject.toml README.md uv.lock /app/

# install dependencies
RUN uv sync --locked

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy the rest of the application code
COPY . /app/

# Run the application
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
