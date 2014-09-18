<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <title>CitizenWatt</title>
        <link rel="stylesheet" href="{{ get_url('static', filename='css/normalize.css') }}">
        <link rel="stylesheet" href="{{ get_url('static', filename='css/style.css') }}">
    </head>

    <body>
        <div id="page">
            <header>
                <a href="index.html"><img src="{{ get_url('static', filename='img/logo.png') }}" alt="Logo CitizenWatt"/></a>

                <div id="menu">
                    <ul>
                        <li><a href="index.html">Accueil</a></li>
                        <li><a href="">Ma conso</a></li>
                        <li><a href="">Archives</a></li>
                        <li><a href="">Guides</a></li>
                        <li><a href="">À propos</a></li>
                    </ul>
                </div>
            </header>

            <main>
                <div class="left-column">
                    <div class="menu">
                        <h1><img alt="" src="{{ get_url('static', filename='img/data.svg') }}" />Données</h1>
                        <a href="{{ get_url('conso') }}">
                            <img alt="" src="{{ get_url('static', filename='img/small-data.svg') }}" />En cours
                        </a>
                        <a href=""><img alt="" src="{{ get_url('static', filename='img/month.svg') }}" />Par mois</a>
                        <a href=""><img alt="More" src="{{ get_url('static', filename='img/more.svg') }}" /></a>
                    </div>

                    <div class="menu">
                        <h1><img alt="" src="{{ get_url('static', filename='img/target.svg') }}" />Objectifs</h1>
                        <a href=""><img alt="" src="{{ get_url('static', filename='img/tick.svg') }}" />Atteints</a>
                        <a href=""><img alt="" src="{{ get_url('static', filename='img/loading.svg') }}" />En cours</a>
                        <a href=""><img alt="More" src="{{ get_url('static', filename='img/more.svg') }}" /></a>
                    </div>
                </div>

                <div class="right-column">
                    <div class="menu">
                        <h1><img alt="" src="{{ get_url('static', filename='img/help.svg') }}" />Aide</h1>
                        <a href=""><img alt="" src="{{ get_url('static', filename='img/wiki.svg') }}" />Wiki</a>
                        <a href=""><img alt="" src="{{ get_url('static', filename='img/contact.svg') }}" />Contact</a>
                        <a href=""><img alt="More" src="{{ get_url('static', filename='img/more.svg') }}" /></a>
                    </div>

                    <div class="menu">
                        <h1><img alt="" src="{{ get_url('static', filename='img/results.svg') }}" />Bilan</h1>
                        <a href=""><img alt="" src="{{ get_url('static', filename='img/bill.svg') }}" />Estimation de facture</a>
                        <a href=""><img alt="" src="{{ get_url('static', filename='img/progress.svg') }}" />Progrès</a>
                        <a href=""><img alt="More" src="{{ get_url('static', filename='img/more.svg') }}" /></a>
                    </div>
                </div>
            </main>

            <footer>
                <p>Licence GNU GPL | <a href="http://citoyenscapteurs.net/">Citoyens Capteurs</a></p>
            </footer>
        </div>
    </body>
</html>

