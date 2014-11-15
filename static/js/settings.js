
function init() {
	var night_rate_info = document.getElementById('night-rate-info')
	  , provider = document.getElementById('provider')
	  ;

	provider.addEventListener('change', function(ev) {
		var need_info = ev.explicitOriginalTarget.className == 'need-rate-info';
		night_rate_info.style.display = need_info ? 'block' : 'none';
	});
}

window.onload = init();
