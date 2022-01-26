function _sl(s, c) {
	return (c || document).querySelector(s);
}


// Example: https://consent.youtube.com/d?continue=https://www.youtube.com/watch?v%3D6fOk9AklzFk&gl=DE&hl=de&pc=yt&src=1

function standAloneConsentForm(l) {
	if (l.pathname == '/m') {
		var e = document.querySelector('c-wiz h1 ~ div a[href*="/d?continue"]');
		
		if (e)
			e.click();
	}
	else if (l.pathname == '/d') {
		document.querySelectorAll('c-wiz h1 ~ div [data-is-touch-wrapper]').forEach(function(button) {
			var next = button.parentNode.nextSibling;
			
			if (next && next.matches('[jsaction]'))
				button.firstChild.click();
		});
		
		document.querySelector('c-wiz form button').click();
	}
}


var _i = setInterval(function() {
	var html = document.querySelector('html');
	
	if (!html || /idc8_329/.test(html.className))
		return;
	
	clearInterval(_i);
	
	html.className += ' idc8_329';
	
	var c = 0, l = document.location, i = setInterval(function() {
		
		// the 2nd step #introAgreeButton alternative may not be in use anymore
		
		if (l.hostname.split('.')[0] == 'consent') {
			var containers = document.querySelectorAll('.cui-csn-data');
			
			if (containers.length > 0) {
				var container = containers[containers.length - 1];
				
				if (l.pathname == '/intro/') {
					var e = _sl('#introAgreeButton');
					
					if (e) {
						e.click();
					} else {
						e = _sl('a[href*="continue"]:not([href*="account"])', container);
					
						if (e) {
							e.click();
						}
					}
				}
				else if (l.pathname == '/ui/') {
					var e = _sl('div[style*="none"] img[src*="keyboard_arrow_down_white"]', container);
					
					if (e) {
						_sl('#agreeButton').click();
						clearInterval(i);
					} else {
						_sl('img[src*="keyboard_arrow_down_white"]', container).parentNode.parentNode.click();
					}
				}
			}
			
			else
				standAloneConsentForm(l);
		}
		else {
			// General privacy reminder
			var e1 = _sl('form[action^="/signin/privacyreminder"] > div > span > div:not([role]) > div:not([tabindex]) span + div');
			if (e1) e1.click();
			
			// google.fr/flights
			var e2 = _sl('#gb[role="banner"] > div > div[style^="behavior"] > div > span + a[role="button"] + a[role="button"]');
			if (e2) e2.click();
			
			// Mobile devices
			var e3 = _sl('#lb[style*="visible"] #cnskc g-raised-button:last-child');
			if (e3) e3.click();
			
			// #cns=1
			if (l.hash == '#cns=1')
				l.hash = '#cns=0';
		}
		
		c++;
		
		if (c == 300)
			clearInterval(i);
	
	}, 500);
}, 500);