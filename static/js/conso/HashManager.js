var HashManager = function() {
	var api = {};
	var unit, mode;

	components = location.hash.slice(1).split('-');
	unit = components[0];
	mode = components[1] || 'now';
	date = components.length > 2 ? new Date(parseInt(components[2])*1000) : null;

	api.updateHash= function(){
		var hash = '#' + unit + '-' + mode;
		if (date !== null) hash += '-' + Math.floor(date.getTime() / 1000);
		location.hash = hash;
	};

	api.setUnit = function(new_unit) {
		unit = new_unit;
		api.updateHash();
	};

	api.getUnit = function() {
		return unit;
	};

	api.setMode = function(new_mode) {
		mode = new_mode;
		api.updateHash();
	};

	api.getMode = function() {
		return mode;
	};

	api.setDate = function(new_date) {
		date = new_date;
		api.updateHash();
	};

	api.getDate = function() {
		return date;
	};

	return api;
};

