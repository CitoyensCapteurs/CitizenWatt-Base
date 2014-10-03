var dateutils = (function() {
	var api = {};

	/**
	 * Get hour length (in milliseconds)
	 */
	api.getHourLength = function() {
		return 3600 * 1000;
	}

	/**
	 * Get day length (in milliseconds)
	 */
	api.getDayLength = function() {
		return api.getHourLength() * 24;
	};

	/**
	 * Get current day start (in millisecond timestamp)
	 * @param date: (optional) Replace current date
	 */
	api.getDayStart = function(date) {
		var date = date || new Date();
		return (new Date(date.getFullYear(), date.getMonth(), date.getDate())).getTime();
	};

	/**
	 * Get current day end (in millisecond timestamp)
	 * @param date: (optional) Replace current date
	 */
	api.getDayEnd = function(date) {
		var date = date || new Date();
		var day = (date.getHours() + 6) % 7;
		return (new Date(date.getFullYear(), date.getMonth(), date.getDate()+1)).getTime();
	};

	/**
	 * Get week length (in milliseconds)
	 */
	api.getWeekLength = function() {
		return api.getDayLength() * 7;
	};

	/**
	 * Get current week start (in millisecond timestamp)
	 * @param date: (optional) Replace current date
	 */
	api.getWeekStart = function(date) {
		var date = date || new Date();
		var day = (date.getDay() + 6) % 7;
		return (new Date(date.getFullYear(), date.getMonth(), date.getDate() - day)).getTime();
	};

	/**
	 * Get current week end (in millisecond timestamp)
	 * @param date: (optional) Replace current date
	 */
	api.getWeekEnd = function(date) {
		var date = date || new Date();
		var day = (date.getDay() + 6) % 7;
		return (new Date(date.getFullYear(), date.getMonth(), date.getDate() - day + 7)).getTime();
	};

	/**
	 * Get current month length (in milliseconds)
	 * @param date: (optional) Replace current date
	 */
	api.getMonthLength = function(date) {
		var date = date || new Date();
		return (new Date(date.getFullYear(),date.getMonth()+1,0)).getDate();
	};

	/**
	 * Get current month start (in millisecond timestamp)
	 * @param date: (optional) Replace current date
	 */
	api.getMonthStart = function(date) {
		var date = date || new Date();
		return (new Date(date.getFullYear(), date.getMonth(), 1)).getTime();
	};

	/**
	 * Get current week end (in millisecond timestamp)
	 * @param date: (optional) Replace current date
	 */
	api.getMonthEnd = function(date) {
		var date = date || new Date();
		return (new Date(date.getFullYear(), date.getMonth()+1, 1)).getTime();
	};

	return api;
})();



// Exports all for unit testing
for (var property in dateutils) {
	if (dateutils.hasOwnProperty(property)) {
		exports[property] = dateutils[property];
	}
}
