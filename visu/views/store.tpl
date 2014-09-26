% include('_begin.tpl', title='Store', page='store')

            <main>
                <div class="menu">
                    <h1><img alt="" src="{{ get_url('static', filename='img/store.svg') }}" />Store</h1>
                </div>
                <div class="coming-soon">
                	<img alt="" src="{{ get_url('static', filename='img/loading_simple.svg') }}" />
                	<span>À venir…</span>
                </div>
            </main>

% include('_end.tpl')
