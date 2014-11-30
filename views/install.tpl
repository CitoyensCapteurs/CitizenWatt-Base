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

                    <h2>Utilisateur</h2>

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
                            <option value="min" {{! 'selected="selected"' if nrf_power == "min" else ''}}>Minimale</option>
                            <option value="low" {{! 'selected="selected"' if nrf_power == "low" else ''}}>Faible</option>
                            <option value="med" {{! 'selected="selected"' if nrf_power == "med" else ''}}>Moyenne</option>
                            <option value="high" {{! 'selected="selected"' if nrf_power == "high" else ''}}>Haute</option>
                        </select>
                    </p>

                    <p class="form-item">
                        <label for="nrf_speed">Vitesse du nRF&nbsp;: </label>
                        <select name="nrf_speed" id="nrf_speed">
                            <option value="250k" {{! 'selected="selected"' if nrf_speed is "250k" else ''}}>Lent (plus fiable)</option>
                            <option value="1M" {{! 'selected="selected"' if nrf_speed is "1M" else ''}}>Normal</option>
                            <option value="2M" {{! 'selected="selected"' if nrf_speed is "2M" else ''}}>Rapide (peu fiable)</option>
                        </select>
                    </p>

                    <p class="form-item">
                        <input type="submit" value="Installer"/>
                    </p>
                </form>
            </main>

% include('_end.tpl')
