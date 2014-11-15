% include('_begin.tpl', title='Settings', page='settings')

            <main>
                <div class="menu">
                    <h1><img alt="" src="{{ get_url('static', filename='img/target.svg') }}" />Configuration</h1>
                </div>

                <article id="user">
                    <form method="post" action="/settings">
                        % if defined('err'):
                        <div class="dialog-err">
                            <h4>{{ err['title'] }}</h4>
                            <p>
                                {{ err['content'] }}
                            </p>
                        </div>
                        % end

                        <h2>Utilisateur</h2>

                        <p class="form-item">
                            <label for="password">Mot de passe&nbsp;: </label>
                            <input type="password" name="password" id="password"/>
                        </p>
                        <p class="form-item">
                            <label for="password_confirm">Mot de passe (confirmation)&nbsp;: </label>
                            <input type="password" name="password_confirm" id="password_confirm"/>
                        </p>
                        <p class="form-help">
                            Laisser vide pour ne pas modifier le mot de passe.
                        </p>
                        <p>
                            <input type="submit" value="Sauvegarder"/>
                        </p>


                        <h2>Abonnement</h2>

                        <p class="form-item">
                            <label for="provider">Fournisseur d'énergie&nbsp;: </label>
                            <select name="provider" id="provider">
                                % for provider in providers:
                                    % if provider["current"]:
                                        % need_rate_info = provider["is_day_night_rate"]
                                    % end
                                    <option value="{{ provider["name"] }}" {{ 'selected' if provider["current"] else '' }} {{ 'class=need-rate-info' if provider["is_day_night_rate"] else '' }}>{{ provider["name"] }}</option>
                                % end
                            </select>
                        </p>

                        <div id="night-rate-info" style="display:{{ 'block' if need_rate_info else 'none' }}">
                            <p class="form-item">
                                <label for="start_night_rate">Début des heures creuses&nbsp;: </label>
                                <input type="time" name="start_night_rate" id="start_night_rate" value="{{ start_night_rate }}" placeholder="hh:mm"/>
                            </p>

                            <p class="form-item">
                                <label for="end_night_rate">Fin des heures creuses&nbsp;: </label>
                                <input type="time" name="end_night_rate" id="end_night_rate" value="{{ end_night_rate }}" placeholder="hh:mm"/>
                            </p>
                        </div>

                        <p>
                            <input type="submit" value="Sauvegarder"/>
                        </p>


                        <h2>Sécurité</h2>

                        <p class="form-item">
                            <label for="base_address">Adresse de la base&nbsp;: </label>
                            <input type="text" name="base_address" id="base_address" value="{{base_address}}"/>
                        </p>
                        <p class="form-help">
                            Par exemple <code>0xE056D446D0LL</code>.
                        </p>
                        <p class="form-item">
                            <label for="aes_key">Clé AES&nbsp;: </label>
                            <input type="int" name="aes_key" id="aes_key" value="{{aes_key}}"/>
                        </p>
                        <p class="form-help">
                            Par exemple <code>1-254-0-145-23-3-4-5-6-6-7-8-0-1-15-64</code>.
                        </p>
                        <p class="form-item">
                            <label for="nrf_power">Puissance du nRF&nbsp;: </label>
                            <select name="nrf_power" id="nrf_power">
                                <option value="min" {{! 'selected="selected"' if nrf_power is "min" else ''}}>Minimale</option>
                                <option value="low" {{! 'selected="selected"' if nrf_power is "low" else ''}}>Faible</option>
                                <option value="med" {{! 'selected="selected"' if nrf_power is "med" else ''}}>Moyenne</option>
                                <option value="high" {{! 'selected="selected"' if nrf_power is "high" or nrf_power not in ["min", "low", "med"] else ''}}>Haute</option>
                            </select>
                        </p>

                        <p>
                            <input type="submit" value="Sauvegarder"/>
                        </p>
                    </form>
                </article>

                <article id="sensors">
                    <h2>Capteurs</h2>

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
                </article>

                <article id="update">
                    <h2>Mise à jour</h2>

                    <p>
                        <a href="{{ get_url('update') }}">Mettre à jour le système</a>
                    </p>
                    <!--<p class="form-help">
                        La mise à jour est automatique. N'utilisez ce bouton que pour forcer la mise à jour.
                    </p>-->
                </article>

            </main>

% include('_end.tpl', scripts=['settings'])
