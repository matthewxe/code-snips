import { add_card_byid, create_card, get_yell } from "./discover.js";

const rated = document.getElementById("highest_rated");
const recent = document.getElementById("recently_uploaded");

async function main() {
	recent.innerHTML = "";
	await add_card_byid("last", recent);

	rated.innerHTML = "";
	await add_card_byid("rated", rated);
}

main();
