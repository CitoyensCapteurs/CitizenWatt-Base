/**
 * Main function
 * Create app, Init it and then update it regularly
 */
function init() {
	var app = App();

	app.oninit = function() {
		//app.update();
		setTimeout(arguments.callee, UPDATE_TIMEOUT);
	}

	app.init();
}

window.onload = init();
