import { get_yell, create_card } from "./discover.js";

const rated = document.getElementById("highest_rated");
const recent = document.getElementById("recently_uploaded");

async function spinner_replace(id, div) {
	const get = await get_yell(id);
	if (get == 404) {
		div.innerHTML = "Could not load this post right now.";
	} else {
		const card = await create_card(get);
		div.innerHTML = "";
		div.appendChild(card);
	}
}

spinner_replace("rated", rated);
spinner_replace("last", recent);
