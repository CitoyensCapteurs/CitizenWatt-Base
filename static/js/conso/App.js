var HashManager = function() {
	var api = {};
	var unit, mode;

	components = location.hash.slice(1).split('-');
	unit = components[0];
	mode = components[1] || 'now';

	api.updateHash= function(){
		location.hash = '#' + unit + '-' + mode;
	};

	api.setUnit = function(new_unit) {
		unit = new_unit;
		api.updateHash();
	};

	api.getUnit = function() {
		return unit;
	};

	api.setMode = function(new_mode) {
		mode = new_mode;
		api.updateHash();
	};

	api.getMode = function() {
		return mode;
	};

	return api;
};

/**
 * Core application
 */
var App = function() {
	var api = {};
	var graph = Graph()
	  , provider = DataProvider()
	  , menu = Menu()
	  , hash = HashManager()
	  , rate = RateDisplay()
	  ;

	menu.onunitchange = function(unit, callback) {
		graph.clean();
		if (unit == 'price') {
			graph = PriceGraph();
			hash.setUnit('euros');
		} else {
			graph = Graph(menu.getMode() == 'now' ? 'W' : 'kWh');
			hash.setUnit('watt');
		}
		graph.init();
		api.initValues(callback);
	};

	menu.onmodechange = function(mode, callback) {
		graph.clean();
		graph = hash.getUnit() == 'watt' ? Graph(menu.getMode() == 'now' ? 'W' : 'kWh') : PriceGraph();
		graph.autoremove = mode == 'now';
		graph.init();
		hash.setMode(mode);
		api.initValues(callback);
	};

	provider.onratechange = rate.setRate;

	/**
	 * Callbacks
	 */
	api.oninit = function(){}; // called when init is done

	/**
	 * Init application.
	 * Add graduation lines
	 */
	api.init = function() {
		menu.init();

		provider.get('/time', function(basetime) {
			dateutils.offset = parseFloat(basetime) * 1000.0 - (new Date()).getTime();

			switch (hash.getUnit()) {
				case 'euros':
					graph = PriceGraph();
					menu.setUnit('price', function(){
						menu.setMode(hash.getMode(), api.oninit);
					});
					break;

				default:
					menu.setUnit('energy', function(){
						menu.setMode(hash.getMode(), api.oninit);
					});
			}

		});
	};

	/**
	 * Init graph values.
	 * @param callback: (optional)
	 */
	api.initValues = function(callback) {
		var target = '/1/get/' + menu.getUnitString();
		var mode = menu.getMode();

		switch (mode) {
			case 'now':
				target
				+= '/by_id/'
				+  (-graph.getWidth()-1).toString() + '/'
				+  '0/1';
				graph.setOverviewLabel('Consommation actuelle');
				break;

			case 'day':
				target
				+= '/by_time/'
				+  (dateutils.getDayStart() / 1000.0 - 86400) + '/'
				+  (dateutils.getDayEnd() / 1000.0 - 86400) + '/'
				+  dateutils.getHourLength() / 1000.0;
				graph.setOverviewLabel('Consommation aujourd\'hui');
				break;

			case 'week':
				target
				+= '/by_time/'
				+  dateutils.getWeekStart() / 1000.0 + '/'
				+  dateutils.getWeekEnd() / 1000.0 + '/'
				+  dateutils.getDayLength() / 1000.0;
				graph.setOverviewLabel('Consommation cette semaine');
				break;

			case 'month':
				target
				+= '/by_time/'
				+  dateutils.getMonthStart() / 1000.0 + '/'
				+  dateutils.getMonthEnd() / 1000.0 + '/'
				+  dateutils.getDayLength() / 1000.0;
				graph.setOverviewLabel('Consommation ce mois');
				break;

			default:
				if (callback) callback();
				return;
		}

		provider.get(target, function(data) {
			graph.startLoading();
			graph.rect_width = graph.getPixelWidth() / data.length - graph.rect_margin;
			var s = 0;
			data.map(function(m) {
				if (m.value !== undefined) {
					graph.addRect(m.value, false);
					s += m.value;
				} else {
					graph.addRect(0, false);
				}
			});
			if (mode != 'now') graph.setOverview(s);
			graph.stopLoading();
			if (callback) callback();
		});

		graph.last_call = Date.now() / 1000.0;
	};

	/**
	 * Go and get new values. This function should be called regularely by the main loop.
	 */
	api.update = function() {
		if (menu.getMode() == 'now') {
			var target
			= '/1/get/'
			+ menu.getUnitString()
			+ '/by_time/'
			+ graph.last_call + '/'
			+ (graph.last_call = Date.now() / 1000.0) + '/'
			+ Config.timestep;

			provider.get(target, function(data) {
				data.map(function(m) {
					if (m.value !== undefined) {
						graph.addRect(m.value);
						graph.setOverview(m.value);
					}
				});
			});
		}
	};

	return api;
};
