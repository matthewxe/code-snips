import { add_card_byid, get_api, create_comment } from "./discover.js";

async function append_comment(comment_id, comment_container) {
	const json = await get_api(comment_id, "comment");
	if (json == "404") {
		return "404";
	}
	const comment = await create_comment(json);
	comment_container.appendChild(comment);
}

async function add_comments(id, yell_type, spinner, div) {
	const orig = await get_api(id, yell_type);
	const orig_id = orig["base_id"];

	const comment_set = await get_api(orig_id, "commentset");

	if (orig == "404" || comment_set == "404") {
		spinner.innerHTML = "Could not load this right now.";
		return;
	}
	const container = document.createElement("div");
	for (var index = 0; index < comment_set.comments.length; index++) {
		append_comment(comment_set.comments[index]["comment_id"], container);
	}

	spinner.remove();
	return div.appendChild(container);
}

async function spinner_replace(id, yell_type, spinner, div) {
	if (yell_type == "comment") {
		var get = await append_comment(id, div);
	} else {
		var get = await add_card_byid(id, yell_type, div);
	}

	if (get == "404") {
		spinner.innerHTML = "Could not load this right now.";
	} else {
		spinner.remove();
	}
}

async function main(yell_type, id) {
	spinner_replace(
		id,
		yell_type,
		document.getElementById("main_spinner"),
		document.getElementById("main"),
	);
	add_comments(
		id,
		yell_type,
		document.getElementById("comments_spinner"),
		document.getElementById("comments"),
	);
}

export { main };
