FROM python:3.10-slim

WORKDIR /app

RUN --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    pip install --no-cache-dir .

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]