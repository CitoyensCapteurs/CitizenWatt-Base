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
	return Math.round(100*(0.2317 + (0.1367 * energy)))/100;
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
	 * Add a new rect to the graph.
	 * @param power: Power represented by the rect.
	 * @param animated: (optional) Whether the addition of the value must be animated. Default to True
	 */
	api.addRect = function(power, animated) {
		if (animated === undefined) animated = true;
		var height = parseInt(power) / MAX_POWER * 100;
		var div = document.createElement('div');
		var blank = document.createElement('div');
		var color = document.createElement('div');
		graph_values.appendChild(div);
		div.appendChild(blank);
		div.appendChild(color);

		div.className = animated ? 'animated rect' : 'rect';
		div.style.width = SIZE + 'px';

		var color_class = (height > 33.3 ? (height >= 66.7 ? 'red' : 'orange') : 'yellow');
		color.className = 'color ' + color_class + '-day';
		color.style.width = SIZE + 'px';
		color.style.height = height + '%';

		blank.className = 'blank';
		blank.style.width = SIZE + 'px';
		blank.style.height = (100 - height) + '%';

		now.className = 'blurry ' + color_class;
		now.innerHTML = Math.floor(power) + 'W';

		++n_values;
		sum += parseInt(power);
		total = sum * UPDATE_TIMEOUT / 3600 / 1000000;
		height = total / MAX_POWER * 100;
		color_class = (height > 33.3 ? (height >= 66.7 ? 'red' : 'orange') : 'yellow');
		day.className = 'blurry ' + color_class;
		var timestamp = Math.round((new Date().getTime()) / 1000);
		day.innerHTML = Math.round(total * 1000)/1000 + 'kWh (' + kWh_to_euros(total)+'€)';

		var max_values = api.getWidth();
		if (n_values >= max_values) {
			graph_values.removeChild(graph_values.firstChild)
		}

	}

	/**
	 * Add an horizontal graduation line (so a graduation for the vertical axis)
	 * @param power: Power at which the graduation is added.
	 */
	api.addVerticalGraduation = function(power) {
		var height = parseInt(power) / MAX_POWER * 100;
		var span = document.createElement('span');
		graph_vertical_axis.appendChild(span);

		span.style.bottom = height + '%';
		span.innerHTML = power + "W";
	}

	/**
	 * Return the width of the graph in number of values that can be displayed
	 */
	api.getWidth = function() {
		return Math.floor(graph.clientWidth / (SIZE + BORDER));
	};

	return api;
};


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

		req.open('GET', API_URL + '/' + nb, true);
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

	/**
	 * Callbacks
	 */
	api.oninit = function(){console.log('Not set')}; // called when init is done

	/**
	 * Init application.
	 * Add graduation lines
	 */
	api.init = function() {
		var graduations = [0.00, 0.33, 0.66, 1.00]; // Graduation positions (relative)
		graduations.map(function (t) {
			graph.addVerticalGraduation(MAX_POWER * t)
		});

		provider.get(graph.getWidth(), function(data) {
			data.map(function(value) {
				graph.addRect(value.power, false)
			});
			api.oninit();
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
