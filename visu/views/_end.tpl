
            <footer>
                <p>Licence GNU GPL | <a href="http://citoyenscapteurs.net/">Citoyens Capteurs</a></p>
            </footer>
        </div>

        <script type="text/javascript">
            // Constants set on the server side
            var API_URL = '{{ API_URL }}api';
        </script>
        % if defined('script'):
        <script src="{{ get_url('static', filename='js/' + script + '.js') }}"></script>
        % end
    </body>
</html>
