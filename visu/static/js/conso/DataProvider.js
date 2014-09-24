/**
 * Provide a way to get new data.
 */
var DataProvider = function() {
	var api = {};

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

	return api;
};
