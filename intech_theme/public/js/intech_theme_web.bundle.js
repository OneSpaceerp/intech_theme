/* In Tech — website, portal and login scripts, bundled.
   The server has already put the theme attributes on <html> and the brand's
   colours inline (api/website.py), so the page paints right before this runs;
   what is here is the brand panel on the login page and the vendor-name pass
   for text the page's own scripts write after load. */

import * as login from "./intech-login";
import { may_have_vendor_name, rebrand } from "./intech-brand-text";

function brand_name() {
	const element = document.getElementById("intech-web");
	try {
		return (element && JSON.parse(element.textContent || "{}").brand_name) || "In Tech";
	} catch (error) {
		return "In Tech";
	}
}

// The login page's messages ("Login to ...", errors) are written by script after load.
function scrub_later_text() {
	const brand = brand_name();
	const observer = new MutationObserver((mutations) => {
		mutations.forEach((mutation) => {
			mutation.addedNodes.forEach((node) => {
				if (node.nodeType === Node.TEXT_NODE && may_have_vendor_name(node.nodeValue)) {
					node.nodeValue = rebrand(node.nodeValue, brand);
				} else if (node.nodeType === Node.ELEMENT_NODE && may_have_vendor_name(node.textContent)) {
					const walker = document.createTreeWalker(node, NodeFilter.SHOW_TEXT);
					while (walker.nextNode()) {
						const text = walker.currentNode;
						if (may_have_vendor_name(text.nodeValue) && !text.parentElement.closest("script,style,textarea,input")) {
							text.nodeValue = rebrand(text.nodeValue, brand);
						}
					}
				}
			});
		});
	});
	observer.observe(document.body, { childList: true, subtree: true });
}

function ready(fn) {
	if (document.readyState !== "loading") fn();
	else document.addEventListener("DOMContentLoaded", fn, { once: true });
}

ready(() => {
	try {
		login.start();
		if (document.documentElement.hasAttribute("data-intech")) scrub_later_text();
	} catch (error) {
		console.error("In Tech:", error);
	}
});
