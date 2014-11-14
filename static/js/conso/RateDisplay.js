/**
 * Display rate type (day or night) in the header
 */
var RateDisplay = function() {
	var api = {};

	var logo_day = document.getElementById('rate-logo-day')
	  , logo_night = document.getElementById('rate-logo-night')
	  ;
	var rate;

	/**
	 * Set rate and show the corresponding image in header
	 */
	api.setRate = function(new_rate) {
		if (new_rate != rate) {
			logo_day.style.display = logo_night.style.display = 'none';
			switch (new_rate) {
				case 'day':
					logo_day.style.display = 'block';
					break;

				case 'night':
					logo_night.style.display = 'block';
					break;

				case 'none':
					alert('none');
			}
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