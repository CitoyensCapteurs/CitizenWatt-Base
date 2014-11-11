% include('_begin.tpl', title='Guide', page='help')

            <main>
                <div class="menu">
                    <h1><img alt="" src="{{ get_url('static', filename='img/help.svg') }}" />Guide</h1>
                </div>
                <div class="menu">
                    <a href="{{ get_url('faq') }}">
                        <img alt="" src="{{ get_url('static', filename='img/faq.svg') }}" />Questions fréquentes
                    </a>
                </div>
                <div class="content">
                    <p>
                        Les <a href="{{ get_url('faq') }}">questions fréquentes</a> donnent des réponses aux questions que vous êtes le plus suceptible de vous poser à propos de CitizenWatt.
                    </p>
                </div>
                <div class="menu">
                    <a href="http://wiki.citizenwatt.paris">
                        <img alt="" src="{{ get_url('static', filename='img/wiki.svg') }}" />Wiki
                    </a>
                </div>
                <div class="content">
                    <p>
                        Le <a href="http://wiki.citizenwatt.paris">wiki de CitizenWatt</a> regroupe toutes les informations dont vous pourriez avoir besoin pour utiliser cette interface, mais aussi les réponses à des questions sur le projet en général.
                    </p>
                </div>
                <div class="menu">
                    <a href="{{ get_url('help') }}#contact" id="contact">
                        <img alt="" src="{{ get_url('static', filename='img/contact.svg') }}" />Contact
                    </a>
                </div>
                <div class="content">
                    <p>
                        Vous pouvez contacter l'équipe de CitizenWatt à l'adresse <a href="mailto:contact@citizenwatt.paris">contact@citizenwatt.paris</a>.
                    </p>
                    <p>
                        Vous pouvez également utiliser <a href="http://www.citizenwatt.paris/#eight">ce formulaire</a>.
                    </p>
                </div>
            </main>

% include('_end.tpl')
