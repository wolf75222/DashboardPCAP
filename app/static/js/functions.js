
var resultat_json = null;
var json_object = null;
var json_object_wifi = null;
var json_object_antenne = null;

var cartographie = L.map(maCarte).setView([49.2577886, 4.031926], 6);

var markerClusters_couverture = L.markerClusterGroup();
var markerClusters_dead_zone = L.markerClusterGroup();
var markerClusters_itineraire = L.markerClusterGroup();

var chemin_racine = document.URL.substring(0, document.URL.lastIndexOf('/')); // Chemin relatif à partir de l'URL actuelle

let date1 = Date.now()

afficher_carte();


/**
 * [Obsolète]
 * Execution de la requête à notre serveur pour récupérer le json qui contient les données à afficher sur la carte.
 * @author Eliot CALD
 */
function generer_carte(){
    date1 = Date.now();
    console.log("DEBUT : "+date1);
    document.getElementById("loader").style.display = "block"; //Affiche l'icone de chargement

    // Paramètres de la requête
    var lat_centre = document.getElementById('lat_centre').value;
    var lon_centre = document.getElementById('lon_centre').value;
    var rayon_centre = document.getElementById('rayon_centre').value;
    var rayon_antenne = document.getElementById('rayon_antenne').value;
    var dist_route = document.getElementById('dist_route').value;

    // Requête
    var url = "http://localhost/avance/deadzone.php?lat_centre="+lat_centre+"&lon_centre="+lon_centre+"&r_centre="+rayon_centre+"&rayon="+rayon_antenne+"&dist="+dist_route+"";


    //Envoie requête
    const xhr = new XMLHttpRequest();
    xhr.open("GET", url);
    xhr.send();
    xhr.responseType = "json";


    // resultat_json : retour brut du serveur, donc du texte au format json
    // json_object : objet json que l'on peut utiliser 
    //Reponse du serveur
    xhr.onload = () => {
        if (xhr.readyState == 4 && xhr.status == 200) {
            const data = xhr.response;
            resultat_json = data;
            json_object = JSON.parse(resultat_json);
            afficher_carte();
        } else {
            console.log(`Error: ${xhr.status}`);
        }
    };

}//fin generer_carte





//------------------------- Antenne -------------------------
/**
 * Fonction qui permet de créer et recrée la carte, de faire les tuiles et d'afficher les marqueurs séléctionnés par le filtre.
 * La fonction est appelée au début et à chaque changement de filtre (checkbox).
 * On se sert du serveur de tuile de notre OSM pour faire l'affichage de la carte.
 * @author Eliot CALD
 */
function afficher_carte(){

    cartographie.remove();

    cartographie = L.map(maCarte).setView([49.2577886, 4.031926], 6);

    //https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png //version osmfr
    //http://194.57.103.203/map/hot/{z}/{x}/{y}.png //version osm labi-*

    L.tileLayer('http://194.57.103.203/map/hot/{z}/{x}/{y}.png`', { //Visuel de la carte
        maxZoom: 20,
        minZoom: 3,
        attribution: '&copy; <a href="https://github.com/ElCald">Eliot CALD</a>'
    }).addTo(cartographie);


    // Groupes de marqueurs
    markerClusters_couverture.clearLayers();
    markerClusters_itineraire.clearLayers();
    markerClusters_dead_zone.clearLayers();



    // Checkbox de filtre pour faire l'affichage ou non sur la carte
    filtre_antenne = document.getElementById("filtre_antenne").checked;
    filtre_polyline = document.getElementById("filtre_polyline").checked;
    filtre_dz = document.getElementById("filtre_dz").checked;
    filtre_route = document.getElementById("filtre_route").checked;
    filtre_itineraire = document.getElementById("filtre_itineraire").checked;


    // Vérifie si le json crée n'est pas vide et que le contenue renvoyé par le serveur n'est pas null
    if(json_object != false && resultat_json != null){

        //------------------------- Itineraire -------------------------
        if(filtre_itineraire == true && json_object["itineraire"] != null){ // Filtre qui permet d'afficher l'itinéraire
            let tab_coord_itin = new Array(); // Tableau contenant tout l'itinéraire

            // Analyse du json
            for(var i=0; i<json_object["itineraire"].length; i++){
                for(var j=0; j<json_object["itineraire"][i].length; j++){
                    tab_coord_itin.push({lat: json_object["itineraire"][i][j]["lat"], lon: json_object["itineraire"][i][j]["lon"], dept: json_object["itineraire"][i][j]["dept"], sup_id: json_object["itineraire"][i][j]["id"]});
                }
            }

        
            // Conversion des éléments en int ou float
            for(let i=0; i<tab_coord_itin.length; i++){
                tab_coord_itin[i].lat = parseFloat(tab_coord_itin[i].lat);
                tab_coord_itin[i].lon = parseFloat(tab_coord_itin[i].lon);
                tab_coord_itin[i].dept = parseInt(tab_coord_itin[i].dept);
                tab_coord_itin[i].sup_id = parseInt(tab_coord_itin[i].sup_id);
            }

            // Création des marqueurs et disposition sur la cartographie
            for(let i=0; i<tab_coord_itin.length; i++){
                var myIcon = L.icon({
                    iconUrl: chemin_racine+'/icons/Festung.png',
                    iconSize: [40, 40],
                    iconAnchor: [10, 40],
                    popupAnchor: [0, -35],
                });
                var marker = L.marker([tab_coord_itin[i].lat, tab_coord_itin[i].lon], { icon: myIcon });
                marker.bindPopup("<strong>Route</strong><br>id: "+tab_coord_itin[i].sup_id+"<br>lat: "+tab_coord_itin[i].lat+"<br>lon: "+tab_coord_itin[i].lon);
                markerClusters_itineraire.addLayer(marker);
            }
            cartographie.addLayer(markerClusters_itineraire);

        }


        
        //------------------------- Dead_zone -------------------------
        if(filtre_dz == true && json_object["dead_zone"] != null){
            let tab_coord_dz = new Array();

            for(var i=0; i<json_object["dead_zone"].length; i++){
                tab_coord_dz.push({lat: json_object["dead_zone"][i]["lat"], lon: json_object["dead_zone"][i]["lon"], dept: json_object["dead_zone"][i]["dept"], sup_id: json_object["dead_zone"][i]["id"]});       
            }


            for(let i=0; i<tab_coord_dz.length; i++){
                tab_coord_dz[i].lat = parseFloat(tab_coord_dz[i].lat);
                tab_coord_dz[i].lon = parseFloat(tab_coord_dz[i].lon);
                tab_coord_dz[i].dept = parseInt(tab_coord_dz[i].dept);
                tab_coord_dz[i].sup_id = parseInt(tab_coord_dz[i].sup_id);
            }


            for(let i=0; i<tab_coord_dz.length; i++){
                var myIcon = L.icon({
                    iconUrl: chemin_racine+'/icons/arrow_up.png',
                    iconSize: [20, 20],
                    iconAnchor: [10, 5],
                    popupAnchor: [-3, -76],
                });

                var marker = L.marker([tab_coord_dz[i].lat, tab_coord_dz[i].lon], { icon: myIcon });
                markerClusters_dead_zone.addLayer(marker);
            }
            cartographie.addLayer(markerClusters_dead_zone);
        }


        //------------------------- Route -------------------------
        if(filtre_route == true && json_object["itineraire"] != null){
            

            for(var i=0; i<json_object["itineraire"].length; i++){
                let tab_coord_polyline = new Array();

                for(var j=0; j<json_object["itineraire"][i].length; j++){

                    if(json_object["itineraire"][i].length > 1){
                        tab_coord_polyline.push([ json_object["itineraire"][i][j]["lat"],  json_object["itineraire"][i][j]["lon"] ]);
                    }
                    
                }

                if(json_object["itineraire"][i].length > 1){
                    var polyline = L.polyline(tab_coord_polyline, {color: 'yellow'}).addTo(cartographie);
                }
            }
        }


        
        //------------------------- Polyline -------------------------
        if(filtre_polyline == true && json_object["polyline"] != null){
            
            for(var i=0; i<json_object["polyline"].length; i++){
                let tab_coord_polyline = new Array();

                for(var j=0; j<json_object["polyline"][i].length; j++){
                    tab_coord_polyline.push([ json_object["polyline"][i][j]["lat"],  json_object["polyline"][i][j]["lon"] ]);
                }

                if(json_object["polyline"][i].length > 1){
                    var polyline = L.polyline(tab_coord_polyline, {color: 'red'}).addTo(cartographie);
                }
                
            }
            
        }



        //------------------------- Couverture -------------------------
        if(filtre_antenne == true && json_object["couverture"] != null){
            // ------------------------- Antenne -------------------------
            let tab_coord_antenne = new Array();

            
            for(var i=0; i<json_object["couverture"].length; i++){
                tab_coord_antenne.push({lat: json_object["couverture"][i]["lat"], lon: json_object["couverture"][i]["lon"], dept: json_object["couverture"][i]["dept"], sup_id: json_object["couverture"][i]["id"], r_moy_min: json_object["couverture"][i]["rayon_moy_min"], r_moy_max: json_object["couverture"][i]["rayon_moy_max"], r_utilise: json_object["couverture"][i]["rayon_utilise"], operateur: json_object["couverture"][i]["operateur"]});
            }


            for(let i=0; i<tab_coord_antenne.length; i++){
                tab_coord_antenne[i].lat = parseFloat(tab_coord_antenne[i].lat);
                tab_coord_antenne[i].lon = parseFloat(tab_coord_antenne[i].lon);
                tab_coord_antenne[i].dept = parseInt(tab_coord_antenne[i].dept);
                tab_coord_antenne[i].sup_id = parseInt(tab_coord_antenne[i].sup_id);
                tab_coord_antenne[i].r_moy_max = parseFloat(tab_coord_antenne[i].r_moy_max);
                tab_coord_antenne[i].r_moy_min = parseFloat(tab_coord_antenne[i].r_moy_min);
                tab_coord_antenne[i].r_utilise = parseFloat(tab_coord_antenne[i].r_utilise);
            }

        

            //------------------------- Rayon antenne -------------------------
            for(let i=0; i<tab_coord_antenne.length; i++){
                var myIcon = L.icon({
                    iconUrl: chemin_racine+'/icons/antenne.png',
                    iconSize: [25, 25],
                    iconAnchor: [10, 5],
                    popupAnchor: [3, 0],
                });

                var marker = L.marker([tab_coord_antenne[i].lat, tab_coord_antenne[i].lon], { icon: myIcon });
                

                marker.bindPopup("<strong>Antenne</strong><br>sup_id: "+tab_coord_antenne[i].sup_id+"<br>lat: "+tab_coord_antenne[i].lat+"<br>lon: "+tab_coord_antenne[i].lon+"<br>rayon: "+tab_coord_antenne[i].r_utilise+"<br>opérateur: "+tab_coord_antenne[i].operateur);
                markerClusters_couverture.addLayer(marker);

                var cercle = L.circle([tab_coord_antenne[i].lat, tab_coord_antenne[i].lon], {
                    color: 'blue',
                    fillColor: 'blue',
                    fillOpacity: 0.1,
                    radius: tab_coord_antenne[i].r_utilise,
                }).addTo(cartographie);
            }

            cartographie.addLayer(markerClusters_couverture);


            
            // ------------------------- UBR json_object  -------------------------
            if(json_object["ubr"] != null){
                let tab_coord_ubr = new Array();
                
                for(var i=0; i<json_object["ubr"].length; i++){
                    tab_coord_ubr.push({lat: json_object["ubr"][i]["lat"], lon: json_object["ubr"][i]["lon"], r_utilise: json_object["ubr"][i]["rayon"], etat: json_object["ubr"][i]["etat"]});
                }


                for(let i=0; i<tab_coord_ubr.length; i++){
                    tab_coord_ubr[i].lat = parseFloat(tab_coord_ubr[i].lat);
                    tab_coord_ubr[i].lon = parseFloat(tab_coord_ubr[i].lon);
                    tab_coord_ubr[i].r_utilise = parseFloat(tab_coord_ubr[i].r_utilise);
                }

            

                //------------------------- Rayon UBR -------------------------
                for(let i=0; i<tab_coord_ubr.length; i++){

                    var myIcon = L.icon({
                        iconUrl: chemin_racine+'/icons/wifi.png',
                        iconSize: [25, 25],
                        iconAnchor: [10, 5],
                        popupAnchor: [3, 0],
                    });

                    var marker = L.marker([tab_coord_ubr[i].lat, tab_coord_ubr[i].lon], { icon: myIcon });

                    marker.bindPopup( "<strong>UBR</strong><br>lat: "+tab_coord_ubr[i].lat+"<br>lon: "+tab_coord_ubr[i].lon+"<br>rayon: "+tab_coord_ubr[i].r_utilise+"<br>etat: "+tab_coord_ubr[i].etat ).addTo(cartographie);

                    var cercle = L.circle([tab_coord_ubr[i].lat, tab_coord_ubr[i].lon], {
                        color: 'green',
                        fillColor: 'green',
                        fillOpacity: 0.1,
                        radius: tab_coord_ubr[i].r_utilise,
                    }).addTo(cartographie);
                }
            }


        }//fin couverture antenne + wifi

    }

    document.getElementById("loader").style.display = "none"; //Retire l'icone de chargement

    let date2 = Date.now();
    console.log("FIN : "+date2);
    console.log("TEMPS MS : "+(date2-date1));
    console.log("TEMPS SEC : "+(date2-date1)/1000);

}//fin afficher_carte




/**
 * Permet de télécharger le fichier JSON qui contient : itineraire, dead_zone, couverture et polyline
*/
function telechargerJSON() {
    const nomFichier = 'donnees.json';

    const blob = new Blob([JSON.stringify(json_object, null, 2)], { type: 'application/json' });

    const url = window.URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.href = url;
    link.download = nomFichier;

    document.body.appendChild(link);

    link.click();

    window.URL.revokeObjectURL(url);
    document.body.removeChild(link);
}//fin telechargerJSON



/**
 * Chargement d'un fichier d'antennes
*/
async function loadFile(file) {
    if(file != null){

        let tab_coord = new Array();

        var markerClusters = L.markerClusterGroup();

        let text = await file.text();
        json_object_antenne = JSON.parse(text);


        for(let i=0; i<json_object_antenne.length; i++){
            tab_coord.push({lat: json_object_antenne[i]["lat"], lon: json_object_antenne[i]["lon"], dept: json_object_antenne[i]["dept"], sup_id: json_object_antenne[i]["sup_id"], operateur: json_object_antenne[i]["operateur"]});
        }


        for(let i=0; i<tab_coord.length; i++){
            tab_coord[i].lat = parseFloat(tab_coord[i].lat);
            tab_coord[i].lon = parseFloat(tab_coord[i].lon);
            tab_coord[i].dept = parseInt(tab_coord[i].dept);
            tab_coord[i].sup_id = parseInt(tab_coord[i].sup_id);
        }


        for(let i=0; i<tab_coord.length-1; i++){
            var marker = L.marker([tab_coord[i].lat, tab_coord[i].lon]);
            marker.bindPopup("<strong>Antenne</strong><br>sup_id: "+tab_coord[i].sup_id+"<br>lat: "+tab_coord[i].lat+"<br>lon: "+tab_coord[i].lon+"<br>operateur: "+tab_coord[i].operateur);
            markerClusters.addLayer(marker);
        }

        cartographie.addLayer(markerClusters);
    }
}//fin loadFile


/**
 * Chargement d'un fichier json dead zone
*/
async function loadFile2(file) {

    if(file != null){
        document.getElementById("loader").style.display = "block"; //Affiche l'icone de chargement
    
        let text = await file.text();

        resultat_json = text;
        json_object = JSON.parse(resultat_json);
        

        afficher_carte();
    }
}//fin loadFile2




/**
 * Fonction qui au clique d'un des labels change sa class pour changer le visuel
 * @param {*} id_cb id du checkbox cliqué
 * @author Eliot CALD
 */
function label_checkbox(id_cb){
    if(document.getElementById(id_cb).checked){
        document.getElementById('label_'+id_cb).classList = "btn btn-outline-warning label_titre";
    }
    else{
        document.getElementById('label_'+id_cb).classList ="btn btn-warning label_titre";
    }
}