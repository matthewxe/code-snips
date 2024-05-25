import { add_card_byid } from "./discover.js";

const query = document.getElementById("searchup").dataset["query"];
const next = document.getElementById("next");
const socket = new WebSocket("ws://" + location.host + "/yell/search/" + query);

socket.addEventListener("message", (ev) => {
	// var data = ev.data;
	// console.log(typeof data);
	// console.log(data);
	add_card_byid(ev.data);
});

async function handle_websocket_infinite_scroll(response) {
	window.removeEventListener("scroll", handle_websocket_infinite_scroll);
	const offset = 100;
	const endOfPage =
		window.innerHeight + window.scrollY >= document.body.offsetHeight - offset;

	console.log(endOfPage);
	if (endOfPage) {
		socket.send("next");
		await new Promise((r) => setTimeout(r, 500));
	}
	window.addEventListener("scroll", handle_websocket_infinite_scroll);
}
window.addEventListener("scroll", handle_websocket_infinite_scroll);
