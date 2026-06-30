from flask import Blueprint, render_template

demo_bp = Blueprint("demo", __name__)


@demo_bp.route("/eq5-demo", methods=["GET"])
def demo_index():
    """Página de demostración del módulo de integraciones (Equipo 5)."""
    return render_template("index.html")
