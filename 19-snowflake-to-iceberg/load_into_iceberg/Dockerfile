FROM python:3.12.4-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync

COPY *.py .

CMD ["uv", "run", "python", "task.py"]
