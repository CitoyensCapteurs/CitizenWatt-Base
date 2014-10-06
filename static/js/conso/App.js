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

	function reload(_, callback) {
		mode = menu.getMode();
		date = menu.getDate();
		graph.clean();
		graph = hash.getUnit() == 'watt' ? Graph(mode == 'now' ? 'W' : 'kWh') : PriceGraph();
		graph.autoremove = mode == 'now' && date === null;
		if (mode == 'now') graph.round = function(v) { return Math.round(v * 10000) / 10000; };
		graph.init();
		hash.setMode(mode);
		hash.setDate(date);
		api.initValues(callback);
	}

	menu.onmodechange = function(ev, calback) {
		menu.setDate(null);
		reload(ev, callback);
	}
	menu.ondatechange = reload;

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

			var unit;
			switch (hash.getUnit()) {
				case 'euros':
					graph = PriceGraph();
					unit = 'price';
					break;

				default:
					unit = 'energy'
			}

			menu.setUnit('price', function(){
			menu.setMode(hash.getMode(), function(){
			menu.setDate(hash.getDate(), function(){
				reload(null, api.oninit);
			}, false);
			}, false);
			});

		});
	};

	/**
	 * Init graph values.
	 * @param callback: (optional)
	 */
	api.initValues = function(callback) {
		var target = '/1/get/' + menu.getUnitString();
		var mode = menu.getMode();
		var date = menu.getDate() || (new Date());

		switch (mode) {
			case 'now':
				menu.timeWidth = Config.timestep * (graph.getWidth()+1) * 1000;
				var start_date = new Date(date.getTime() - menu.timeWidth);
				target
				+= '/by_time/'
				+  start_date.getTime() / 1000.0 + '/'
				+  date.getTime() / 1000.0 + '/'
				+  Config.timestep;
				if (!menu.getDate()) graph.setOverviewLabel('Consommation actuelle');
				else                 graph.setOverviewLabel('Consommation entre ' + dateutils.humanTime(start_date) + ' et ' + dateutils.humanTime(date));
				break;

			case 'day':
				target
				+= '/by_time/'
				+  dateutils.getDayStart(date) / 1000.0 + '/'
				+  dateutils.getDayEnd(date) / 1000.0 + '/'
				+  dateutils.getHourLength(date) / 1000.0;
				graph.setOverviewLabel('Consommation ' + dateutils.humanDay(date));
				break;

			case 'week':
				target
				+= '/by_time/'
				+  dateutils.getWeekStart(date) / 1000.0 + '/'
				+  dateutils.getWeekEnd(date) / 1000.0 + '/'
				+  dateutils.getDayLength(date) / 1000.0;
				graph.setOverviewLabel('Consommation ' + dateutils.humanWeek(date));
				break;

			case 'month':
				target
				+= '/by_time/'
				+  dateutils.getMonthStart(date) / 1000.0 + '/'
				+  dateutils.getMonthEnd(date) / 1000.0 + '/'
				+  dateutils.getDayLength(date) / 1000.0;
				graph.setOverviewLabel('Consommation ' + dateutils.humanMonth(date));
				break;

			default:
				if (callback) callback();
				return;
		}

		graph.setOverview('');
		graph.startLoading();
		provider.get(target, function(data) {
			graph.rect_width = graph.getPixelWidth() / data.length - graph.rect_margin;
			var s = 0, i = 0;
			data.map(function(m) {
				if (m.value !== undefined) {
					graph.addRect(m.value, false, graph.getLegend(mode, date, i));
					s += m.value;
				} else {
					graph.addRect(undefined, false, graph.getLegend(mode, date, i));
				}
				i += 1;
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
		if (menu.getMode() == 'now' && menu.getDate() === null) {
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
