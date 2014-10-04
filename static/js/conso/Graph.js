/**
 * Gather graph-related functions
 */
var Graph = function(unit) {
	var api = {};

	var graph = document.getElementById('graph')
	  , graph_vertical_axis = document.getElementById('graph_vertical_axis')
	  , graph_values = document.getElementById('graph_values')
	  , graph_loading = document.getElementById('graph_loading')
	  , now = document.getElementById('now')
	  , now_label = document.getElementById('now_label')
	  , sum, n_values, mean
	  ;

	/**
	 * Function used to convert values received from server
	 */
	api.convertValue = function(v){ return v; };

	api.max_value = 1;
	api.unit = unit || 'W';
	api.type = 'energy';
	api.rect_width = Config.rect_width;
	api.rect_margin = Config.rect_margin;
	api.autoremove = true;

	/**
	 * Set color class name from height (between 0.0 and 1.0)
	 */
	api.colorize = function(t) {
		return (t > 33.3 ? (t >= 66.7 ? 'red' : 'orange') : 'yellow');
	}

	/**
	 * Round value according to max value
	 */
	api.round = function(v) {
		return Math.round(v * 10) / 10;
		/*
		var g = Math.pow(10, Math.round(Math.log(api.max_value))-2);
		return Math.round(v / g) * g;
		*/
	}

	/**
	 * Init graph
	 */
	api.init = function() {
		n_values = 0;

		var graduations = [0.00, 0.33, 0.66, 1.00]; // Graduation positions (relative)
		graduations.map(function (t) {
			api.addVerticalGraduation(api.max_value * t)
		});

		/*
		graph.addEventListener('mouseover', function() {
			now.innerHTML = 'blabla';
		});

		graph.addEventListener('mouseout', function() {
			now.innerHTML = 'blo';
		});
		*/

		return api;
	}

	/**
	 * Set value disaplyed in overview
	 * @param power: value to display
	 */
	api.setOverview = function(power) {
		now.innerHTML = api.round(power) + api.unit;
		var height = power / api.max_value * 100;
		now.className = 'blurry ' + api.colorize(height);
	};

	/**
	 * Set label under overview field.
	 * @pram label: new label
	 */
	api.setOverviewLabel = function(label) {
		now_label.innerHTML = label;
	};


	/**
	 * Add a new rect to the graph.
	 * @param power: Power represented by the rect.
	 * @param animated: (optional) Whether the addition of the value must be animated. Default to True
	 */
	api.addRect = function(power, animated) {
		if (animated === undefined) animated = true;
		
		if (power > api.max_value) {
			api.scaleVertically(power / api.max_value);
		}

		var height = api.round(power) / api.max_value * 100;
		var div = document.createElement('div');
		graph_values.appendChild(div);

		var info = document.createElement('div');
		div.appendChild(info);

		info.className = 'rect-info';
		info.innerHTML = api.round(power) + api.unit;

		var color = document.createElement('div');
		div.appendChild(color);

		var color_class = api.colorize(height);
		div.className = animated ? 'animated rect' : 'rect';
		div.className += ' ' + api.type;

		color.className = 'rect-color ' + color_class + '-day';
		color.style.height = height + '%';
		

		++n_values;

		var max_values = api.getWidth();
		// Le +10 c'est pour prendre de la marge. On ne peut pas mettre
		// simplement 1 sinon ça se voit lorsque plusieurs nouvelles mesures
		// arrivent en même temps.
		if (api.autoremove && n_values > max_values + 10) {
			/*
			graph_values.firstChild.style.width = '0';
			graph_values.firstChild.addEventListener('transitionend', function(){
				graph_values.removeChild(this);
			}, false);
			*/
			graph_values.removeChild(graph_values.firstChild)
		}

		div.style.width = api.rect_width + 'px';


		return api;
	}

	/**
	 * Add an horizontal graduation line (so a graduation for the vertical axis)
	 * @param pos: Relative position at which the graduation is placed
	 */
	api.addVerticalGraduation = function(pos) {
		var height = pos * 100;
		var span = document.createElement('span');
		graph_vertical_axis.appendChild(span);

		span.style.bottom = height + '%';
		span.setAttribute('cw-graduation-position', pos);
		api.updateVerticalGraduation(span);

		return api;
	}

	/**
	 * Update displayed value of vertical graduation
	 * @param graduation: graduation to resize
	 */
	api.updateVerticalGraduation = function(graduation) {
		var power = api.round(graduation.getAttribute('cw-graduation-position') * api.max_value);
		graduation.innerHTML = power + api.unit;
		return api;
	};

	/**
	 * Change single rect vertical scale without modifying the value it represents.
	 * @param rect: rect to resize
	 * @param ratio: Value by which multiply the rect vertical scale
	 */
	api.scaleRect = function(rect, ratio) {
		var color = rect.getElementsByClassName('rect-color')[0];
		height = parseInt(color.style.height.slice(0, -1));
		new_height = height / ratio;
		color.style.height = new_height + '%';

		var color_class = api.colorize(new_height);
		color.className = color.className.replace(/[^ ]*-day/, color_class + '-day');
		return api;
	};

	/**
	 * Change graph vertical scale
	 * @param ratio: Value by which multiply the graph vertical scale
	 */
	api.scaleVertically = function(ratio) {
		api.max_value = api.max_value * ratio;

		var rects = graph_values.children;
		for (var i = 0 ; i < rects.length ; i++) {
			api.scaleRect(rects[i], ratio);
		}
		var graduations = graph_vertical_axis.children;
		for (var i = 0 ; i < graduations.length ; i++) {
			api.updateVerticalGraduation(graduations[i]);
		}
		return api;
	};


	/**
	 * @return the width of the graph in pixels
	 */
	api.getPixelWidth = function() {
		return graph.clientWidth;
	};

	/**
	 * @return the width of the graph in number of values that can be displayed
	 */
	api.getWidth = function() {
		return Math.floor(api.getPixelWidth() / (api.rect_width + api.rect_margin));
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

	/**
	 * Hide loading icon
	 */
	api.stopLoading = function() {
		graph_loading.style.visibility = 'hidden';
	}

	/**
	 * Hide loading icon
	 */
	api.startLoading = function() {
		graph_loading.style.visibility = 'visible';
	}

	return api;
};


var PriceGraph = function() {
	var api = Graph('€');

	api.type = 'price';

	api.colorize = function(t) {
		return (t > 33.3 ? (t >= 66.7 ? 'dark-blue' : 'blue') : 'light-blue');
	}

	return api;
};

