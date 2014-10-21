/**
 * Gather graph-related functions
 * @param unit: (optional) Graphe unit
 * @param max_value: (optional) Defautl graph max_value
 */
var Graph = function(unit, max_value) {
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

	api.unit = unit || 'W';
	api.type = 'energy';
	api.rect_width = Config.rect_width;
	api.rect_margin = Config.rect_margin;
	api.autoremove = true;
	api.max_value = max_value || 1e-6;

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
	}

	/**
	 * Init graph
	 */
	api.init = function() {
		n_values = 0;

		var graduations = [0.00, 0.33, 0.66, 1.00]; // Graduation positions (relative)
		graduations.map(function (t) {
			api.addVerticalGraduation(t)
		});
		
		return api;
	}

	/**
	 * Set value disaplyed in overview
	 * @param power: value to display
	 */
	api.setOverview = function(power) {
		if (power === null) {
			now.innerHTML = '&nbsp;';
			return;
		}
		if (api.unit == 'cents/min') power = power / 8 * 60 * 100;
		now.innerHTML = api.round(power) + (api.unit == 'cents/min' ? ' centimes par minute' : api.unit);
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
	 * @param legend: (optional) Legend to add to the rect
	 */
	api.addRect = function(power, animated, legend) {
		if (animated === undefined) animated = true;
		var defined = true;
		if (power === undefined) {
			defined = false;
			power = 0;
		}

		if (unit == 'cents/min') {
			power = power / 8 * 60 * 100;
		}
		
		if (power > api.max_value) {
			api.scaleVertically(power / api.max_value);
		}

		var div = document.createElement('a');
		div.setAttribute('href', location.hash); // TODO
		graph_values.appendChild(div);

		div.className = 'rect';
		if (!defined) div.className += ' undefined';
		if (animated) div.className += ' animated';
		div.className += ' ' + api.type;

		var info = document.createElement('div');
		div.appendChild(info);

		info.className = 'rect-info';
		if (defined) info.innerHTML = api.round(power) + api.unit;
		else         info.innerHTML = '<em>Pas de donnée</em>';
		if (legend) info.innerHTML += '<br/>' + legend;

		var color = document.createElement('div');
		div.appendChild(color);

		var height = api.round(power) / api.max_value * 100;
		var color_class = api.colorize(height);

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
	};

	/**
	 * Remove last rect from graph
	 * @return api;
	 */
	api.removeRect = function() {
		if (graph_values.lastChild)
			graph_values.removeChild(graph_values.lastChild);
		
		return api;
	};

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
	 * Add an horizontal absolute graduation line
	 * @param pos: Absolute position at which the graduation is placed
	 */
	api.addAbsoluteVerticalGraduation = function(pos) {
		if (pos * 1.1 > api.max_value) {
			api.scaleVertically(pos * 1.1 / api.max_value);
		}

		var height = pos / api.max_value * 100;
		var span = document.createElement('span');
		var hr_id = rand64(5);
		graph_vertical_axis.appendChild(span);

		span.style.bottom = height + '%';
		span.setAttribute('cw-absolute-graduation-position', pos);
		span.setAttribute('cw-absolute-graduation-hr', hr_id);

		var hr = document.createElement('hr');
		hr.style.bottom = height + '%';
		hr.id = hr_id;
		hr.className = 'absolute-graduation-hr';
		graph.appendChild(hr);

		api.updateVerticalGraduation(span);

		return api;
	}

	/**
	 * Update displayed value of vertical graduation
	 * @param graduation: graduation to resize
	 */
	api.updateVerticalGraduation = function(graduation) {
		if (graduation.getAttribute('cw-graduation-position') !== null) {
			var power = api.round(graduation.getAttribute('cw-graduation-position') * api.max_value);
			graduation.innerHTML = power + api.unit;
		}
		if (graduation.getAttribute('cw-absolute-graduation-position') !== null) {
			var pos = graduation.getAttribute('cw-absolute-graduation-position');
			var hr_id = graduation.getAttribute('cw-absolute-graduation-hr');
			var hr = document.getElementById(hr_id);
			hr.style.bottom = graduation.style.bottom = (pos / api.max_value * 100) + '%';
			var power = api.round(pos);
			graduation.innerHTML = power + api.unit;
		}
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
			graph_values.removeChild(graph_values.firstChild);
		while (graph_vertical_axis.firstChild)
			graph_vertical_axis.removeChild(graph_vertical_axis.firstChild);

		var hr;
		while (hr = document.getElementsByClassName('absolute-graduation-hr')[0])
			hr.parentNode.removeChild(hr);
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


	/**
	 * Return a human readable legend
	 * @param mode: 'now', 'day', 'week', 'month'
	 * @param date: view date
	 * @param i: index
	 * [Static]
	 */
	api.getLegend = function(mode, date, i) {
		switch(mode) {
			case 'now':
				return '';

			case 'day':
				return i + 'h - ' + (i+1) + 'h';

			case 'week':
				return dateutils.getStringDay(i);

			case 'month':
				return i + ' ' + dateutils.getStringMonth(date);
		}
	};

	return api;
};


var PriceGraph = function(unit) {
	var api = Graph(unit);

	api.type = 'price';

	api.colorize = function(t) {
		return (t > 33.3 ? (t >= 66.7 ? 'dark-blue' : 'blue') : 'light-blue');
	}

	return api;
};

