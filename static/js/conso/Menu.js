/**
 * Handle graph menu buttons
 */
var Menu = function() {
	var api = {};
	var now_btn = document.getElementById('scale-now')
	  , day_btn = document.getElementById('scale-day')
	  , week_btn = document.getElementById('scale-week')
	  , month_btn = document.getElementById('scale-month')
	  , toggle_unit = document.getElementById('toggle-unit')
	  , mode = ''
	  , unit = ''
	  ;

	api.onunitchange = function(unit, callback){};
	api.onmodechange = function(mode, callback){};

	/**
	 * Add menu listeners
	 */
	api.init = function() {
		now_btn.addEventListener('click', function() {
			api.setMode('now');
		});

		day_btn.addEventListener('click', function() {
			api.setMode('day');
		});

		week_btn.addEventListener('click', function() {
			api.setMode('week');
		});

		month_btn.addEventListener('click', function() {
			api.setMode('month');
		});

		toggle_unit.addEventListener('click', function(ev){api.toggleUnit()});
	}

	/**
	 * Get display mode
	 */
	api.getMode = function() {
		return mode;
	};

	/**
	 * Set display mode.
	 * @param mode: New mode
	 * @param callback: (optional)
	 * @return boolean Whether the mode is accepted.
	 */
	api.setMode = function(new_mode, callback) {
		now_btn.className = '';
		day_btn.className = '';
		week_btn.className = '';
		month_btn.className = '';
		switch(new_mode) {
			case 'now':
				now_btn.className = 'active';
				break;
			case 'day':
				day_btn.className = 'active';
				break;
			case 'week':
				week_btn.className = 'active';
				break;
			case 'month':
				month_btn.className = 'active';
				break;
			default:
				return false;
		}
		if (new_mode != mode) {
			mode = new_mode;
			api.onmodechange(mode, callback);
		}
		return true;
	};

	/**
	 * Set unit.
	 * @param unit: New mode
	 * @param callback: (optional)
	 * @return boolean Whether the unit is accepted.
	 */
	api.setUnit = function(new_unit, callback) {
		switch(new_unit) {
			case 'energy':
				toggle_unit.innerHTML = 'Énergie';
				toggle_unit.className = 'red-day';
				break;
			case 'price':
				toggle_unit.innerHTML = 'Prix';
				toggle_unit.className = 'blue-day';
				break;
			default:
				return false;
		}
		if (new_unit != unit) {
			unit = new_unit;
			api.onunitchange(unit, callback);
		}
		return true;
	};

	/**
	 * Get unit.
	 */
	api.getUnit = function() {
		return unit;
	};

	/**
	 * Get unit string, which designate unit in ascii chars.
	 * This is used for example in the API.
	 * @return unit string.
	 */
	api.getUnitString = function() {
		return {
			'energy': mode == 'now' ? 'watts' : 'kwatthours',
			'price': 'euros'
		}[unit];
	};

	/**
	 * Get unit shortcut.
	 * This is used for displaying.
	 * @return unit shortcut.
	 */
	api.getUnitShortcut = function() {
		return {
			'energy': mode == 'now' ? 'W' : 'kWh',
			'price': '€'
		}[unit];
	};

	/**
	 * Toggle unit
	 * @param callback: (optional)
	 */
	api.toggleUnit = function(callback) {
		if (unit == 'energy') {
			api.setUnit('price', callback);
		} else {
			api.setUnit('energy', callback);
		}
	};

	return api;
}
