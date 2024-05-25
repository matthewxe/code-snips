const main = document.getElementById("main");

async function get_yell(id) {
	const result = await fetch("/yell/" + id);
	return await result.json();
}

async function get_tags(id) {
	const result = await fetch("/tags/" + id);
	return await result.json();
}

async function append_tags(title, id) {
	const tags = await get_tags(id);
	if (tags == "404") {
		return "404";
	}
	title.innerHTML += "<br><br>Tags: ";
	for (var index = 0; index < tags.length; index++) {
		const tag = document.createElement("span");
		tag.className = "mx-1 fs-6 badge bg-secondary";
		tag.innerHTML = tags[index];
		title.appendChild(tag);
	}
}

// async function create_card(json) {
async function create_card(json, tags) {
	const yell_id = json["yell_id"];

	const card = document.createElement("div");
	card.className = "bg-body-tertiary card p-3 flex-grow-1";
	const title_container = document.createElement("div");
	title_container.className = "d-flex align-middle";
	const title = document.createElement("h3");
	title.className = "pe-5 flex-grow-1";
	title.innerHTML = json["yell_title"];

	title_container.appendChild(title);
	card.appendChild(title_container);

	const lower_container = document.createElement("div");
	lower_container.className = "d-flex h-1";
	const made_by = document.createElement("p");
	made_by.className = "align-middle flex-grow-1";
	made_by.innerHTML =
		"Made by " +
		json["author"] +
		", " +
		new Date(json["yell_datetime"]).toLocaleString();
	const made_inLang = document.createElement("p");
	made_inLang.className = "pe-3 align-middle text-info";
	made_inLang.innerHTML = json["post_filename"];
	lower_container.appendChild(made_by);
	lower_container.appendChild(made_inLang);
	card.appendChild(lower_container);

	const accordion = document.createElement("div");
	accordion.className = "accordion";

	const description = document.createElement("div");
	description.className = "accordion-item";
	const description_header = document.createElement("h2");
	description_header.className = "accordion-header";
	const description_header_button = document.createElement("button");
	description_header_button.className = "accordion-button collapsed";
	description_header_button.type = "button";
	description_header_button.dataset.bsToggle = "collapse";
	description_header_button.dataset.bsTarget =
		"#accordionPanelDescription" + yell_id;
	description_header_button.ariaExpanded = "false";
	description_header_button.ariaControls =
		"accordionPanelDescription" + yell_id;
	description_header_button.innerHTML = "Description";
	description_header.appendChild(description_header_button);
	description.appendChild(description_header);

	const description_content = document.createElement("div");
	description_content.id = "accordionPanelDescription" + yell_id;
	description_content.className = "accordion-collapse collapse";

	const description_content_body = document.createElement("div");
	description_content_body.className = "accordion-body";
	description_content_body.innerHTML = json["post_description"];
	append_tags(description_content_body, yell_id);
	description_content.appendChild(description_content_body);
	description.appendChild(description_content);
	accordion.appendChild(description);

	const code = document.createElement("div");
	code.className = "accordion-item";
	const code_header = document.createElement("h2");
	code_header.className = "accordion-header";
	const code_header_button = document.createElement("button");
	code_header_button.className = "accordion-button";
	code_header_button.type = "button";
	code_header_button.dataset.bsToggle = "collapse";
	code_header_button.dataset.bsTarget = "#accordionPanelCode" + yell_id;
	code_header_button.ariaExpanded = "true";
	code_header_button.ariaControls = "accordionPanelCode" + yell_id;
	code_header_button.innerHTML = "Code";
	code_header.appendChild(code_header_button);
	code.appendChild(code_header);

	const code_content = document.createElement("div");
	code_content.id = "accordionPanelCode" + yell_id;
	code_content.className = "accordion-collapse collapse show position-relative";

	const code_content_body = document.createElement("div");
	code_content_body.className = "accordion-body overflow-scroll p-0";
	code_content_body.innerHTML = json["post_code"];

	const code_content_copy = document.createElement("button");
	code_content_copy.className = "card position-absolute top-0 end-0 pb-1 m-1";
	code_content_copy.innerHTML = "Copy";
	code_content_copy.onclick = () => {
		navigator.clipboard.writeText(
			code_content_body.getElementsByClassName("code")[0].textContent,
		);
		code_content_copy.innerHTML = "Copied";
		setTimeout(() => {
			code_content_copy.innerHTML = "Copy";
		}, 2000);
	};

	code_content_body.appendChild(code_content_copy);
	code_content.appendChild(code_content_body);
	code.appendChild(code_content);
	accordion.appendChild(code);
	card.appendChild(accordion);

	// Prism.highlightElement(code_content_body_pre_code);
	return card;
}

async function add_card_byid(id, div = main) {
	// console.log("request for post", id);
	const get = await get_yell(id);
	if (get == "404") {
		// console.log("failed request for post", id);
		return 404;
	}
	const tags = await get_tags(id);

	const card = await create_card(get);
	div.appendChild(card);
	// console.log("completed request for post", id);
}

// async function add_card_bydict(dict) {
// 	// console.log("request for post", dict["yell_title"]);
// 	if (dict == '404') {
// 		return;
// 	}
//
// 	const card = await create_card(dict);
// 	// console.log(card);
// 	main.appendChild(card);
// 	// console.log("completed request for post", dict["yell_title"]);
// }

async function wait_for_scroll() {
	return new Promise((resolve) =>
		window.addEventListener("scroll", () => {
			window.removeEventListener("scroll", self);
			const endOfPage =
				window.innerHeight + window.scrollY >= document.body.offsetHeight - 100;

			if (endOfPage) {
				// console.log(endOfPage);
				resolve(new Promise((r) => setTimeout(r, 500)));
			} else return window.addEventListener("scroll", self);
		}),
	);
}

async function main_discover() {
	const get = await get_yell("last");
	for (var index = get["yell_id"]; index > 0; index--) {
		if (index % 15 == 0) {
			await wait_for_scroll();
		}
		add_card_byid(index);
	}
	stop_spinner();
}

const warn = document.getElementById("warn");
const spinner = document.getElementById("spinner");

const showtext = setTimeout(() => {
	warn.style.display = "block";
}, 7000);

function stop_spinner() {
	clearTimeout(showtext);
	spinner.style.display = "none";
	warn.style.display = "block";
	warn.innerHTML = "No more results";
}

export {
	get_yell,
	add_card_byid,
	// add_card_bydict,
	create_card,
	main_discover,
	stop_spinner,
};
