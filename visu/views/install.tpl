% include('_begin.tpl', title='Accueil', page='home')

            <main>
                <div class="menu">
                    <h1><img title="" src="{{ get_url('static', filename='img/install.svg') }}" />Installation</h1>
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
                        <label for="provider">Fournisseur d'énergie&nbsp;: </label>
                        <select name="provider" id="provider">
                            % for provider in providers:
                                <option value="{{ provider["name"]}}">{{ provider["name"] }}</option>
                            % end
                        </select>
                    </p>

                    <p class="form-item">
                        <input type="submit" value="Installer"/>
                    </p>
                </form>
            </main>

% include('_end.tpl')
