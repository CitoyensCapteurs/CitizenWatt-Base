<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <title>CitizenWatt — {{ title }}</title>
        <link rel="stylesheet" href="{{ get_url('static', filename='css/normalize.css') }}">
        <link rel="stylesheet" href="{{ get_url('static', filename='css/style.css') }}">
    </head>

    <body>
        <div id="page">
            <header>
                <a href="{{ get_url('index') }}"><img src="{{ get_url('static', filename='img/logo.png') }}" alt="Logo CitizenWatt"/></a>

                % if valid_session():
                    <nav id="menu">
                        <a {{ !'class="active"' if page=='home' else '' }} href="{{ get_url('index') }}">Accueil</a>
                        <a {{ !'class="active"' if page=='conso' else '' }} href="{{ get_url('conso') }}">Conso</a>
                        <a {{ !'class="active"' if page=='settings' else '' }} href="{{ get_url('settings') }}">Config</a>
                        <a {{ !'class="active"' if page=='help' else '' }} href="{{ get_url('help') }}">Guide</a>
                        <a {{ !'class="active"' if page=='results' else '' }} href="{{ get_url('results') }}">Bilan</a>
                        <a href="{{ get_url('logout') }}">Déconnexion</a>
                    </nav>
                % end
            </header>
