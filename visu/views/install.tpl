% include('_begin.tpl', title='Accueil', page='home')

            <main>
                <h1>Installation</h1>
                <form action="" method="post">
                    <p>
                        <label for="login">Identifiant&nbsp;: </label>
                        <input type="text" name="login" id="login" value="{{login}}"/>
                    </p>

                    <p>
                        <label for="password">Mot de passe&nbsp;: </label>
                        <input type="password" name="password" id="password"/>
                    </p>

                    <p>
                        <label for="password_confirm">Confirmer le mot de passe&nbsp;: </label>
                        <input type="password" name="password_confirm" id="password_confirm"/>
                    </p>

                    <p>
                        <input type="submit" value="Installer"/>
                    </p>
                </form>
            </main>

% include('_end.tpl')
