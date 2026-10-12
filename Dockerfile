FROM node:24-alpine AS ui
WORKDIR /build/ui
COPY ui/package*.json ./
RUN npm ci
COPY ui/ ./
RUN npm run build

FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 SOLUS_DATA_DIR=/data
WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src/ ./src/
COPY --from=ui /build/src/solus/static/solus/ ./src/solus/static/solus/
RUN pip install --no-cache-dir . && useradd --create-home --uid 10001 solus && mkdir /data && chown solus:solus /data
USER solus
VOLUME /data
EXPOSE 8000
CMD ["solus", "serve", "--host", "0.0.0.0"]
