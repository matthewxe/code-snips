import { add_card_byid } from "./discover.js";

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

const query = document.getElementById("searchup").dataset["query"];
// const next = document.getElementById("next");
const socket = new WebSocket(
	"ws://" + location.host + "/api/yell/search/" + query,
);

socket.addEventListener("message", (ev) => {
	// console.log(ev.data);
	if (ev.data == "404") {
		stop_spinner();
		socket.removeEventListener("message", self);
		return "shitass";
	}
	// console.log(ev.data);
	add_card_byid(ev.data);
});

async function handle_websocket_infinite_scroll() {
	window.removeEventListener("scroll", handle_websocket_infinite_scroll);
	const offset = 100;
	const endOfPage =
		window.innerHeight + window.scrollY >= document.body.offsetHeight - offset;

	// console.log(endOfPage);
	if (endOfPage) {
		socket.send("next");
		await new Promise((r) => setTimeout(r, 500));
	}
	window.addEventListener("scroll", handle_websocket_infinite_scroll);
}
window.addEventListener("scroll", handle_websocket_infinite_scroll);
