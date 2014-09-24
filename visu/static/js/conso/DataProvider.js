/**
 * Provide a way to get new data.
 */
var DataProvider = function() {
	var api = {};
	var slope_watt_euro, constant_watt_euros;

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
				callback(res.data);
			}
		}
	}


	/**
	 * Convert energy to euros. Get equation from server at first use.
	 * @param energy:
	 * @param callback: callback that take converted value as first argument
	 */
	api.convertEnergyToEuros = function(energy, callback) {
		if (slope_watt_euro === undefined) {
			api.get('energy_providers/current', function(provider) {
				slope_watt_euro	= provider.slope_watt_euro;
				constant_watt_euro	= provider.constant_watt_euro;
			});
		}
		callback(slope_watt_euro * energy + constant_watt_euros);
	}

	return api;
};
