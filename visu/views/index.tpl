% include('_begin.tpl', title='Accueil', page='home')

            <main>
                <div class="left-column">
                    <div class="menu">
                        <h1><a href="{{ get_url('conso') }}"><img alt="" src="{{ get_url('static', filename='img/data.svg') }}" />Consommation</a></h1>
                        <a href="{{ get_url('conso') }}">
                            <img alt="" src="{{ get_url('static', filename='img/small-data.svg') }}" />En cours
                        </a>
                        <a href="{{ get_url('conso') }}">
                            <img alt="" src="{{ get_url('static', filename='img/month.svg') }}" />Par mois
                        </a>
                        <a href="{{ get_url('conso') }}">
                            <img alt="More" src="{{ get_url('static', filename='img/more.svg') }}" />
                        </a>
                    </div>

                    <div class="menu">
                        <h1><a href="{{get_url('target') }}"><img alt="" src="{{ get_url('static', filename='img/target.svg') }}" />Objectifs</a></h1>
                        <a href="{{ get_url('target') }}#ok">
                            <img alt="" src="{{ get_url('static', filename='img/tick.svg') }}" />Atteints
                        </a>
                        <a href="{{ get_url('target') }}#wip">
                            <img alt="" src="{{ get_url('static', filename='img/loading.svg') }}" />En cours
                        </a>
                        <a href="{{ get_url('target') }}">
                            <img alt="More" src="{{ get_url('static', filename='img/more.svg') }}" />
                        </a>
                    </div>
                </div>

                <div class="right-column">
                    <div class="menu">
                        <h1><a href="{{ get_url('help') }}"><img alt="" src="{{ get_url('static', filename='img/help.svg') }}" />Guide</a></h1>
                        <a href="http://wiki.citizenwatt.paris">
                            <img alt="" src="{{ get_url('static', filename='img/wiki.svg') }}" />Wiki
                        </a>
                        <a href="{{ get_url('help') }}#contact">
                            <img alt="" src="{{ get_url('static', filename='img/contact.svg') }}" />Contact
                        </a>
                        <a href="{{ get_url('help') }}">
                            <img alt="More" src="{{ get_url('static', filename='img/more.svg') }}" />
                        </a>
                    </div>

                    <div class="menu">
                        <h1><a href="{{ get_url('results') }}"><img alt="" src="{{ get_url('static', filename='img/results.svg') }}" />Bilan</a></h1>
                        <a href="{{ get_url('results') }}">
                            <img alt="" src="{{ get_url('static', filename='img/bill.svg') }}" />Estimation de facture
                        </a>
                        <a href="{{ get_url('results') }}">
                            <img alt="" src="{{ get_url('static', filename='img/progress.svg') }}" />Progrès
                        </a>
                        <a href="{{ get_url('results') }}">
                            <img alt="More" src="{{ get_url('static', filename='img/more.svg') }}" />
                        </a>
                    </div>
                </div>
            </main>

% include('_end.tpl')
