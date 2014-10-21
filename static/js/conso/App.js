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

	function reload(_, callback) {
		var mode = menu.getMode()
		  , date = menu.getDate()
		  , unit = menu.getUnit()
		  ;

		graph.clean();
		graph = unit == 'energy' ? Graph(mode == 'now' ? 'W' : 'kWh') : PriceGraph(mode == 'now' ? 'cents/min' : '€');
		graph.autoremove = mode == 'now' && date === null;

		if (unit == 'price') graph.round = function(v) { return Math.round(v * 100) / 100; };

		if (mode == 'now' && unit == 'energy') {
			provider.getProviderInfo(function(provider) {
				graph.addAbsoluteVerticalGraduation(provider['threshold']);
			});
		}
		graph.init();
		hash.setMode(mode);
		hash.setDate(date);
		hash.setUnit(unit == 'price' ? 'euros' : 'watt');
		api.initValues(callback);
	};

	menu.onmodechange = function(ev, callback) {
		menu.setDate(null, function(){
			reload(null, callback);
		}, false);
	}
	menu.onunitchange = reload;
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

			var unit = hash.getUnit() == 'euros' ? 'price' : 'energy';

			menu.setUnit(unit, function(){
			menu.setMode(hash.getMode(), function(){
			menu.setDate(hash.getDate(), function(){
				reload(null, api.oninit);
			}, false);
			}, false);
			}, false);

		});
	};

	/**
	 * Init graph values.
	 * @param callback: (optional)
	 */
	api.initValues = function(callback) {
		provider.getSensorId(function(sensor_id) {
			var target = '/' + sensor_id + '/get/' + menu.getUnitString();
			var mode = menu.getMode();
			var date = menu.getDate() || (new Date());
			var modifier = 0;

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
					modifier = 1. / (dateutils.getMonthLength(date) / dateutils.getDayLength());
					break;

				case 'week':
					target
					+= '/by_time/'
					+  (dateutils.getWeekStart(date) / 1000.0) + '/'
					+  ((dateutils.getWeekStart(date) + dateutils.getDayLength(date) * 7) / 1000.0) + '/' // Avoid pbs with Daylight Saving Time
					+  (dateutils.getDayLength(date) / 1000.0);
					graph.setOverviewLabel('Consommation ' + dateutils.humanWeek(date));
					modifier = 7. / (dateutils.getMonthLength(date) / dateutils.getDayLength());
					break;

				case 'month':
					target
					+= '/by_time/'
					+  dateutils.getMonthStart(date) / 1000.0 + '/'
					+  dateutils.getMonthEnd(date) / 1000.0 + '/'
					+  dateutils.getDayLength(date) / 1000.0;
					graph.setOverviewLabel('Consommation ' + dateutils.humanMonth(date));
					modifier = 1.0;
					break;

				default:
					if (callback) callback();
					return;
			}

			graph.setOverview(null);
			graph.startLoading();
			provider.get(target, function(data) {
				graph.rect_width = graph.getPixelWidth() / data.length - graph.rect_margin;
				var s = 0, i = 0;
				var last_good_value = null;
				var before_last_value = null;
				var last_value = null;
				data.map(function(m) {
					if (m !== null) {
						if (last_value === null && before_last_value !== null) {
							v = (before_last_value + m.value) / 2.0;
							s += v;
							graph
							.removeRect()
							.addRect(v, false, graph.getLegend(mode, date, i));
						}
						graph.addRect(m.value, false, graph.getLegend(mode, date, i));
						s += m.value;
						last_good_value = m.value;
						before_last_value = last_value;
						last_value = m.value;
					} else if (mode != 'now' || i < data.length - 1) { // Avoid leading undefined rect in instant view
						graph.addRect(undefined, false, graph.getLegend(mode, date, i));
						before_last_value = last_value;
						last_value = null;
					}
					i += 1;
				});
				if (mode != 'now') {
					provider.getConvertInfo(rate.getRate(), function(base_price){
						// Assume that base_price is not dependent of rate type
						graph.setOverview(s + base_price * modifier);
					});
				} else {
					graph.setOverview(last_good_value);
				}
				graph.stopLoading();
				if (callback) callback();
			});

			graph.last_call = Date.now() / 1000.0;
		});
	};

	/**
	 * Go and get new values. This function should be called regularely by the main loop.
	 */
	api.update = function() {
		if (menu.getMode() == 'now' && menu.getDate() === null && menu.isUpdated()) {
			provider.getSensorId(function(sensor_id) {
				var target
				= '/' + sensor_id + '/get/'
				+ menu.getUnitString()
				+ '/by_time/'
				+ graph.last_call + '/'
				+ (graph.last_call = Date.now() / 1000.0) + '/'
				+ Config.timestep;

				provider.get(target, function(data) {
					data.map(function(m) {
						if (m !== null) {
							graph.addRect(m.value);
							graph.setOverview(m.value);
						}
					});
				});
			});
		}
	};

	return api;
};
