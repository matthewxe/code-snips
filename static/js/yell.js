import { add_card_byid, get_api } from "./discover.js";

async function append_comment(comment_id, comment_container) {
	const json = await get_api(comment_id, "comment");
	console.log(json);
	if (json == "404") {
		return "404";
	}
	const comment = document.createElement("div");
	comment.className = "bg-body-tertiary card p-3 mb-3";
	const title_container = document.createElement("div");
	title_container.className = "d-flex align-middle";

	const lower_container = document.createElement("div");
	lower_container.className = "d-flex h-1";
	const made_by = document.createElement("p");
	made_by.className = "align-middle flex-grow-1";
	const name = document.createElement("span");
	name.innerHTML = json["author"];
	name.className = "text-info";
	made_by.appendChild(name);
	made_by.innerHTML += ", " + new Date(json["base_datetime"]).toLocaleString();
	lower_container.appendChild(made_by);
	comment.appendChild(lower_container);

	const content = document.createElement("a");
	// title.className = "pe-5 flex-grow-1 fs-3 comment-title";
	content.className = "card-title";
	content.innerHTML = json["comment_content"];
	content.href = "/comment" + "/" + json["content_id"];
	comment.appendChild(content);

	if (json["base_comments"] > 0) {
		const replies = document.createElement("a");
		name.innerHTML = "replies" + json["base_comments"];
		name.className = "text-info";
		console.log("bruh");
		comment.appendChild(replies);
	}

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
		console.log("shite");
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
