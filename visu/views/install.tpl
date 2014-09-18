% include('_begin.tpl', title='Accueil', page='home')

            <main>
                <div class="menu">
                    <h1><img title="" src="{{ get_url('static', filename='img/install.svg') }}" />Installation</h1>
                </div>
                <form action="" method="post">
                    <p class="form-item">
                        <label for="login">Identifiant&nbsp;: </label>
                        <input type="text" name="login" id="login" value="{{login}}"/>
                    </p>

                    <p class="form-item">
                        <label for="password">Mot de passe&nbsp;: </label>
                        <input type="password" name="password" id="password"/>
                    </p>

                    <p class="form-item">
                        <label for="password_confirm">Confirmer le mot de passe&nbsp;: </label>
                        <input type="password" name="password_confirm" id="password_confirm"/>
                    </p>

                    <p class="form-item">
                        <input type="submit" value="Installer"/>
                    </p>
                </form>
            </main>

% include('_end.tpl')
