% include('_begin.tpl', title='Settings', page='settings')

            <main>
                <div class="menu">
                    <h1><img alt="" src="{{ get_url('static', filename='img/target.svg') }}" />Configuration</h1>
                </div>

                <form method="post" action="/settings">
                    <fieldset id="user">
                        <legend>Utilisateur</legend>
                        <p class="form-item"><label for="password">Mot de passe&nbsp;: </label><input type="password" name="password" id="password"/></p>
                        <p class="form-item"><label for="password_confirm">Mot de passe (confirmation)&nbsp;: </label><input type="password" name="password_confirm" id="password_confirm"/></p>
                        <p class="form-help">Laisser vide pour ne pas modifier le mot de passe.</p>

                        <p class="form-item">
                            <label for="provider">Fournisseur d'énergie&nbsp;: </label>
                            <select name="provider" id="provider">
                                % for provider in providers:
                                    <option value="{{ provider["name"] }}">{{ provider["name"] }}</option>
                                % end
                            </select>
                        </p>

                        <p class="form-item">
                            <label for="base_address">Adresse de la base&nbsp;: </label>
                            <input type="text" name="base_address" id="base_address" value="{{base_address}}"/>
                        </p>
                        <p>Par exemple <code>0xE056D446D0LL</code>.</p>
                        <p class="form-item">
                            <label for="aes_key">Clé AES&nbsp;: </label>
                            <input type="int" name="aes_key" id="aes_key" value="{{aes_key}}"/>
                        </p>
                        <p>Par exemple <code>1, 254, 0, 145, 23, 3, 4, 5, 6, 6, 7, 8, 0, 1, 15, 64</code>.</p>


                        <p class="form-item">
                            <label for="start_night_rate">Début des heures creuses&nbsp;: </label>
                            <input type="time" name="start_night_rate" id="start_night_rate" value="{{ start_night_rate }}" placeholder="hh:mm"/>
                        </p>

                        <p class="form-item">
                            <label for="end_night_rate">Fin des heures creuses&nbsp;: </label>
                            <input type="time" name="end_night_rate" id="end_night_rate" value="{{ end_night_rate }}" placeholder="hh:mm"/>
                        </p>

                        <p><input type="submit" value="Sauver"/></p>
                    </fieldset>
                    <fieldset id="sensors">
                        <legend>Capteurs</legend>

                        % if len(sensors) > 0:
                            <table>
                                <tr>
                                    <th>Nom</th>
                                    <th>Type</th>
                                    <th>Appairer</th>
                                </tr>
                            % for sensor in sensors:
                                <tr>
                                    <td>{{ sensor["name"] }}</td>
                                    <td>{{ sensor["type"] }}</td>
                                    <td><a href="/reset_timer/{{ sensor["id"] }}">Appairer</a></td>
                                </tr>
                            % end
                            </table>
                        % else:
                            <p>Aucun capteur disponible.</p>
                        % end
                    </fieldset>
                </form>

            </main>

% include('_end.tpl', scripts=['settings'])
