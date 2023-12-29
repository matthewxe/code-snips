import { get_yell, create_card } from "./discover.js";

const rated = document.getElementById("highest_rated");
const recent = document.getElementById("recently_uploaded");

async function spinner_replace(id, div) {
	const get = await get_yell(id);
	if (get == 404) {
		// console.log("failed request for post", id);
		return 404;
	}

	const card = await create_card(get);
	div.innerHTML = "";
	div.appendChild(card);
}

spinner_replace("rated", rated);
spinner_replace("last", recent);
