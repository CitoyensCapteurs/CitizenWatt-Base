% include('_begin.tpl', title='Guide', page='help')

            <main>
            	<div class="menu">
                    <h1><img alt="" src="{{ get_url('static', filename='img/faq_big.svg') }}" />Questions fréquentes</h1>
                </div>
                % for q,a in faq:
                <h2>{{ q }}</h2>
                <p>
                	{{ a }}
                </p>
                % end
            </main>

% include('_end.tpl')
