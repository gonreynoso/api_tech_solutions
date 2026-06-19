import psycopg2
from flasgger import Swagger
from flask import Flask

from config import Config
from routes.auth import auth_bp
from routes.clientes import clientes_bp
from routes.planes import planes_bp
from routes.servicios import servicios_bp
from routes.usuarios import usuarios_bp
from utils.responses import error

SWAGGER_CONFIG = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/",
}

SWAGGER_TEMPLATE = {
    "swagger": "2.0",
    "info": {
        "title": "Consultora Tech Solutions API",
        "description": "API REST para gestión de clientes, servicios y autenticación.",
        "version": "1.0.0",
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Token JWT con prefijo 'Bearer '. Ej: Bearer eyJhbGciOi...",
        }
    },
}


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    Swagger(app, config=SWAGGER_CONFIG, template=SWAGGER_TEMPLATE)

    app.register_blueprint(auth_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(servicios_bp)
    app.register_blueprint(planes_bp)
    app.register_blueprint(usuarios_bp)

    @app.errorhandler(404)
    def not_found(e):
        return {"success": False, "message": "Recurso no encontrado"}, 404

    @app.errorhandler(psycopg2.OperationalError)
    def db_unavailable(e):
        app.logger.error("DB connection error: %s", e)
        return error("Servicio de base de datos no disponible", 503)

    @app.errorhandler(psycopg2.Error)
    def db_error(e):
        app.logger.error("DB error: %s", e)
        return error("Error al procesar la solicitud en la base de datos", 500)

    @app.errorhandler(Exception)
    def unhandled_error(e):
        app.logger.exception("Unhandled error")
        return error("Error interno del servidor", 500)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=app.config["FLASK_ENV"] == "development")
