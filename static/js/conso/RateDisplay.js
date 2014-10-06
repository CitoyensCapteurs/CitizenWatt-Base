/**
 * Display rate type (day or night) in the header
 */
var RateDisplay = function() {
	var api = {};

	var logo_day = document.getElementById('rate-logo-day')
	  , logo_night = document.getElementById('rate-logo-night')
	  ;
	var rate;

	api.setRate = function(new_rate) {
		if (new_rate != rate) {
			logo_day.style.display = logo_night.style.display = 'none';
			(new_rate == 'day' ? logo_day : logo_night).style.display = 'block';
			rate = new_rate;
		}
	};

	/**
	 * @return current rate ('day' or 'night')
	 */
	api.getRate = function() {
		return rate;
	}

	return api;
}