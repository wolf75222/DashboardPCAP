#!/bin/bash

# Fonctions pour les couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

function print_info {
    echo -e "${GREEN}$1${NC}"
}

function print_warning {
    echo -e "${YELLOW}$1${NC}"
}

function print_error {
    echo -e "${RED}$1${NC}"
}

# Naviguer au dossier racine du projet où run.py est situé
cd "$(dirname "$0")/.." || { print_error "Erreur: Impossible de naviguer au dossier racine du projet."; exit 1; }

# Activer l'environnement virtuel
if [ -d "venv" ]; then
    print_info "Activation de l'environnement virtuel..."
    source venv/bin/activate
    if [ $? -ne 0 ]; then
        print_error "Erreur: Impossible d'activer l'environnement virtuel."
        exit 1
    fi
    print_info "Environnement virtuel activé avec succès."
else
    print_error "Erreur: Le répertoire de l'environnement virtuel 'venv' est introuvable."
    exit 1
fi

# Chargement des variables d'environnement depuis le dossier 'app'
if [ -f ./app/.env ]; then
    print_info "Chargement des variables d'environnement depuis le fichier .env..."
    source ./app/.env
    print_info "Variables d'environnement chargées avec succès."
else
    print_error "Erreur: Le fichier .env est introuvable dans le dossier 'app'. Assurez-vous qu'il est présent."
    exit 1
fi

# Génération de la documentation avec Doxygen si l'option -d est fournie
if [ "$1" = "-d" ]; then
    print_info "Génération de la documentation avec Doxygen..."
    if doxygen Doxyfile; then
        print_info "Documentation générée avec succès."
        print_info "----------------------------------------------------------------------"
        print_info "Lancement de la documentation..."
        if open ./docs/html/index.html; then
            print_info "Documentation ouverte avec succès."
        else
            print_error "Erreur: Impossible d'ouvrir la documentation."
            exit 1
        fi
    else
        print_error "Erreur: Échec de la génération de la documentation."
        exit 1
    fi
    exit 0
fi

# Définition des chemins pour Tailwind CSS
TAILWIND_INPUT="./app/static/src/input.css"
TAILWIND_OUTPUT="./app/static/dist/css/output.css"

print_info "Démarrage de Tailwind CSS Build Process en mode --watch..."
if npx tailwindcss -i $TAILWIND_INPUT -o $TAILWIND_OUTPUT --watch & then
    print_info "Processus Tailwind CSS démarré avec succès."
else
    print_error "Erreur: Échec du démarrage du processus Tailwind CSS."
    exit 1
fi

# Calcul du temps de lancement
start_time=$(date +%s)

print_info "Démarrage de l'application Flask..."

# Vérification de l'environnement pour ajuster le mode de démarrage de Flask
case "$FLASK_ENV" in
    development)
        print_info "Environnement de développement détecté."
        export FLASK_DEBUG=1
        ;;
    production)
        print_info "Environnement de production détecté."
        export FLASK_DEBUG=0
        ;;
    test)
        print_info "Environnement de test détecté."
        ;;
    *)
        print_warning "Environnement non spécifié, démarrage en mode développement par défaut."
        export FLASK_DEBUG=1
        ;;
esac

# Calcul du temps juste avant de démarrer l'application
end_time=$(date +%s)
execution_time=$((end_time - start_time))
print_info "----------------------------------------------------------------------"
print_info "Temps de lancement : $execution_time secondes"
print_info "----------------------------------------------------------------------"

# Vérification que Flask est installé
if ! python3 -c "import flask" &> /dev/null; then
    print_error "Erreur: Flask n'est pas installé dans l'environnement virtuel."
    exit 1
fi

# Vérification que l'environnement virtuel est activé
if [[ "$VIRTUAL_ENV" == "" ]]; then
    print_error "Erreur : L'environnement virtuel n'est pas activé."
    exit 1
else
    print_info "Environnement virtuel activé avec succès."
fi

# Vérification que les modules de requirements.txt sont installés
if [ -f "requirements.txt" ]; then
    while IFS= read -r requirement
    do
        module=$(echo $requirement | sed 's/==.*//')
        # Gérer les noms d'import spécifiques
        case $module in
            python-dotenv)
                import_name="dotenv"
                ;;
            flask-socketio)
                import_name="flask_socketio"
                ;;
            datetime)
                import_name="datetime"
                ;;
            *)
                import_name=$module
                ;;
        esac

        if ! python3 -c "import $import_name" &> /dev/null; then
            print_error "Erreur: Le module $import_name (installé en tant que $module) n'est pas installé."
            exit 1
        fi
    done < requirements.txt
else
    print_error "Erreur: Le fichier requirements.txt est introuvable."
    exit 1
fi

print_info "Tous les modules requis sont installés."

# Démarrage de l'application Flask selon l'environnement
if [ "$FLASK_ENV" = "development" ]; then
    if ! python3 run.py; then
        print_error "Erreur: Échec du démarrage de l'application Flask en mode développement."
        exit 1
    fi
elif [ "$FLASK_ENV" = "production" ]; then
    if ! gunicorn --workers 3 --bind 0.0.0.0:5000 -m 007 "app:create_app()"; then
        print_error "Erreur: Échec du démarrage de l'application Flask en mode production."
        exit 1
    fi
elif [ "$FLASK_ENV" = "test" ]; then
    if ! python3 -m unittest discover -s tests; then
        print_error "Erreur: Échec des tests."
        exit 1
    fi
else
    if ! python3 run.py; then
        print_error "Erreur: Échec du démarrage de l'application Flask en mode développement par défaut."
        exit 1
    fi
fi

print_info "L'application Flask a démarré avec succès."

# Garder le script en cours d'exécution pour le processus Tailwind CSS --watch
wait
