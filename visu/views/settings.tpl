% include('_begin.tpl', title='Settings', page='settings')

            <main>
                <div class="menu">
                    <h1><img alt="" src="{{ get_url('static', filename='img/target.svg') }}" />Configuration</h1>

                    <form method="post" action="/settings">
                        <fieldset id="user">
                            <legend>Utilisateur</legend>
                            <p><label for="password">Mot de passe&nbsp;: </label><input type="password" name="password" id="password"/></p>
                            <p><label for="password_confirm">Mot de passe (confirmation)&nbsp;: </label><input type="password_confirm" name="password_confirm" id="password_confirm"/></p>
                            <p><input type="submit" value="Sauver"/></p>
                        </fieldset>
                        <fieldset id="sensors">
                            <legend>Capteurs</legend>

                            % if len(sensors) > 0:
                                <table>
                                    <tr>
                                        <th>Nom</th>
                                        <th>Type</th>
                                    </tr>
                                % for sensor in sensors:
                                    <tr>
                                        <td>{{ sensor["name"] }}</td>
                                        <td>{{ sensor["type"] }}</td>
                                    </tr>
                                % end
                                </table>
                            % else:
                                <p>Aucun capteur disponible.</p>
                            % end
                        </fieldset>
                    </form>
                </div>
            </main>

% include('_end.tpl', script='settings')
