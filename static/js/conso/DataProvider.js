/**
 * Provide a way to get new data.
 */
var DataProvider = function() {
	var api = {};
	var slope_watt_euros, constant_watt_euros, saved_rate = null; // Cache for convertion rate

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

	return api;
};
