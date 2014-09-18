% include('_begin.tpl', title='Objectifs', page='target')

            <main>
                <div class="menu">
                    <h1><img alt="" src="{{ get_url('static', filename='img/target.svg') }}" />Objectifs</h1>
                    <div id="target-ok">
                        <a href="">
                            <img alt="[Fait]" src="{{ get_url('static', filename='img/target-ok.svg') }}" />Objectif achevé
                        </a>
                    </div>
                    <div id="target-wip">
                        <a href="">
                            <img alt="[En cours]" src="{{ get_url('static', filename='img/target-wip.svg') }}" />Objectif en cours
                        </a>
                    </div>
                    <div id="target-no">
                        <a href="">
                            <img alt="[Non fait]" src="{{ get_url('static', filename='img/target-no.svg') }}" />Objectif non commencé
                        </a>
                    </div>
                    <div id="target-more">
                        <a href="">
                            <img alt="Plus" src="{{ get_url('static', filename='img/more.svg') }}" />
                        </a>
                    </div>
                </div>
            </main>

% include('_end.tpl', script='target')
