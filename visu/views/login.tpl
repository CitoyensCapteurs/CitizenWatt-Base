% include('_begin.tpl', title='Accueil', page='home')

            <main>
                <h1>Connexion</h1>
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
                        <input type="submit" value="Connexion"/>
                    </p>
                </form>
            </main>

% include('_end.tpl')
