export async function get_yell(id) {
    var result = await fetch("/yell/" + id);
    return await result.json();
}

// async function create_card(json) {
export async function create_card(json) {
    var yell_id = json["yell_id"];

    var card = document.createElement("div");
    card.className = "bg-body-tertiary mx-2 card p-3 flex-grow-1";
    var title_container = document.createElement("div");
    title_container.className = "d-flex align-middle";
    var title = document.createElement("h3");
    title.className = "pe-5 flex-grow-1";
    title.innerHTML = json["yell_title"];
    title_container.appendChild(title);
    card.appendChild(title_container);

    var lower_container = document.createElement("div");
    lower_container.className = "d-flex h-1";
    var made_by = document.createElement("p");
    made_by.className = "align-middle flex-grow-1";
    made_by.innerHTML =
        "Made by " + json["yell_maker"] + ", " + json["yell_datetime"];
    var made_inLang = document.createElement("p");
    made_inLang.className = "pe-3 align-middle text-info";
    made_inLang.innerHTML = json["yell_language"];
    lower_container.appendChild(made_by);
    lower_container.appendChild(made_inLang);
    card.appendChild(lower_container);

    var accordion = document.createElement("div");
    accordion.className = "accordion";
    // accordion.id = "accordionPanelsStayOpenExample";

    var description = document.createElement("div");
    description.className = "accordion-item";
    var description_header = document.createElement("h2");
    description_header.className = "accordion-header";
    var description_header_button = document.createElement("button");
    description_header_button.className = "accordion-button collapsed";
    description_header_button.type = "button";
    description_header_button.dataset.bsToggle = "collapse";
    description_header_button.dataset.bsTarjson =
        "#accordionPanelDescription" + yell_id;
    description_header_button.ariaExpanded = "false";
    description_header_button.ariaControls =
        "accordionPanelDescription" + yell_id;
    description_header_button.innerHTML = "Description";
    description_header.appendChild(description_header_button);
    description.appendChild(description_header);

    var description_content = document.createElement("div");
    description_content.id = "accordionPanelDescription" + yell_id;
    description_content.className = "accordion-collapse collapse";

    var description_content_body = document.createElement("div");
    description_content_body.className = "accordion-body";
    description_content_body.innerHTML = json["yell_description"];
    description_content.appendChild(description_content_body);
    description.appendChild(description_content);
    accordion.appendChild(description);

    var code = document.createElement("div");
    code.className = "accordion-item";
    var code_header = document.createElement("h2");
    code_header.className = "accordion-header";
    var code_header_button = document.createElement("button");
    code_header_button.className = "accordion-button";
    code_header_button.type = "button";
    code_header_button.dataset.bsToggle = "collapse";
    code_header_button.dataset.bsTarjson = "#accordionPanelCode" + yell_id;
    code_header_button.ariaExpanded = "true";
    code_header_button.ariaControls = "accordionPanelCode" + yell_id;
    code_header_button.innerHTML = "Code";
    code_header.appendChild(code_header_button);
    code.appendChild(code_header);

    var code_content = document.createElement("div");
    code_content.id = "accordionPanelCode" + yell_id;
    code_content.className = "accordion-collapse collapse show";

    var code_content_body = document.createElement("div");
    code_content_body.className = "accordion-body p-1";
    var code_content_body_pre = document.createElement("pre");
    var code_content_body_pre_code = document.createElement("code");
    code_content_body_pre_code.classList =
        "language-" + json["yell_language_prism"];
    // console.log(json["yell_code_prism"]);
    code_content_body_pre_code.innerHTML = json["yell_code"];
    code_content_body_pre.appendChild(code_content_body_pre_code);
    code_content_body.appendChild(code_content_body_pre);
    code_content.appendChild(code_content_body);
    code.appendChild(code_content);
    accordion.appendChild(code);
    card.appendChild(accordion);

    Prism.highlightElement(code_content_body_pre_code);
    return card;
}

export async function add_card(index) {
    console.log("request for post", index);
    var main = document.getElementById("main");
    var get = await get_yell(index);
    if (get == 404) {
        return;
    }

    var card = await create_card(get);
    main.appendChild(card);
    console.log("completed request for post", index);
}

async function main() {
    var get = await get_yell("last");
    for (var index = get["yell_id"]; index > 0; index--) {
        add_card(index);
    }
}

main();
