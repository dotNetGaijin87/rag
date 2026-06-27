"""Flask application factory."""

from __future__ import annotations

import logging

import requests
from flask import Flask, jsonify
from flask_cors import CORS

from .api import api
from .config import Config
from .container import Container


def create_app(config: Config | None = None) -> Flask:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    config = config or Config.from_env()
    app = Flask(__name__)
    CORS(app)

    container = Container(config)
    app.config["CONTAINER"] = container

    # Blocks until Neo4j is reachable, then creates indexes.
    container.graph.ensure_schema()

    app.register_blueprint(api, url_prefix="/api")
    _register_error_handlers(app)

    @app.teardown_appcontext
    def _noop(_exc):  # driver lifecycle is process-scoped; closed on shutdown
        return None

    app.logger.info("RAG backend ready.")
    return app


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(ValueError)
    def _bad_request(exc: ValueError):
        return jsonify({"error": str(exc)}), 400

    @app.errorhandler(requests.RequestException)
    def _upstream_error(exc: requests.RequestException):
        app.logger.exception("Upstream (Ollama) error")
        return (
            jsonify({"error": "The language model service is unavailable.", "detail": str(exc)}),
            502,
        )

    @app.errorhandler(Exception)
    def _internal_error(exc: Exception):
        app.logger.exception("Unhandled error")
        return jsonify({"error": "Internal server error.", "detail": str(exc)}), 500
