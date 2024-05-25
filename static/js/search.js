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

const handleInfiniteScroll = () => {
    const endOfPage =
        window.innerHeight + window.scrollY >= document.body.offsetHeight - 300;
    console.log(
        window.innerHeight,
        window.scrollY,
        window.innerHeight + window.scrollY,
        document.body.offsetHeight,
        endOfPage,
    );

    if (endOfPage) {
        console.log("yuh");
        var what = socket.send("next");
        console.log(what);
    }
};
window.addEventListener("scroll", handleInfiniteScroll);

// next.addEventListener("click", () => {
//     socket.send("next");
// });
