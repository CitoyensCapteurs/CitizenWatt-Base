var dateutils = (function() {
	var api = {};

	/**
	 * Difference between base (raspi) time and local user
	 */
	api.offset = 0;

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
		return (new Date(date.getFullYear(), date.getMonth(), date.getDate())).getTime() + api.offset;
	};

	/**
	 * Get current day end (in millisecond timestamp)
	 * @param date: (optional) Replace current date
	 */
	api.getDayEnd = function(date) {
		var date = date || new Date();
		var day = (date.getHours() + 6) % 7;
		return (new Date(date.getFullYear(), date.getMonth(), date.getDate()+1)).getTime() + api.offset;
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
		return (new Date(date.getFullYear(), date.getMonth(), date.getDate() - day)).getTime() + api.offset;
	};

	/**
	 * Get current week end (in millisecond timestamp)
	 * @param date: (optional) Replace current date
	 */
	api.getWeekEnd = function(date) {
		var date = date || new Date();
		var day = (date.getDay() + 6) % 7;
		return (new Date(date.getFullYear(), date.getMonth(), date.getDate() - day + 7)).getTime() + api.offset;
	};

	/**
	 * Get current month length (in milliseconds)
	 * @param date: (optional) Replace current date
	 */
	api.getMonthLength = function(date) {
		var date = date || new Date();
		return (new Date(date.getFullYear(),date.getMonth()+1,0)).getDate() * api.getDayLength();
	};

	/**
	 * Get current month start (in millisecond timestamp)
	 * @param date: (optional) Replace current date
	 */
	api.getMonthStart = function(date) {
		var date = date || new Date();
		return (new Date(date.getFullYear(), date.getMonth(), 1)).getTime() + api.offset;
	};

	/**
	 * Get current week end (in millisecond timestamp)
	 * @param date: (optional) Replace current date
	 */
	api.getMonthEnd = function(date) {
		var date = date || new Date();
		return (new Date(date.getFullYear(), date.getMonth()+1, 1)).getTime() + api.offset;
	};

	/**
	 * Return human readable day of week
	 * @param i: index of day or date
	 */
	api.getStringDay = function(i) {
		if (i.getDay !== undefined) i = (i.getDay() + 6) % 7;
		return ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'][i];
	};

	/**
	 * Return human readable month
	 * @param i: index of month or date
	 */
	api.getStringMonth = function(i) {
		if (i.getMonth !== undefined) i = i.getMonth();
		return ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'][i];
	};

	/**
	 * Human readable time. Relative for first values (now, 1 min ago, etc) and then absolute.
	 * @param date
	 * @return string time
	 */
	api.humanTime = function(date) {
		var now = new Date();
		var prefix = now > date ? 'il y a ' : 'dans ';
		var diff = Math.abs(date.getTime() - now.getTime());
		if (diff < 60*1000)
			return prefix + Math.round(diff / 1000) + 's';

		if (Math.abs(date.getTime() - now.getTime()) < 3600*1000)
			return prefix + Math.round(diff / 60000) + 'min';// + Math.abs(date.getSeconds() - comp.getSeconds()) + 's';

		if (api.getDayStart(date) == api.getDayStart())
			return date.getHours() + 'h' + date.getMinutes();

		return api.humanDay() + ' à ' + date.getHours() + 'h' + date.getMinutes();
	};

	/**
	 * Human readable date. Relative for first values (today, yesterday) and then absolute.
	 * @param date
	 * @return string date
	 */
	api.humanDay = function(date) {
		var comp = new Date();
		if (api.getDayStart(comp) == api.getDayStart(date))
			return 'aujourd\'hui';
		
		comp.setDate(comp.getDate() + 1);
		if (api.getDayStart(comp) == api.getDayStart(date))
			return 'demain';

		comp.setDate(comp.getDate() - 2);
		if (api.getDayStart(comp) == api.getDayStart(date))
			return 'hier';

		if (api.getWeekStart() == api.getWeekStart(date) && date < (new Date()))
			return api.getStringDay(date).toLowerCase() + ' dernier';

		//if (api.getMonthStart() == api.getMonthStart(date))
		//	return 'le ' + date.getDate();

		return 'le ' + date.getDate() + ' ' + api.getStringMonth(date).toLowerCase();
	};

	/**
	 * Human readable week. Relative for first values (this week, past week) and then absolute.
	 * @param date
	 * @return string week
	 */
	api.humanWeek = function(date) {
		var comp = new Date();
		if (api.getWeekStart(comp) == api.getWeekStart(date))
			return 'cette semaine';
		
		comp.setDate(comp.getDate() + 7);
		if (api.getWeekStart(comp) == api.getWeekStart(date))
			return 'la semaine prochaine';

		comp.setDate(comp.getDate() - 14);
		if (api.getWeekStart(comp) == api.getWeekStart(date))
			return 'la semaine dernière';

		var f = new Date(api.getWeekStart(date));
		var l = new Date(api.getWeekEnd(date) - 1);
		var v
		= 'entre le ' + f.getDate() + ' ' + api.getStringMonth(f)
		+ ' et le ' + l.getDate() + ' ' + api.getStringMonth(l);
		return v.toLowerCase();
	};

	/**
	 * Human readable month.
	 * @param date
	 * @return string month
	 */
	api.humanMonth = function(date) {
		var comp = new Date();
		if (api.getMonthStart(comp) == api.getMonthStart(date))
			return 'ce mois';
		
		return 'en ' + api.getStringMonth(date).toLowerCase();
	};

	return api;
})();


/*
// Exports all for unit testing
for (var property in dateutils) {
	if (dateutils.hasOwnProperty(property)) {
		exports[property] = dateutils[property];
	}
}
//*/