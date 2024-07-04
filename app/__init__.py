from flask import Flask
from dotenv import load_dotenv
import os
from flask_socketio import SocketIO
import logging

# Charger les variables d'environnement
print("Chargement des variables d'environnement...")
load_dotenv()
print("Variables d'environnement chargées.")


def create_app():
    """Créer l'application Flask avec SocketIO intégré.

    Returns:
        Tuple (Flask, SocketIO): Tuple contenant l'instance de l'application Flask et l'instance de SocketIO.
    """

    print("Création de l'application Flask...")
    # Création de l'application Flask
    app = Flask(__name__)
    app.logger.setLevel(logging.DEBUG)
    app.logger.debug("Initialisation de l'application Flask")
    print("Application Flask créée.")

    print("Initialisation de SocketIO...")
    # Création de l'instance de SocketIO
    socketio = SocketIO(app)
    app.logger.debug("SocketIO initialisé")
    print("SocketIO initialisé.")

    print("Configuration de l'application avec les variables d'environnement...")
    # Configuration de l'application avec les variables d'environnement
    app.config["UPLOAD_FOLDER"] = os.getenv("UPLOAD_FOLDER")
    app.config["TSHARK_PATH"] = os.getenv("TSHARK_PATH")
    app.secret_key = os.getenv("SECRET_KEY")
    app.logger.debug("Configuration de l'application chargée")
    print("Configuration de l'application chargée.")

    print("Enregistrement des blueprints...")
    # Importation et enregistrement des blueprints pour les vues et l'API
    from .routes.views.views import views_blueprint

    app.register_blueprint(views_blueprint)
    app.logger.debug("Blueprint 'views' enregistré")

    from .routes.api.paquet.cam import cam_blueprint
    from .routes.api.paquet.denm import denm_blueprint
    from .routes.api.paquet.geo import geo_blueprint

    app.register_blueprint(cam_blueprint, url_prefix="/api/paquet/cam")
    app.register_blueprint(denm_blueprint, url_prefix="/api/paquet/denm")
    app.register_blueprint(geo_blueprint, url_prefix="/api/paquet/geo")
    app.logger.debug("Blueprints 'paquet' enregistrés")

    from .routes.api.paquets.cam import cam_paq_blueprint
    from .routes.api.paquets.denm import denm_paq_blueprint
    from .routes.api.paquets.geo import geo_paq_blueprint

    app.register_blueprint(cam_paq_blueprint, url_prefix="/api/paquets/cam")
    app.register_blueprint(denm_paq_blueprint, url_prefix="/api/paquets/denm")
    app.register_blueprint(geo_paq_blueprint, url_prefix="/api/paquets/geo")
    app.logger.debug("Blueprints 'paquets' enregistrés")

    print("Tous les blueprints ont été enregistrés.")
    app.logger.debug("Tous les blueprints ont été enregistrés")

    return app, socketio
