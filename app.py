from flask import Flask

from config import Config
from routes.auth import auth_bp
from routes.clientes import clientes_bp
from routes.servicios import servicios_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.register_blueprint(auth_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(servicios_bp)

    @app.errorhandler(404)
    def not_found(e):
        return {"success": False, "message": "Recurso no encontrado"}, 404

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=app.config["FLASK_ENV"] == "development")
