// General params
var UPDATE_TIMEOUT = 2000 // En millisecondes
  , DEFAULT_RECT_WIDTH = 12
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
