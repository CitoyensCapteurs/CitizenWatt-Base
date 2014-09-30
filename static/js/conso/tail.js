/**
 * Main function
 * Create app, Init it and then update it regularly
 */
function init() {
	var app = App();

	app.oninit = function() {
		app.update();
		setTimeout(arguments.callee, Config.update_timeout);
	}

	app.init();
}

window.onload = init();
