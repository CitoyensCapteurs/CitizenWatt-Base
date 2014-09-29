% include('_begin.tpl', title='Accueil', page='home')

            <main>
                <div class="menu">
                    <h1><img alt="" src="{{ get_url('static', filename='img/login.svg') }}" />Connexion</h1>
                </div>
                <form action="" method="post">
                    % if defined('err'):
                    <div class="dialog-err">
                        <h4>{{ err['title'] }}</h4>
                        <p>
                            {{ err['content'] }}
                        </p>
                    </div>
                    % end
                    <p class="form-item">
                        <label for="login">Identifiant&nbsp;: </label>
                        <input type="text" name="login" id="login" value="{{login}}" autofocus/>
                    </p>

                    <p class="form-item">
                        <label for="password">Mot de passe&nbsp;: </label>
                        <input type="password" name="password" id="password"/>
                    </p>

                    <p class="form-item">
                        <input type="submit" value="Connexion"/>
                    </p>
                </form>
            </main>

% include('_end.tpl')
