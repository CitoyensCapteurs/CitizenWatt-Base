CitizenWatt-Base
================

This is the code running on the base (Raspberry Pi) for the CitizenWatt project. It receives incoming measures from the sensor and displays a web visualization to manage the measures.

## Installation

1. Write a Raspbian SD card.
2. Run the scripts in the `system` folder to install the necessary packages.
3. Init submodules with git submodule init` et `git submodule update`.
4. Run `make` to compile the `receive` program (needs extra librf24)
5. Use supervisord with the conf file in the `system` dir to handles the startup of the services.
6. (bis) Alternatively, launch `receive` (to actually receive the data), `process.py` (to receive the data from `receive` and store them in database) and the main script, `visu.py` which will serve the visualization.

## API documentation

This is a list of all the endpoints available in the API. You should authenticate yourself to use the API. For this purpose, use a POST request with `login` and `password` fields.

All the results are in a JSON dict, under the key `data`, for security purpose.

* `/api/sensors`
	* Returns all the available sensors with their associated measure types. If no sensors are found, returns `null`.

* `/api/sensors/<id:int>`
    * Returns all the infos for the specified sensor. If no matching sensor is found, returns `null`.

* `/api/types`
	* Returns all the available measure types. If no types are found, returns `null`.

* `/api/time`
    * Returns the current timestamp of the server.

* `/api/<sensor:int>/get/watts/by_id/<nb:int>`
    * Returns measure with id `<id1>` associated to sensor `<sensor>`, in watts.
    * If `<id1>` < 0, counts from the last measure, as in Python lists.
    * If no matching data is found, returns `null`.

* `/api/<sensor:int>/get/<watt_euros:watts|kwatthours|euros>/by_id/<nb1:int>/<nb2:int>`
    * Returns measures between ids `<id1>` and `<id2>` from sensor `<sensor>` in watts or euros.
    * If `<id1>` and `<id2>` are negative, counts from the end of the measures.
    * Depending on `<watt_euros>`:
        * If it is `watts`, returns the list of measures.
        * If it is `kwatthours`, returns the total energy for all the measures (dict).
        * If it is `euros`, returns the cost of all the measures (dict).
    * Returns measure in ASC order of timestamp.
    * Returns `null` if no measures were found.

* `/api/<sensor:int>/get/<[watt_euros:watts|kwatthours|euros>/by_id/<id1:int>/<id2:int>/<step:int>`
    * Returns all the measures of sensor `sensor` between ids `<id1>` and `<id2>`, grouped by `<step>`, as a list of the number of steps element.`<step>` should be positive.
    * Each item is `null` if no matching measures are found.
    * Depending on `<watt_euros>`:
        * If it is `watts`, returns the mean power for each group.
        * If it is `kwatthours`, returns the total energy for each group.
        * If it is `euros`, returns the cost of each group.
    * Returns measure in ASC order of timestamp.
    * Returns `null` if no measures were found.

* `/api/<sensor:int>/get/<watt_euros:watts|kwatthours|euros>/by_time/<time1:float>/<time2:float>`
    * Returns measures between timestamps `<time1>` and `<time2>` from sensor `<sensor>` in watts or euros.
    * Depending on `<watt_euros>`:
        * If it is `watts`, returns the list of measures.
        * If it is `kwatthours`, returns the total energy for all the measures (dict).
        * If it is `euros`, returns the cost of all the measures (dict).
    * Returns measure in ASC order of timestamp.
    * Returns `null` if no matching measures are found.

* `/api/<sensor:int>/get/<watt_euros:watts|kwatthours|euros>/by_time/<time1:float>/<time2:float>/<step:float>`
    * Returns all the measures of sensor `sensor` between timestamps `time1` and `time2`, grouped by step, as a list of the number of steps element.
    * Each item is `null` if no matching measures are found.
    * Depending on `<watt_euros>`:
        * If it is `watts`, returns the mean power for each group.
        * If it is `kwatthours`, returns the total energy for each group.
        * If it is `euros`, returns the cost of each group.
    * Returns measure in ASC order of timestamp.

* `/api/<sensor:int>/delete/by_id/<id1:int>`
    * Deletes measure with id `<id1>` associated to sensor `<sensor>`.
    * If `<id1> < 0`, counts from the last measure, as in Python lists.
    * If no matching data is found, returns `null`. Else, returns the number of deleted measures (1).

* `/api/<sensor:int>/delete/by_id/<id1:int>/<id2:int>`
    * Deletes measures between ids `<id1>` and `<id2>` from sensor `<sensor>`.
    * Returns `null` if no matching measures are found. Else, returns the number of deleted measures.

* `/api/<sensor:int>/delete/by_time/<time1:float>`
    * Deletes measure at timestamp `<time1>` for sensor `<sensor>`.
    * Returns null if no measure is found. Else, returns the number of deleted measures (1).

* `/api/<sensor:int>/delete/by_time/<time1:float>/<time2:float>`
    * Deletes measures between timestamps <time1> and <time2> from sensor <sensor>.
    * Returns null if no matching measures are found. Else, returns the number of deleted measures.

* `/api/<sensor:int>/insert/<value:float>/<timestamp:int>/<night_rate:int>`
    * Insert a measure with:
        * Timestamp `<timestamp>`
        * Value `<value>`
        * Tariff "day" if `<night_rate> == 0`, "night" otherwise.
    * Returns `True` if successful, `False` otherwise.

* `/api/energy_providers`
    * Returns all the available energy providers or `null` if none found.

* `/api/energy_providers/<id:current|int>`
    * Returns the current energy provider (if `id == "current"`), or the energy provider with the specified id.

* `/api/<energy_provider:current|int>/watt_to_euros/<tariff:night|day>/<consumption:float>`
    * Returns the cost in euros associated with a certain consumption, in kWh.
    * One should specify the tariff (night or day, day if no such distinction is to be done) and the id of the energy_provider.
    * Returns `null` if no valid result to return.



Code organisation
-----------------

*(to be translated)*


 * bottle.py : C'est la lib bottle utilisée pour servir l'interface
web sans avoir à faire tourner un serveur apache. Pas touche au
fichier. C'est du MVC classique, si vous connaissez.

http://bottlepy.org/

 * bottle_sqlalchemy.py : Ça aussi c'est une lib, un ORM pour faire
l'intermédiaire avec la base de données PostgreSQL en ne manipulant
que des objets idiomatiques en Python plutôt que des requêtes SQL
brutes (évite les injections, les erreurs de construction de requête,
simplifie la vie).

https://github.com/iurisilvio/bottle-sqlalchemy

* bottlesession.py : Encore une lib pour ajouter à bottle la gestion
des session http (pour gérer la connexion à l'interface, car elle est
protégée pr un mot de passe).

https://github.com/linsomniac/bottlesession

* process.py : Enregistre les données en provenance du capteur dans la
base de données. La communication bas-niveau se fait via le code
`receive.cpp` qui envoie ensuite les donnée à `process.py` en
utilisant un « named pipe » d'Unix. La raison pour laquelle on s'est
organisé comme ça est que cela permet de faire tout ce qui est
manipulation de la base de données en Python seulement, et donc
d'utiliser le même module (`libcitizenwatt/database.py`). Ça évite la
duplication de code et permet de n'avoir qu'un seul endroit où faire
les modifs si on veut changer le schéma de la base.

* receive.cpp : Comme dit ci-dessus, ce fichier dialogue avec le NRF
(la lib était dispo en C++ mais pas en Python et on n'a pas fait de
binding pour Python). Ce fichier ne fait vraiment que ça, il ne
déchiffre pas les messages (qui sont chiffrés en AES). C'est
`process.py` qui s'en charge.

* requirements.txt : Ça c'est assez pédestre (en fait je découvre à
l'instant ce fichier), mais ça permet de garder une trace des
dépendances.

* updater.sh : Script lancé lors des mises à jour. Maintenant, il
s'agit essentiellement d'un apt-get update.

* visu.py : C'est le serveur de l'interface. Un fichier bien trop long
à mon avis puisqu'il contient à lui seul tout le code, mais Lucas aime
bien les fichiers longs… Enfin on l'a pas encore découpé disons, mais
faudrait qu'on le fasse. L'idée générale est assez simple et tous les
blocs sont construits de la même façon, utilisant le mécanisme de
bottle. Par exemple :

```
@app.route("/settings",           # Route gérée par cette fonction
           name="settings",       # Nom de la route, pour la
référencer depuis la vue
           template="settings",   # Nom de la vue à utiliser
           apply=valid_user(),    # Restriction d'accès (il faut être connecté)
           method="post")         # Méthode HTTP à gérer (GET ou POST
en général)
def settings_post(db):
    # [...] (Traite la requête)
    # Si on veut rediriger sur une autre page
    redirect("/settings")
    # Si on veut rendre la vue et y lier des variables
    return {"foo": "bar"} # La variable "foo" sera utilisable dans la vue
```

Les noms des vues sont relatives au dossier `views/` et les fichiers
correspondant doivent comporter l'extension `.tpl`.

Le code des vues est essentiellement du HTML dans lequel on peut
afficher des variables avec `{{ foo }}`. Il y a aussi des spécificités
pour les liens, pour pouvoir changer les routes sans modifier tous les
liens du code. Le plus simple est de regarder un lien de de s'en
inspirer.

Plus de doc sur le format de templating : http://bottlepy.org/docs/dev/stpl.html

 * views/ : Dossier contenant toutes les vues.

    * views/_begin.tpl : Début de toutes les pages de template.

Appelée depuis les autres templates avec la commande `%
include('_begin.tpl', title='Community', page='community')` où `title`
est la titre de la page et `page` est utilisé pour l'apparence des
menus (enfin en lisant le code de `_begin.tpl`, ça se comprend assez
vite.

    * views/_end.tpl : Idem, mais pour la fin.

Appelée avec `% include('_end.tpl')` ou alors `% include('_end.tpl',
scripts=['foo', 'bar'])` pour inclure des scripts (cf `conso.tpl` par
exemple).

Les autres fichiers tpl se comprennent bien : ils sont assez courts et
c'est juste du HTML augmenté.

 * static/ : Ce sont les fichiers statiques servis par la visu (css,
js, images, fontes).

    * static/css/normalize.css : Permet d'harmoniser le comportement
des différents navigateurs. Ne pas modifier.

    * static/css/style.css : Contient tout le style de l'interface. Il
faudra peut-être songer à le découper, mais c'est jamais évident à
découper un fichier css.

    * static/img/ : Images utilisées dans l'interface. Notez qu'elles
sont toutes en SVG donc redimensionnables à souhait et faciles à
modifier en utilisant Inkscape. Si vous avez besoin d'images en
particulier, dite-moi.

    * static/js/ : On n'utilise aucune lib JS externe, mais si vous
voulez en ajouter (jQuery, D3JS, etc.) mettez-les dans un dossier
`lib/`.

       * static/js/conso/ : Tous les fichiers utilisés pour la page de
conso. C'est développé en utilisant le modèle des Black Boxes
(https://hacks.mozilla.org/2014/08/black-box-driven-development-in-javascript/)
et chaque fichier dont le nom commence par une majuscule correspond à
la définition d'une de ces BBs.

          * static/js/conso/App.js : Point d'entrée du code de la
visu. Initialise le graphe (`init`), récupère les premières données
(`initValues`), met à jour si on est en visu instantanée (`update`)

          * static/js/conso/Config.js : Comme son nom l'indique, juste
quelques variables de config.

          * static/js/conso/DataProvider.js : Module de récupération
des données via l'API. L'intégralité de la dépendance du code aux
routes de l'API doit être contenue dans cette BB. C'est-à-dire que si
l'API change, seul ce fichier doit être modifié.

          * static/js/conso/Graph.js : Gère l'affichage du graphe.
Fichier un peu lourd… `addRect` ajoute un nouveau batton à
l'histogramme. `setOverview` modifie la valeur affichée au-dessus du
graphe. etc. Le rôle de chaque fonction est résumé dans le code.

          * static/js/conso/HashManager.js : Gère la route côté client
(après le # de l'URL) pour permettre de recharger la page sans revenir
à la vue par défaut.

          * static/js/conso/Menu.js : Gère les boutons de navigation
sous le graphe et donc l'unité d'affichage et l'échelle.

          * static/js/conso/RateDisplay.js : Gère l'affichage du petit
soleil/la petite lune dans la barre de navigation en fonction de
l'horaire (horaire de jour ou horaire de nuit).

          * static/js/conso/tail.js : Crée l'objet App au chargement de la page.

       * static/js/conso/dateutils.js : Fournit des fonctions
utilitaires de gestion du temps non disponibles dans l'API Date() de
JavaScript.

       * static/js/conso/settings.js : Code js utilisé par la page de
configuration.

       * static/js/conso/target.js : Code qui était utilisé par la
page « Objectifs » à l'apoque où elle existait. Je supprime.

       * static/js/conso/utils.js : Le vrac de ce qui reste. En
l'occurrence, juste une fonction qui crée une chaine base64 aléatoire.

 * libcitizenwatt/ : Modules python propres à CitizenWatt

    * libcitizenwatt/cache.py : Gère le cache pour les requêtes. C'est
là, et uniquement là, qu'intervient Redis pour le moment.

    * libcitizenwatt/config.py : Gère le chargement et la création du
fichier de configuration.

    * libcitizenwatt/database.py : Déclare et manipule la base de
données PostgreSQL

    * libcitizenwatt/tools.py : Fonctions utilitaires en vrac.

 * RF24/ : le dossier est vide => La lib RF24 (le pilote du NRF en
gros) est gérée par les dépôts maintenant. Il faudrait supprimer ce
dossier.


