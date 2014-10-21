% include('_begin.tpl', title='Consommation', page='conso')

            <main>
                <div class="menu">
                    <h1><img alt="" src="{{ get_url('static', filename='img/data.svg') }}" />Consommation</h1>
                </div>
                <div id="overview">
                    <div>
                        <p id="now" class="blurry red">&nbsp;</p>
                        <p id="now_label">Consommation actuelle</p>
                    </div>
                </div>


                <div id="graph">
                    <button id="prev">&lt;</button>
                    <div id="graph_loading">
                        <img alt="Chargement" src="{{ get_url('static', filename='img/loading_simple.svg') }}" />
                    </div>
                    <div id="graph_values_wrapper">
                        <div id="graph_values"></div>
                    </div>
                    <div id="graph_vertical_axis"></div>
                    <hr style="bottom:33.3%"/>
                    <hr style="bottom:66.7%"/>
                    <button id="next">&gt;</button>
                </div>


                <nav id="scale">
                    <button id="scale-now" class="active">Maintenant</button>
                    <button id="scale-day">Aujourd'hui</button>
                    <button id="scale-week">Cette semaine</button>
                    <button id="scale-month">Ce mois</button>
                    <button id="unit-energy" class="active">Watts</button>
                    <button id="unit-price">Euros</button>
                </nav>

                <button style="display: none" id="update-toggle">Start/Stop update</button>

                <p style="text-align: center;">{{ provider }}</p>
            </main>

<%
    scripts = [
        'utils',
        'dateutils',
        'conso/Menu',
        'conso/Graph',
        'conso/DataProvider',
        'conso/RateDisplay',
        'conso/HashManager',
        'conso/App',
        'conso/Config',
        'conso/tail'
    ]
    include('_end.tpl', scripts=scripts)
%>

