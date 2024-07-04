<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="author" content="@author Eliot CALD">
    <title>Carte zone blanche</title>

    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.3/dist/leaflet.css" integrity="sha256-kLaT2GOSpHechhsozzB+flnD+zUyjE2LlfWPgU04xyI=" crossorigin=""/>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/leaflet.markercluster@1.3.0/dist/MarkerCluster.css" />
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/leaflet.markercluster@1.3.0/dist/MarkerCluster.Default.css" />
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
    
    <style type="text/css">
	    #maCarte{ /* la carte DOIT avoir une hauteur sinon elle n'apparaît pas */
	        height:92vh;
            z-index: 1;
	    }

        #loader {
            display: none;
            position: absolute;
            left: 50%;
            top: 50%;
            z-index: 10;
            width: 120px;
            height: 120px;
            margin: -76px 0 0 -76px;
            border: 16px solid #f3f3f3;
            border-radius: 50%;
            border-top: 16px solid #3498db;
            -webkit-animation: spin 2s linear infinite;
            animation: spin 2s linear infinite;
        }

        @-webkit-keyframes spin {
            0% { -webkit-transform: rotate(0deg); }
            100% { -webkit-transform: rotate(360deg); }
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
	</style>

</head>
<body>
    <div id="loader"></div>
    <div id="maCarte" class="carte"></div>
    

    <div class="container-fluid">
        

        <table class="table table-bordered table-dark">
            <tr>
                <td>
                    <label for="filtre_dz">Points dead zone</label>
                    <input type="checkbox" id="filtre_dz" name="filtre_dz" onclick="afficher_carte()">
                </td>
                <td>
                    <label for="filtre_antenne">Antennes</label>
                    <input type="checkbox" id="filtre_antenne" name="filtre_antenne" onclick="afficher_carte()">
                </td>
                <td>
                    <label for="filtre_itineraire">Itineraire</label>
                    <input type="checkbox" id="filtre_itineraire" name="filtre_itineraire" onclick="afficher_carte()">
                </td>
                <td>
                    <label for="filtre_polyline">Polyline dead zone</label>
                    <input type="checkbox" id="filtre_polyline" name="filtre_polyline" onclick="afficher_carte()" checked>
                </td>
                <td>
                    <label for="filtre_route">Polyline route</label>
                    <input type="checkbox" id="filtre_route" name="filtre_route" onclick="afficher_carte()">
                </td>
            </tr>
        </table>

        <div class="container-fluid">
            <div class="row">
                <div class="col-md-3">
                    <label for="fichier_polyline">Charger fichier json</label>
                    <input class="form-control" type="file" name="fichier_polyline" onchange="loadFile2(this.files[0])">
                </div>
                <div class="col-md-7"></div>
                <div class="col-md-2">
                    <div class="d-flex justify-content-end">
                        <button class="btn btn-secondary" onclick="telechargerJSON()">Télécharger JSON</button>
                    </div>
                </div>
            </div>
            <br>
            <div class="row">
                <div class="col-md-3">
                    <label for="fichier_antennes">Afficher un fichier d'antennes</label>
                    <input class="form-control" type="file" name="fichier_antennes" onchange="loadFile(this.files[0])">
                </div>
            </div>
        </div>
    </div>
    
    <br>

    <div class="container">
        <label>Rechercher dead zones</label>
        <div class="input-group">
            <input class="form-control" type='text' id="lat_centre" name="lat_centre" value="" placeholder="Latitude" required>
            <input class="form-control" type='text' id="lon_centre" name="lon_centre" value="" placeholder="Longitude" required>
            <input class="form-control" type='number' id="rayon_centre" name="rayon_centre" value="" placeholder="Rayon centre (km)" required>
            <input class="form-control" type='number' id="rayon_antenne" name="rayon_antenne" value="" placeholder="Rayon antenne (km) (Si 0 -> max | -1 -> min)" required>
            <input class="form-control" type='number' id="dist_route" name="dist_route" value="" placeholder="Distance route (km)" required>
            <button class="btn btn-secondary" onclick="generer_carte()">Rechercher</button>
        </div>
    </div>

    <br>

</body>
</html>

<script src="https://unpkg.com/leaflet@1.9.3/dist/leaflet.js" integrity="sha256-WBkoXOwTeyKclOHuWtc+i2uENFpDZ9YPdf5Hf+D7ewM=" crossorigin=""></script>
<script type="text/javascript" src="https://unpkg.com/leaflet.markercluster@1.3.0/dist/leaflet.markercluster.js"></script>
<script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
<script src="functions.js"></script>

