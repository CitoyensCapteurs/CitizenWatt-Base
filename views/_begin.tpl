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
                <a href="{{ get_url('index') }}" class="header-logo">
                    <img src="{{ get_url('static', filename='img/logo.png') }}" alt="Logo CitizenWatt"/>
                </a>
                <div id="rate-logo-day" class="rate-logo">
                    <img src="{{ get_url('static', filename='img/sun.svg') }}" alt="Tarif de jour"/>
                    <span>Tarif de jour</span>
                </div>
                <div id="rate-logo-night" class="rate-logo">
                    <img src="{{ get_url('static', filename='img/moon.svg') }}" alt="Tarif de nuit"/>
                    <span>Tarif de nuit</span>
                </div>

                % if valid_session():
                    <nav id="menu">
                        <a {{ !'class="active"' if page=='home' else '' }} href="{{ get_url('index') }}">Accueil</a>
                        <a {{ !'class="active"' if page=='conso' else '' }} href="{{ get_url('conso') }}">Conso</a>
                        <a {{ !'class="active"' if page=='settings' else '' }} href="{{ get_url('settings') }}">Config</a>
                        <a {{ !'class="active"' if page=='help' else '' }} href="{{ get_url('help') }}">Guide</a>
                        <a {{ !'class="active"' if page=='community' else '' }} href="{{ get_url('community') }}">Communauté</a>
                    </nav>
                % end
            </header>
