import cProfile
import pstats
import io
from app import create_app
import os
from flask_socketio import SocketIO

# Charger les variables d'environnement
from dotenv import load_dotenv

print("Chargement des variables d'environnement...")
load_dotenv()
print("Variables d'environnement chargées.")

# Configuration du logger
import logging
from logging.handlers import RotatingFileHandler

print("Configuration du logger...")
# Définir le niveau de logging basé sur l'environnement
if os.getenv("FLASK_ENV") == "production":
    log_level = logging.ERROR
elif os.getenv("FLASK_ENV") == "test":
    log_level = logging.CRITICAL
else:
    log_level = logging.DEBUG

# Configuration du fichier de log
handler = RotatingFileHandler("app.log", maxBytes=10000, backupCount=3)
handler.setLevel(log_level)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
print("Logger configuré.")

# Configuration du cache
from flask_caching import Cache

print("Configuration du cache...")
cache_config = {
    "DEBUG": True,  # certains paramètres peuvent être définis via des variables d'environnement
    "CACHE_TYPE": "simple",  # Type de cache, ex. Redis, FileSystem, SimpleCache
    "CACHE_DEFAULT_TIMEOUT": 300,
}

# Création de l'application Flask
print("Création de l'application Flask...")
app, socketio = create_app()
app.logger.addHandler(handler)
app.config.from_mapping(cache_config)
cache = Cache(app)
print("Application Flask créée et configurée.")

# Activer le threading si nécessaire
from werkzeug.serving import run_simple
from werkzeug.middleware.proxy_fix import ProxyFix

print("Configuration du middleware ProxyFix...")
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1
)
print("Middleware ProxyFix configuré.")

if __name__ == "__main__":
    print("Démarrage du profilage avec cProfile...")
    pr = cProfile.Profile()
    pr.enable()

    # Démarrer l'application avec ou sans reloader basé sur l'environnement
    if os.getenv("FLASK_ENV") == "development":
        print(
            "Environnement de développement détecté. Démarrage de Flask avec reloader..."
        )
        socketio.run(app, debug=True, use_reloader=True)
    else:
        print(
            "Environnement de production ou de test détecté. Démarrage de Flask sans reloader..."
        )
        socketio.run(app, host="localhost", port=5000, use_reloader=False, debug=False)

    pr.disable()
    print("Profilage terminé. Génération du rapport...")
    s = io.StringIO()
    sortby = pstats.SortKey.CUMULATIVE
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())
    print("Rapport de profilage généré.")
