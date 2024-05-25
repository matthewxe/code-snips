import { add_card_byid } from "./discover.js";

const rated = document.getElementById("highest_rated");
const recent = document.getElementById("recently_uploaded");

async function spinner_replace(id, div) {
	const get = await add_card_byid(id, "yell", div);
	console.log(id, get);
	if (get == "404") {
		div.innerHTML = "Could not load this post right now.";
	} else {
		div.children[0].remove();
	}
}

spinner_replace("rated", rated);
spinner_replace("last", recent);
