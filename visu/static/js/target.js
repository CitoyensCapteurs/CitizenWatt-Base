
function init() {
	var target_ok = document.getElementById('target-ok')
	  , target_wip = document.getElementById('target-wip')
	  , target_no = document.getElementById('target-no')
	  , target_more = document.getElementById('target-more')
	  ;

	target_ok.style.display = 'block';
	target_wip.style.display = 'block';
	target_no.style.display = 'block';
	target_more.style.display = 'none';
	switch (location.hash) {
		case '#ok':
			target_wip.style.display = 'none';
			target_no.style.display = 'none';
			target_more.style.display = 'block';
			break;

		case '#wip':
			target_ok.style.display = 'none';
			target_no.style.display = 'none';
			target_more.style.display = 'block';
			break;
	}
}

window.onload = init();
window.addEventListener('hashchange', init);
