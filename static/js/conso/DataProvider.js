/**
 * Provide a way to get new data.
 */
var DataProvider = function() {
	var api = {};
	var slope_watt_euros, constant_watt_euros, saved_rate = null; // Cache for convertion rate
	var sensor_id = null; // Cache for sensor ID

	api.onratechange = function(rate){};

	/**
	 * Get new data from server.
	 * @param target: Type of data to get (@see API specification)
	 * @param callback: callback that take data as first argument
	 */
	api.get = function(target, callback) {
		var req = new XMLHttpRequest();
		req.open('GET', API_URL + target, true);
		req.send();
		req.onreadystatechange = function() {
			if (req.readyState == 4) {
				try {
					res = JSON.parse(req.responseText);
				}
				catch (e) {
					console.log('ERROR', req.responseText);
				}
				if (res.rate !== undefined) {
					api.onratechange(res.rate);
				}
				callback(res.data);
			}
		}
	}


	/**
	 * Get watt_euros convertion info
	 * @param rate: day or night tariff
	 * @param callback: callback that takes origin value and slope
	 */
	api.getConvertInfo = function(rate, callback) {
		if (saved_rate != rate) {
			api.get('/energy_providers/current', function(provider) {
				slope_watt_euros	= provider[rate+'_slope_watt_euros'];
				constant_watt_euros	= provider[rate+'_constant_watt_euros'];
				saved_rate = rate;
				callback(constant_watt_euros, slope_watt_euros);
			});
		} else {
			callback(constant_watt_euros, slope_watt_euros);
		}
	}


	/**
	 * Get active sensor ID (active iff name is 'CitizenWatt')
	 * @param callback: callback that takes sensor ID
	 */
	api.getSensorId = function(callback) {
		if (sensor_id == null) {
			api.get('/sensors', function(sensors) {
				for (var i = sensors.length - 1; i >= 0; i--) {
					if (sensors[i].name == 'CitizenWatt')
						sensor_id = sensors[i].id;
				};
				callback(sensor_id);
			});
		} else {
			callback(sensor_id);
		}	
	}

	return api;
};
