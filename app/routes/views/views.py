from flask import (
    Blueprint,
    render_template,
    request,
    url_for,
    current_app,
    jsonify,
    abort,
    session,
    redirect,
)

from flask_socketio import SocketIO

import os
import json
import subprocess
from app.models.Packets import Packets
from app.models.Packet import Packet
from app.models.DENM import DENM
from app.models.CAM import CAM


# Créer un blueprint pour les vues
views_blueprint = Blueprint("views", __name__)


@views_blueprint.route("/")
def index():
    # Utiliser le chemin absolu depuis la racine de l'application Flask
    data_dir = os.path.join(current_app.root_path, "data/json")

    try:
        # Liste tous les fichiers .json et les trier par date de modification, les plus récents d'abord
        files = sorted(
            (f for f in os.listdir(data_dir) if f.endswith(".json")),
            key=lambda f: os.path.getmtime(os.path.join(data_dir, f)),
            reverse=True,
        )

        # Prendre les cinq fichiers les plus récents
        recent_files = files[:10]
    except FileNotFoundError:
        recent_files = []
        print(f"Erreur: Le dossier spécifié n'existe pas {data_dir}")
    except Exception as e:
        recent_files = []
        print(f"Erreur: {e}")

    # Passer la liste des fichiers à la vue pour affichage
    return render_template("index.html", recent_files=recent_files)


@views_blueprint.route("/packets")
def packets_no_filename():
    filename = session.get("last_used_file")
    if filename:
        return redirect(url_for("views.packets", filename=filename))
    else:
        # Handle the case where there is no filename in the session, perhaps redirecting to an error page or main index
        return redirect(url_for("views.index"))


@views_blueprint.route("/packets/<filename>")
def packets(filename):
    page = request.args.get("page", 1, type=int)
    per_page = 10  # Number of packets per page
    data_dir = os.path.join(current_app.root_path, "data/json")
    file_path = os.path.join(data_dir, filename)

    try:
        packets_collection = Packets(file_path)
        session["last_used_file"] = filename  # Update the last used file in the session
    except FileNotFoundError:
        abort(404, description="File not found.")
    except ValueError as e:
        abort(400, description=str(e))

    total_packets = len(packets_collection.packets)
    total_pages = (total_packets + per_page - 1) // per_page
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    packets_page = packets_collection.packets[start_index:end_index]

    pagination = {
        "total": total_packets,
        "page": page,
        "total_pages": total_pages,
        "start_page": max(1, page - 5),
        "end_page": min(total_pages, page + 5),
    }

    return render_template(
        "packets.html", packets=packets_page, pagination=pagination, file=filename
    )


@views_blueprint.route("/dashboard")
def dashboard():
    filename = session.get("last_used_file")
    if not filename:
        # If no file has been selected yet, redirect or handle accordingly
        return redirect(url_for("views.index"))

    data_dir = os.path.join(current_app.root_path, "data/json")
    file_path = os.path.join(data_dir, filename)

    try:
        packets_collection = Packets(file_path)
    except FileNotFoundError:
        abort(404, description="File not found.")
    except ValueError as e:
        abort(400, description=str(e))

    # print(packets_collection.time_series_data())
    # packets_collection.test()
    # print(packets_collection.test())

    return render_template("dashboard.html", packets=packets_collection, file=filename)


# DENMmap
@views_blueprint.route("/DENMmap")
def DENMmap():
    filename = session.get("last_used_file")
    if not filename:
        # If no file has been selected yet, redirect or handle accordingly
        return redirect(url_for("views.index"))

    data_dir = os.path.join(current_app.root_path, "data/json")
    file_path = os.path.join(data_dir, filename)

    try:
        packets_collection = Packets(file_path)
    except FileNotFoundError:
        abort(404, description="File not found.")
    except ValueError as e:
        abort(400, description=str(e))

    return render_template("DENMmap.html", packets=packets_collection, file=filename)


def get_unique_filename(base_folder, base_filename):
    counter = 1
    filename = base_filename
    while os.path.exists(os.path.join(base_folder, filename)):
        filename = f"{os.path.splitext(base_filename)[0]}_{counter}.pcap"
        counter += 1
    return filename


@views_blueprint.route("/upload", methods=["POST"])
def upload_file():
    if "files" not in request.files:
        return "Aucun fichier n'a été fourni.", 400

    files = request.files.getlist("files")
    if len(files) == 0 or all(file.filename == "" for file in files):
        return "Aucun fichier sélectionné.", 400

    base_upload_folder = current_app.config["UPLOAD_FOLDER"]
    pcap_folder = os.path.join(base_upload_folder, "pcap")
    json_folder = os.path.join(base_upload_folder, "json")

    os.makedirs(pcap_folder, exist_ok=True)
    os.makedirs(json_folder, exist_ok=True)

    pcap_files = []

    for file in files:
        if file.filename.endswith(".pcap"):
            filename = os.path.join(pcap_folder, file.filename)
            file.save(filename)
            pcap_files.append(filename)

    if pcap_files:
        combined_pcap = os.path.join(pcap_folder, "combined.pcap")
        json_output = os.path.join(json_folder, "combined.json")

        subprocess.run(
            [
                os.path.join("/Applications/Wireshark.app/Contents/MacOS/mergecap"),
                "-w",
                combined_pcap,
            ]
            + pcap_files,
            check=True,
        )

        with open(json_output, "w") as json_file:
            subprocess.run(
                [
                    os.path.join("/Applications/Wireshark.app/Contents/MacOS/tshark"),
                    "-r",
                    combined_pcap,
                    "-T",
                    "json",
                ],
                stdout=json_file,
                check=True,
            )

        return redirect(
            url_for("views.packets", filename=os.path.basename(json_output))
        )

    return "Aucun fichier PCAP à traiter.", 400


@views_blueprint.route("/deadzone")
def deadzone():
    filename = session.get("last_used_file")
    if not filename:
        # If no file has been selected yet, redirect or handle accordingly
        return redirect(url_for("views.index"))

    data_dir = os.path.join(current_app.root_path, "data/json")
    file_path = os.path.join(data_dir, filename)

    try:
        packets_collection = Packets(file_path)
    except FileNotFoundError:
        abort(404, description="File not found.")
    except ValueError as e:
        abort(400, description=str(e))

    return render_template("deadzone.html", packets=packets_collection, file=filename)
