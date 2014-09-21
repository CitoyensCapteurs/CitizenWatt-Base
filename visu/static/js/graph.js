// General params
var MAX_POWER = 3500
  , UPDATE_TIMEOUT = 2000 // En millisecondes
  , SIZE = 12 // Must be identical to @keyframes slidein (Used by Graph)
  , BORDER = 2 // Must be identical to #graph_values .rect (Used by Graph)
  ;

// Init variables
var start_time= Math.round((new Date().getTime()) / 1000)
  ;


/**
 * Converts energy to price.
 */
function kWh_to_euros(energy) {
	return Math.round(100*(0.2317 + (0.1367 * energy)))/100;  // TODO: Use API here
}

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
	  , mode = 'now'
	  , unit = 'W'
	  ;

	api.onunitchange = function(unit){};
	api.onmodechange = function(mode){};

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

		toggle_unit.addEventListener('click', api.toggleUnit);
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
	 * @return boolean Whether the mode is accepted.
	 */
	api.setMode = function(new_mode) {
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
		mode = new_mode;
		api.onmodechange(mode);
		return true;
	};

	/**
	 *
	 */
	api.toggleUnit = function() {
		if (unit == 'W') {
			unit = '€';
		} else {
			unit = 'W';
		}
		api.onunitchange(unit);
	};

	return api;
}

/**
 * Gather graph-related functions
 */
var Graph = function() {
	var api = {};

	var graph = document.getElementById('graph')
	  , graph_vertical_axis = document.getElementById('graph_vertical_axis')
	  , graph_values = document.getElementById('graph_values')
	  , now = document.getElementById('now')
	  , day = document.getElementById('day')
	  , sum = 0
	  , n_values = 0
	  , mean
	  ;

	/**
	 * Function used to convert values received from server
	 */
	api.convertValue = function(v){ return v; };

	api.max_value = MAX_POWER;
	api.unit = 'W';
	api.type = 'energy';

	/**
	 * Set color class name from height (between 0.0 and 1.0)
	 */
	api.colorize = function(t) {
		return (t > 33.3 ? (t >= 66.7 ? 'red' : 'orange') : 'yellow');
	}

	/**
	 * Init graph
	 */
	api.init = function() {
		var graduations = [0.00, 0.33, 0.66, 1.00]; // Graduation positions (relative)
		graduations.map(function (t) {
			api.addVerticalGraduation(api.max_value * t)
		});
		return api;
	}


	/**
	 * Add a new rect to the graph.
	 * @param power: Power represented by the rect.
	 * @param animated: (optional) Whether the addition of the value must be animated. Default to True
	 */
	api.addRect = function(power, animated) {
		if (animated === undefined) animated = true;
		power = parseInt(api.convertValue(power));

		var height = power / api.max_value * 100;
		var div = document.createElement('div');
		var blank = document.createElement('div');
		var color = document.createElement('div');
		graph_values.appendChild(div);
		div.appendChild(blank);
		div.appendChild(color);

		div.className = animated ? 'animated rect' : 'rect';
		div.className += ' ' + api.type;
		div.style.width = SIZE + 'px';

		var color_class = api.colorize(height);
		color.className = 'color ' + color_class + '-day';
		color.style.width = SIZE + 'px';
		color.style.height = height + '%';

		blank.className = 'blank';
		blank.style.width = SIZE + 'px';
		blank.style.height = (100 - height) + '%';

		now.className = 'blurry ' + color_class;
		now.innerHTML = power + api.unit;

		++n_values;
		sum += power;
		total = sum * UPDATE_TIMEOUT / 3600 / 1000000;
		height = total / MAX_POWER * 100;
		color_class = api.colorize(height);
		day.className = 'blurry ' + color_class;
		var timestamp = Math.round((new Date().getTime()) / 1000);
		day.innerHTML = Math.round(total * 1000)/1000 + 'kWh (' + kWh_to_euros(total)+'€)';

		var max_values = api.getWidth();
		if (n_values >= max_values) {
			graph_values.removeChild(graph_values.firstChild)
		}

		return api;
	}

	/**
	 * Add an horizontal graduation line (so a graduation for the vertical axis)
	 * @param power: Power at which the graduation is added.
	 */
	api.addVerticalGraduation = function(power) {
		power = parseInt(power);
		var height = power / api.max_value * 100;
		var span = document.createElement('span');
		graph_vertical_axis.appendChild(span);

		span.style.bottom = height + '%';
		span.innerHTML = power + api.unit;

		return api;
	}

	/**
	 * Change single vertical graduation scale
	 * @param graduation: graduation to resize
	 * @param ratio: Value by which multiply the vertical scale
	 */
	api.scaleVerticalGraduation = function(graduation, ratio) {
		var value = parseInt(graduation.innerHTML.slice(0, -api.unit.length))
		  , new_value = value * ratio;
		graduation.innerHTML = new_value + api.unit;
		return api;
	};

	/**
	 * Change single rect vertical scale without modifying the value it represents.
	 * @param rect: rect to resize
	 * @param ratio: Value by which multiply the rect vertical scale
	 */
	api.scaleRect = function(rect, ratio) {
		var color = rect.getElementsByClassName('color')[0]
		  , blank = rect.getElementsByClassName('blank')[0]
		  ;
		height = parseInt(color.style.height.slice(0, -1));
		new_height = height / ratio;
		color.style.height = new_height + '%';
		blank.style.height = (100 - new_height) + '%';
		return api;
	};

	/**
	 * Change graph vertical scale
	 * @param ratio: Value by which multiply the graph vertical scale
	 */
	api.scaleVertically = function(ratio) {
		var rects = graph_values.children;
		for (var i = 0 ; i < rects.length ; i++) {
			api.scaleRect(rects[i], ratio);
		}
		var graduations = graph_vertical_axis.children;
		console.log(graduations);
		for (var i = 0 ; i < graduations.length ; i++) {
			console.log(graduations[i]);
			api.scaleVerticalGraduation(graduations[i], ratio);
		}
		return api;
	};


	/**
	 * @return the width of the graph in number of values that can be displayed
	 */
	api.getWidth = function() {
		return Math.floor(graph.clientWidth / (SIZE + BORDER));
	};

	/**
	 * Clean graph (remove all values)
	 */
	api.clean = function() {
		while (graph_values.firstChild)
			graph_values.removeChild(graph_values.firstChild)
		while (graph_vertical_axis.firstChild)
			graph_vertical_axis.removeChild(graph_vertical_axis.firstChild)
	}

	return api;
};


var PriceGraph = function() {
	var api = Graph();

	api.convertValue = kWh_to_euros;
	api.max_value = kWh_to_euros(MAX_POWER);
	api.unit = '€';
	api.type = 'price';

	api.colorize = function(t) {
		return (t > 33.3 ? (t >= 66.7 ? 'dark-blue' : 'blue') : 'light-blue');
	}

	return api;
}


/**
 * Provide a way to get new data.
 */
var DataProvider = function() {
	var api = {};
	var req = new XMLHttpRequest();

	/**
	 * Get new data from server.
	 * @param nb: (optional) Number of values to request
	 * @param callback: callback that take data as first argument
	 */
	api.get = function(nb, callback) {
		if (callback === undefined) {
			callback = nb;
			nb = 1;
		}

		req.open('GET', API_URL + '/1/get/by_id/' + nb, true);
		req.send();
		req.onreadystatechange = function() {
			if (req.readyState == 4) {
				res = JSON.parse(req.responseText);
				callback(res.data);
			}
		}
	}

	return api;
};


/**
 * Core application
 */
var App = function() {
	var api = {};
	var graph = Graph();
	var provider = DataProvider();
	var menu = Menu(api);

	menu.onunitchange = function(unit) {
		graph.clean();
		if (unit == '€') {
			graph = PriceGraph();
		} else {
			graph = Graph();
		}
		graph.init();
		api.initValues();
	};

	menu.onmodechange = function(mode) {
		if (mode == 'day') {
			graph.scaleVertically(2.0);
		}
	};

	/**
	 * Callbacks
	 */
	api.oninit = function(){console.log('Not set')}; // called when init is done

	/**
	 * Init application.
	 * Add graduation lines
	 */
	api.init = function() {
		menu.init();
		graph.init();
		api.initValues(api.oninit);
	};

	/**
	 * Init graph values.
	 * @param callback: (optional)
	 */
	api.initValues = function(callback) {
		provider.get(graph.getWidth(), function(data) {
			data.map(function(value) {
				graph.addRect(value.power, false)
			});
			if (callback) callback();
		});
	}

	/**
	 * Go and get new values. This function should be called regularely by the main loop.
	 */
	api.update = function() {
		provider.get(function(data) {
			data.map(function(value) {
				graph.addRect(value.power)
			});
		});
	}

	return api;
};



/**
 * Main function
 * Create app, Init it and then update it regularly
 */
function init() {
	var app = App();

	app.oninit = function() {
		app.update();
		setTimeout(arguments.callee, UPDATE_TIMEOUT);
	}

	app.init();
}

window.onload = init();
